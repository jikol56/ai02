import win32api
import win32con
import win32security
import psutil
import logging
from typing import List

class VBABlocker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.blocked_processes = ['vba', 'vbe', 'vbscript']

    def block_vba_execution(self) -> bool:
        """
        VBA 실행을 차단하는 메인 함수
        """
        try:
            # 레지스트리 설정 변경
            self._modify_registry()
            # 실행 중인 VBA 프로세스 종료
            self._kill_vba_processes()
            return True
        except Exception as e:
            self.logger.error(f"VBA 차단 중 오류 발생: {str(e)}")
            return False

    def _modify_registry(self):
        """
        Windows 레지스트리를 수정하여 VBA 실행을 차단
        """
        # TODO: 레지스트리 수정 로직 구현
        pass

    def _kill_vba_processes(self):
        """
        실행 중인 VBA 관련 프로세스를 종료
        """
        for proc in psutil.process_iter(['name']):
            try:
                if any(blocked in proc.info['name'].lower() for blocked in self.blocked_processes):
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def is_vba_blocked(self) -> bool:
        """
        VBA가 차단되어 있는지 확인
        """
        # TODO: VBA 차단 상태 확인 로직 구현
        return False 