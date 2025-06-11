import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from threading import Thread, Event
import winreg
import psutil
from .logger import measure_time

class ChangeTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.changes: List[Dict] = []
        self.tracking = False
        self.stop_event = Event()
        self.track_thread: Optional[Thread] = None
        
        # 로그 파일 경로 설정
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, 'system_changes.json')

    @measure_time
    def start_tracking(self) -> bool:
        """변경 사항 추적 시작"""
        if self.tracking:
            self.logger.warning("이미 추적이 실행 중입니다.")
            return False

        try:
            self.stop_event.clear()
            self.track_thread = Thread(target=self._track_changes)
            self.track_thread.daemon = True
            self.track_thread.start()
            self.tracking = True
            self.logger.info("시스템 변경 사항 추적이 시작되었습니다.")
            return True
        except Exception as e:
            self.logger.error(f"추적 시작 실패: {e}")
            return False

    @measure_time
    def stop_tracking(self) -> bool:
        """변경 사항 추적 중지"""
        if not self.tracking:
            self.logger.warning("추적이 실행 중이 아닙니다.")
            return False

        try:
            self.stop_event.set()
            if self.track_thread:
                self.track_thread.join(timeout=5.0)
            self.tracking = False
            self._save_changes()
            self.logger.info("시스템 변경 사항 추적이 중지되었습니다.")
            return True
        except Exception as e:
            self.logger.error(f"추적 중지 실패: {e}")
            return False

    def _track_changes(self):
        """변경 사항 추적 메인 루프"""
        while not self.stop_event.is_set():
            try:
                self._check_registry_changes()
                self._check_process_changes()
            except Exception as e:
                self.logger.error(f"변경 사항 추적 중 오류 발생: {e}")

    def _check_registry_changes(self):
        """레지스트리 변경 사항 확인"""
        try:
            # VBA 관련 레지스트리 키 모니터링
            vba_keys = [
                r'Software\Microsoft\Office\16.0\Excel\Security',
                r'Software\Microsoft\Office\16.0\Word\Security',
                r'Software\Microsoft\Office\16.0\PowerPoint\Security'
            ]

            for key_path in vba_keys:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                        try:
                            value, _ = winreg.QueryValueEx(key, 'VBAWarnings')
                            self._add_change('registry', {
                                'key': key_path,
                                'value': 'VBAWarnings',
                                'data': value,
                                'timestamp': datetime.now().isoformat()
                            })
                        except WindowsError:
                            pass
                except WindowsError:
                    continue
        except Exception as e:
            self.logger.error(f"레지스트리 변경 확인 실패: {e}")

    def _check_process_changes(self):
        """프로세스 변경 사항 확인"""
        try:
            target_processes = ['EXCEL.EXE', 'WINWORD.EXE', 'POWERPNT.EXE']
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    if proc.info['name'].upper() in target_processes:
                        self._add_change('process', {
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'start_time': datetime.fromtimestamp(proc.info['create_time']).isoformat(),
                            'timestamp': datetime.now().isoformat()
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            self.logger.error(f"프로세스 변경 확인 실패: {e}")

    def _add_change(self, change_type: str, data: Dict):
        """변경 사항 추가"""
        change = {
            'type': change_type,
            'data': data
        }
        self.changes.append(change)
        self._save_changes()

    def _save_changes(self):
        """변경 사항을 파일에 저장"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.changes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"변경 사항 저장 실패: {e}")

    @measure_time
    def get_changes(self) -> List[Dict]:
        """저장된 변경 사항 반환"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"변경 사항 로드 실패: {e}")
            return []

    @measure_time
    def clear_changes(self) -> bool:
        """변경 사항 기록 초기화"""
        try:
            self.changes = []
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
            self.logger.info("변경 사항 기록이 초기화되었습니다.")
            return True
        except Exception as e:
            self.logger.error(f"변경 사항 초기화 실패: {e}")
            return False 