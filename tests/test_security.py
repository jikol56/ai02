import unittest
import os
from src.core.security import SecurityManager

class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.security_manager = SecurityManager()

    def test_is_admin(self):
        """관리자 권한 확인 테스트"""
        is_admin = self.security_manager.is_admin
        self.assertIsInstance(is_admin, bool)

    def test_get_current_user(self):
        """현재 사용자 확인 테스트"""
        username = self.security_manager.get_current_user()
        self.assertIsNotNone(username)
        self.assertIsInstance(username, str)

    def test_get_current_user_sid(self):
        """현재 사용자 SID 확인 테스트"""
        sid = self.security_manager.get_current_user_sid()
        if sid:  # SID를 가져올 수 있는 경우에만 테스트
            self.assertIsInstance(sid, str)
            self.assertTrue(sid.startswith('S-'))

    def test_check_required_privileges(self):
        """필요한 권한 확인 테스트"""
        result = self.security_manager.check_required_privileges()
        self.assertIsInstance(result, bool)

if __name__ == '__main__':
    unittest.main() 