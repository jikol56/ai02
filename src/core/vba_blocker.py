import win32api
import win32con
import win32security
import psutil
import logging
from .registry import RegistryManager
from .process_monitor import ProcessMonitor
from .security import SecurityManager

class VBABlocker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.registry_manager = RegistryManager()
        self.process_monitor = ProcessMonitor()
        self.security_manager = SecurityManager()

    def block_vba_execution(self) -> bool:
        """VBA 실행 차단"""
        try:
            # 관리자 권한 확인
            if not self.security_manager.check_required_privileges():
                self.logger.error("관리자 권한이 필요합니다.")
                return False

            # 레지스트리 백업
            if not self.registry_manager.backup_registry():
                self.logger.error("레지스트리 백업 실패")
                return False

            # 레지스트리 수정
            if not self.registry_manager.modify_registry():
                self.logger.error("레지스트리 수정 실패")
                return False

            # 실행 중인 VBA 프로세스 종료
            self._kill_vba_processes()

            # 프로세스 모니터링 시작
            if not self.process_monitor.start_monitoring():
                self.logger.error("프로세스 모니터링 시작 실패")
                return False

            self.logger.info("VBA 실행이 차단되었습니다.")
            return True
        except Exception as e:
            self.logger.error(f"VBA 차단 실패: {e}")
            return False

    def _kill_vba_processes(self):
        """실행 중인 VBA 프로세스 종료"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].upper() in self.process_monitor.target_processes:
                    proc.terminate()
                    proc.wait(timeout=3)
                    self.logger.info(f"{proc.info['name']} 프로세스가 종료되었습니다.")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                self.logger.error(f"프로세스 종료 실패: {e}")

    def is_vba_blocked(self) -> bool:
        """VBA가 차단되었는지 확인"""
        try:
            # 관리자 권한 확인
            if not self.security_manager.is_admin:
                self.logger.warning("관리자 권한이 필요합니다.")
                return False

            # 레지스트리 상태 확인
            registry_blocked = self.registry_manager.check_registry_status()
            
            # 프로세스 모니터링 상태 확인
            monitoring_active = self.process_monitor.monitoring
            
            # 실행 중인 VBA 프로세스 확인
            running_processes = self.process_monitor.get_running_processes()
            no_running_processes = len(running_processes) == 0

            return registry_blocked and monitoring_active and no_running_processes
        except Exception as e:
            self.logger.error(f"VBA 차단 상태 확인 실패: {e}")
            return False

    def restore_vba(self) -> bool:
        """VBA 실행 복원"""
        try:
            # 관리자 권한 확인
            if not self.security_manager.check_required_privileges():
                self.logger.error("관리자 권한이 필요합니다.")
                return False

            # 프로세스 모니터링 중지
            if not self.process_monitor.stop_monitoring():
                self.logger.error("프로세스 모니터링 중지 실패")
                return False

            # 레지스트리 복원
            if not self.registry_manager.restore_registry():
                self.logger.error("레지스트리 복원 실패")
                return False

            self.logger.info("VBA 실행이 복원되었습니다.")
            return True
        except Exception as e:
            self.logger.error(f"VBA 복원 실패: {e}")
            return False 