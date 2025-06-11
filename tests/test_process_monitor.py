import unittest
import time
from src.core.process_monitor import ProcessMonitor

class TestProcessMonitor(unittest.TestCase):
    def setUp(self):
        self.process_monitor = ProcessMonitor()

    def test_start_stop_monitoring(self):
        """모니터링 시작/중지 기능 테스트"""
        # 모니터링 시작
        result = self.process_monitor.start_monitoring()
        self.assertTrue(result)
        self.assertTrue(self.process_monitor.monitoring)

        # 이미 실행 중인 경우
        result = self.process_monitor.start_monitoring()
        self.assertFalse(result)

        # 모니터링 중지
        result = self.process_monitor.stop_monitoring()
        self.assertTrue(result)
        self.assertFalse(self.process_monitor.monitoring)

        # 이미 중지된 경우
        result = self.process_monitor.stop_monitoring()
        self.assertFalse(result)

    def test_get_running_processes(self):
        """실행 중인 프로세스 목록 조회 테스트"""
        processes = self.process_monitor.get_running_processes()
        self.assertIsInstance(processes, list)
        
        for process in processes:
            self.assertIn('name', process)
            self.assertIn('pid', process)
            self.assertIn('start_time', process)

    def test_is_process_running(self):
        """프로세스 실행 상태 확인 테스트"""
        # 존재하지 않는 프로세스
        result = self.process_monitor.is_process_running('NONEXISTENT.EXE')
        self.assertFalse(result)

        # 존재하는 프로세스 (실제 실행 여부는 환경에 따라 다름)
        result = self.process_monitor.is_process_running('EXCEL.EXE')
        self.assertIsInstance(result, bool)

if __name__ == '__main__':
    unittest.main() 