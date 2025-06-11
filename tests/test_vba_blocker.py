import unittest
from src.core.vba_blocker import VBABlocker

class TestVBABlocker(unittest.TestCase):
    def setUp(self):
        self.vba_blocker = VBABlocker()

    def test_block_vba_execution(self):
        """VBA 차단 기능 테스트"""
        result = self.vba_blocker.block_vba_execution()
        self.assertTrue(result)
        
        # 차단 상태 확인
        is_blocked = self.vba_blocker.is_vba_blocked()
        self.assertTrue(is_blocked)

    def test_restore_vba(self):
        """VBA 복원 기능 테스트"""
        # 먼저 차단
        self.vba_blocker.block_vba_execution()
        
        # 복원
        result = self.vba_blocker.restore_vba()
        self.assertTrue(result)
        
        # 복원 상태 확인
        is_blocked = self.vba_blocker.is_vba_blocked()
        self.assertFalse(is_blocked)

    def test_is_vba_blocked(self):
        """VBA 차단 상태 확인 기능 테스트"""
        # 초기 상태 확인
        initial_status = self.vba_blocker.is_vba_blocked()
        
        # 차단
        self.vba_blocker.block_vba_execution()
        
        # 차단 후 상태 확인
        blocked_status = self.vba_blocker.is_vba_blocked()
        
        self.assertNotEqual(initial_status, blocked_status)

if __name__ == '__main__':
    unittest.main() 