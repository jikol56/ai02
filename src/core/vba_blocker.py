import win32api
import win32con
import win32security
import psutil
import logging
from typing import List
from .registry import RegistryManager

class VBABlocker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.blocked_processes = ['vba', 'vbe', 'vbscript']
        self.registry_manager = RegistryManager()

    def block_vba_execution(self) -> bool:
        """
        VBA 실행을 차단하는 메인 함수
        """
        try:
            # 레지스트리 백업
            if not self.registry_manager.backup_registry():
                self.logger.error("Failed to backup registry")
                return False

            # 레지스트리 설정 변경
            if not self.registry_manager.modify_registry():
                self.logger.error("Failed to modify registry")
                return False

            # 실행 중인 VBA 프로세스 종료
            self._kill_vba_processes()
            return True
        except Exception as e:
            self.logger.error(f"VBA 차단 중 오류 발생: {str(e)}")
            return False

    def _kill_vba_processes(self):
        """
        실행 중인 VBA 관련 프로세스를 종료
        """
        for proc in psutil.process_iter(['name']):
            try:
                if any(blocked in proc.info['name'].lower() for blocked in self.blocked_processes):
                    proc.kill()
                    self.logger.info(f"Killed process: {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.logger.warning(f"Failed to kill process: {str(e)}")
                continue

    def is_vba_blocked(self) -> bool:
        """
        VBA가 차단되어 있는지 확인
        """
        # 레지스트리 설정 확인
        if not self.registry_manager.check_registry_status():
            return False

        # 실행 중인 VBA 프로세스 확인
        for proc in psutil.process_iter(['name']):
            try:
                if any(blocked in proc.info['name'].lower() for blocked in self.blocked_processes):
                    return False
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return True

    def restore_vba(self) -> bool:
        """
        VBA 차단을 해제하고 원래 설정으로 복원
        """
        try:
            return self.registry_manager.restore_registry()
        except Exception as e:
            self.logger.error(f"VBA 복원 중 오류 발생: {str(e)}")
            return False 