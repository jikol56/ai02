import winreg
import logging
from typing import Optional, Tuple, Dict
import os
from datetime import datetime
import re

class RegistryManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # VBA 관련 레지스트리 키
        self.vba_keys = {
            'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Excel\\Security': {
                'VBAWarnings': 2,  # 2: 모든 매크로 비활성화
                'AccessVBOM': 0    # 0: VBA 프로젝트 액세스 비활성화
            },
            'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Word\\Security': {
                'VBAWarnings': 2,
                'AccessVBOM': 0
            },
            'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\PowerPoint\\Security': {
                'VBAWarnings': 2,
                'AccessVBOM': 0
            }
        }
        self.backup_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backup')
        os.makedirs(self.backup_path, exist_ok=True)

    def _get_hive_and_path(self, key_path: str) -> Tuple[int, str]:
        """
        레지스트리 키 경로에서 hive와 나머지 경로를 분리
        """
        hive_map = {
            'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
            'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
            'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
            'HKEY_USERS': winreg.HKEY_USERS
        }
        
        parts = key_path.split('\\', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid registry path: {key_path}")
            
        hive_name, path = parts
        if hive_name not in hive_map:
            raise ValueError(f"Unknown registry hive: {hive_name}")
            
        return hive_map[hive_name], path

    def _parse_reg_file(self, reg_file: str) -> Dict[str, Dict[str, int]]:
        """
        .reg 파일을 파싱하여 레지스트리 값 추출
        """
        registry_data = {}
        current_key = None
        
        with open(reg_file, 'r', encoding='utf-16') as f:
            for line in f:
                line = line.strip()
                
                # 키 경로 파싱
                if line.startswith('[') and line.endswith(']'):
                    current_key = line[1:-1]
                    registry_data[current_key] = {}
                    continue
                
                # 값 파싱
                if current_key and '=' in line:
                    try:
                        name, value = line.split('=', 1)
                        name = name.strip('"')
                        
                        # dword 값 파싱
                        if value.startswith('dword:'):
                            hex_value = value[6:]
                            registry_data[current_key][name] = int(hex_value, 16)
                    except ValueError as e:
                        self.logger.warning(f"Failed to parse line: {line}, Error: {str(e)}")
                        continue
        
        return registry_data

    def backup_registry(self) -> bool:
        """
        현재 레지스트리 설정을 백업
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_path, f'registry_backup_{timestamp}.reg')
            
            # Windows Registry Editor Version 5.00 헤더 추가
            with open(backup_file, 'w', encoding='utf-16') as f:
                f.write('Windows Registry Editor Version 5.00\n\n')
            
            for key_path in self.vba_keys.keys():
                hive, path = self._get_hive_and_path(key_path)
                with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                    for value_name, _ in self.vba_keys[key_path].items():
                        try:
                            value, _ = winreg.QueryValueEx(key, value_name)
                            with open(backup_file, 'a', encoding='utf-16') as f:
                                f.write(f'[{key_path}]\n')
                                f.write(f'"{value_name}"=dword:{value:08x}\n\n')
                        except WindowsError:
                            self.logger.warning(f"Value {value_name} not found in {key_path}")
            
            self.logger.info(f"Registry backup created: {backup_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to backup registry: {str(e)}")
            return False

    def modify_registry(self) -> bool:
        """
        VBA 관련 레지스트리 설정을 수정
        """
        try:
            for key_path, values in self.vba_keys.items():
                hive, path = self._get_hive_and_path(key_path)
                with winreg.OpenKey(hive, path, 0, winreg.KEY_WRITE) as key:
                    for value_name, value in values.items():
                        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)
                        self.logger.info(f"Modified {key_path}\\{value_name} to {value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to modify registry: {str(e)}")
            return False

    def restore_registry(self, backup_file: Optional[str] = None) -> bool:
        """
        백업된 레지스트리 설정을 복원
        """
        try:
            if backup_file is None:
                # 가장 최근 백업 파일 찾기
                backup_files = [f for f in os.listdir(self.backup_path) if f.startswith('registry_backup_')]
                if not backup_files:
                    raise FileNotFoundError("No backup files found")
                backup_file = os.path.join(self.backup_path, sorted(backup_files)[-1])

            # .reg 파일 파싱
            registry_data = self._parse_reg_file(backup_file)
            
            # 레지스트리 값 복원
            for key_path, values in registry_data.items():
                hive, path = self._get_hive_and_path(key_path)
                try:
                    with winreg.OpenKey(hive, path, 0, winreg.KEY_WRITE) as key:
                        for value_name, value in values.items():
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)
                            self.logger.info(f"Restored {key_path}\\{value_name} to {value}")
                except WindowsError as e:
                    self.logger.error(f"Failed to restore key {key_path}: {str(e)}")
                    continue

            self.logger.info(f"Registry restored from: {backup_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore registry: {str(e)}")
            return False

    def check_registry_status(self) -> bool:
        """
        현재 레지스트리 설정이 VBA 차단 상태인지 확인
        """
        try:
            for key_path, values in self.vba_keys.items():
                hive, path = self._get_hive_and_path(key_path)
                with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                    for value_name, expected_value in values.items():
                        try:
                            current_value, _ = winreg.QueryValueEx(key, value_name)
                            if current_value != expected_value:
                                return False
                        except WindowsError:
                            return False
            return True
        except Exception as e:
            self.logger.error(f"Failed to check registry status: {str(e)}")
            return False 