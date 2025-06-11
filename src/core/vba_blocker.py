import win32api
import win32con
import win32security
import psutil
import logging
from .registry import RegistryManager
from .process_monitor import ProcessMonitor
from .security import SecurityManager
from .change_tracker import ChangeTracker
from .logger import Logger, measure_time

class VBABlocker:
    def __init__(self):
        self.registry_manager = RegistryManager()
        self.process_monitor = ProcessMonitor()
        self.security_manager = SecurityManager()
        self.change_tracker = ChangeTracker()
        self.logger = Logger()

    @measure_time
    def block_vba_execution(self) -> bool:
        """VBA 실행을 차단합니다."""
        try:
            self.logger.info("VBA 차단 시작")
            
            # 관리자 권한 확인
            if not self.security_manager.check_required_privileges():
                self.logger.error("관리자 권한이 필요합니다.")
                return False

            # 변경 사항 추적 시작
            if not self.change_tracker.start_tracking():
                self.logger.error("변경 사항 추적 시작 실패")
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
            if not self._kill_vba_processes():
                self.logger.error("VBA 프로세스 종료 실패")
                return False

            # 프로세스 모니터링 시작
            if not self.process_monitor.start_monitoring():
                self.logger.error("프로세스 모니터링 시작 실패")
                return False

            self.logger.info("VBA 차단 완료")
            return True
        except Exception as e:
            self.logger.error(f"VBA 차단 중 오류 발생: {str(e)}")
            return False

    def _kill_vba_processes(self):
        """실행 중인 VBA 프로세스를 종료합니다."""
        try:
            killed = False
            for proc in self._get_vba_processes():
                try:
                    proc.kill()
                    self.logger.info(f"프로세스 종료: {proc.name()} (PID: {proc.pid})")
                    killed = True
                except Exception as e:
                    self.logger.error(f"프로세스 종료 실패: {proc.name()} (PID: {proc.pid}) - {str(e)}")
            return killed
        except Exception as e:
            self.logger.error(f"VBA 프로세스 종료 중 오류 발생: {str(e)}")
            return False

    def _get_vba_processes(self):
        """VBA 관련 프로세스 목록을 반환합니다."""
        target_processes = ['EXCEL.EXE', 'WINWORD.EXE', 'POWERPNT.EXE']
        return [p for p in psutil.process_iter(['name']) 
                if p.info['name'] in target_processes]

    @measure_time
    def is_vba_blocked(self) -> bool:
        """VBA 차단 상태를 확인합니다."""
        try:
            # 관리자 권한 확인
            if not self.security_manager.is_admin:
                self.logger.warning("관리자 권한이 필요합니다.")
                return False

            # 레지스트리 상태 확인
            registry_status = self.registry_manager.check_registry_status()
            
            # 프로세스 모니터링 상태 확인
            monitoring_active = self.process_monitor.monitoring
            
            # 실행 중인 VBA 프로세스 확인
            running_processes = self.process_monitor.get_running_processes()
            no_running_processes = len(running_processes) == 0

            is_blocked = registry_status and monitoring_active and no_running_processes
            self.logger.debug(f"VBA 차단 상태: {is_blocked}")
            return is_blocked
        except Exception as e:
            self.logger.error(f"VBA 차단 상태 확인 중 오류 발생: {str(e)}")
            return False

    @measure_time
    def restore_vba(self) -> bool:
        """VBA 실행을 복원합니다."""
        try:
            self.logger.info("VBA 복원 시작")
            
            # 관리자 권한 확인
            if not self.security_manager.check_required_privileges():
                self.logger.error("관리자 권한이 필요합니다.")
                return False

            # 프로세스 모니터링 중지
            if not self.process_monitor.stop_monitoring():
                self.logger.error("프로세스 모니터링 중지 실패")
                return False

            # 변경 사항 추적 중지
            if not self.change_tracker.stop_tracking():
                self.logger.error("변경 사항 추적 중지 실패")
                return False

            # 레지스트리 복원
            if not self.registry_manager.restore_registry():
                self.logger.error("레지스트리 복원 실패")
                return False

            self.logger.info("VBA 복원 완료")
            return True
        except Exception as e:
            self.logger.error(f"VBA 복원 중 오류 발생: {str(e)}")
            return False

    @measure_time
    def get_system_changes(self) -> list:
        """시스템 변경 사항을 반환합니다."""
        try:
            changes = self.change_tracker.get_changes()
            self.logger.debug(f"시스템 변경 사항 조회: {len(changes)}개")
            return changes
        except Exception as e:
            self.logger.error(f"시스템 변경 사항 조회 중 오류 발생: {str(e)}")
            return []

    @measure_time
    def clear_system_changes(self) -> bool:
        """시스템 변경 사항을 초기화합니다."""
        try:
            self.change_tracker.clear_changes()
            self.logger.info("시스템 변경 사항 초기화 완료")
            return True
        except Exception as e:
            self.logger.error(f"시스템 변경 사항 초기화 중 오류 발생: {str(e)}")
            return False 