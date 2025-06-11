import unittest
import os
import time
from src.core.change_tracker import ChangeTracker

class TestChangeTracker(unittest.TestCase):
    def setUp(self):
        self.change_tracker = ChangeTracker()
        self.log_file = self.change_tracker.log_file

    def tearDown(self):
        # 테스트 후 로그 파일 정리
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_start_stop_tracking(self):
        """추적 시작/중지 기능 테스트"""
        # 추적 시작
        result = self.change_tracker.start_tracking()
        self.assertTrue(result)
        self.assertTrue(self.change_tracker.tracking)

        # 이미 실행 중인 경우
        result = self.change_tracker.start_tracking()
        self.assertFalse(result)

        # 추적 중지
        result = self.change_tracker.stop_tracking()
        self.assertTrue(result)
        self.assertFalse(self.change_tracker.tracking)

        # 이미 중지된 경우
        result = self.change_tracker.stop_tracking()
        self.assertFalse(result)

    def test_get_changes(self):
        """변경 사항 조회 테스트"""
        # 추적 시작
        self.change_tracker.start_tracking()
        time.sleep(2)  # 변경 사항 수집을 위한 대기
        self.change_tracker.stop_tracking()

        # 변경 사항 조회
        changes = self.change_tracker.get_changes()
        self.assertIsInstance(changes, list)

    def test_clear_changes(self):
        """변경 사항 초기화 테스트"""
        # 추적 시작
        self.change_tracker.start_tracking()
        time.sleep(2)  # 변경 사항 수집을 위한 대기
        self.change_tracker.stop_tracking()

        # 변경 사항 초기화
        result = self.change_tracker.clear_changes()
        self.assertTrue(result)
        self.assertEqual(len(self.change_tracker.get_changes()), 0)

if __name__ == '__main__':
    unittest.main() 