import psutil
import logging
import time
from typing import List, Dict, Optional
from threading import Thread, Event
from .logger import Logger

class ProcessMonitor:
    def __init__(self):
        self.logger = Logger('process_monitor')
        self.target_processes = {
            'EXCEL.EXE': 'Microsoft Excel',
            'WINWORD.EXE': 'Microsoft Word',
            'POWERPNT.EXE': 'Microsoft PowerPoint',
            'MSACCESS.EXE': 'Microsoft Access',
            'OUTLOOK.EXE': 'Microsoft Outlook'
        }
        self.monitoring = False
        self.stop_event = Event()
        self.monitor_thread: Optional[Thread] = None

    def start_monitoring(self) -> bool:
        """프로세스 모니터링 시작"""
        if self.monitoring:
            self.logger.warning("이미 모니터링이 실행 중입니다.")
            return False

        try:
            self.stop_event.clear()
            self.monitor_thread = Thread(target=self._monitor_processes)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.monitoring = True
            self.logger.info("프로세스 모니터링이 시작되었습니다.")
            return True
        except Exception as e:
            self.logger.error(f"모니터링 시작 실패: {e}")
            return False

    def stop_monitoring(self) -> bool:
        """프로세스 모니터링 중지"""
        if not self.monitoring:
            self.logger.warning("모니터링이 실행 중이 아닙니다.")
            return False

        try:
            self.stop_event.set()
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5.0)
            self.monitoring = False
            self.logger.info("프로세스 모니터링이 중지되었습니다.")
            return True
        except Exception as e:
            self.logger.error(f"모니터링 중지 실패: {e}")
            return False

    def _monitor_processes(self):
        """프로세스 모니터링 메인 루프"""
        while not self.stop_event.is_set():
            try:
                self._check_and_terminate_processes()
                time.sleep(1)  # 1초 간격으로 체크
            except Exception as e:
                self.logger.error(f"모니터링 중 오류 발생: {e}")
                time.sleep(5)  # 오류 발생 시 5초 대기

    def _check_and_terminate_processes(self):
        """VBA 관련 프로세스 확인 및 종료"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].upper() in self.target_processes:
                    self._terminate_process(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    def _terminate_process(self, process: psutil.Process):
        """프로세스 종료"""
        try:
            process_name = process.info['name']
            process.terminate()
            process.wait(timeout=3)  # 3초 대기
            self.logger.info(f"{self.target_processes[process_name.upper()]} 프로세스가 종료되었습니다.")
        except psutil.TimeoutExpired:
            try:
                process.kill()  # 강제 종료
                self.logger.warning(f"{self.target_processes[process_name.upper()]} 프로세스가 강제 종료되었습니다.")
            except psutil.NoSuchProcess:
                pass
        except Exception as e:
            self.logger.error(f"프로세스 종료 실패: {e}")

    def get_running_processes(self) -> List[Dict[str, str]]:
        """현재 실행 중인 VBA 관련 프로세스 목록 반환"""
        running_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
            try:
                if proc.info['name'].upper() in self.target_processes:
                    running_processes.append({
                        'name': self.target_processes[proc.info['name'].upper()],
                        'pid': proc.info['pid'],
                        'start_time': time.strftime('%Y-%m-%d %H:%M:%S', 
                                                  time.localtime(proc.info['create_time']))
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return running_processes

    def is_process_running(self, process_name: str) -> bool:
        """특정 프로세스가 실행 중인지 확인"""
        process_name = process_name.upper()
        if process_name not in self.target_processes:
            return False

        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].upper() == process_name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False 