import unittest
import os
import json
import tempfile
from datetime import datetime
from src.core.security import SecurityManager

class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.security_manager = SecurityManager()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # 임시 파일 정리
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
        
    def test_security_policy_loading(self):
        """보안 정책 로드 테스트"""
        policy = self.security_manager._load_security_policy()
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, dict))
        self.assertIn('require_admin', policy)
        self.assertIn('block_remote_access', policy)
        self.assertIn('audit_changes', policy)
        
    def test_default_policy_creation(self):
        """기본 보안 정책 생성 테스트"""
        policy = self.security_manager._create_default_policy()
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, dict))
        self.assertTrue(policy['require_admin'])
        self.assertTrue(policy['block_remote_access'])
        self.assertTrue(policy['audit_changes'])
        
    def test_audit_logging(self):
        """감사 로깅 테스트"""
        # 감사 로그 기록
        self.security_manager.audit_action('test_action', {'test': 'data'})
        
        # 로그 확인
        logs = self.security_manager.get_audit_log()
        self.assertTrue(len(logs) > 0)
        self.assertEqual(logs[-1]['action'], 'test_action')
        self.assertEqual(logs[-1]['details'], {'test': 'data'})
        
    def test_audit_log_clearing(self):
        """감사 로그 초기화 테스트"""
        # 로그 기록
        self.security_manager.audit_action('test_action', {'test': 'data'})
        
        # 로그 초기화
        self.security_manager.clear_audit_log()
        
        # 로그 확인
        logs = self.security_manager.get_audit_log()
        self.assertEqual(len(logs), 0)
        
    def test_process_security(self):
        """프로세스 보안 테스트"""
        # 허용된 프로세스 테스트
        self.assertTrue(self.security_manager.check_process_security('EXCEL.EXE'))
        
        # 허용되지 않은 프로세스 테스트
        self.assertFalse(self.security_manager.check_process_security('NOTEPAD.EXE'))
        
    def test_registry_security(self):
        """레지스트리 보안 테스트"""
        # 허용된 레지스트리 키 테스트
        self.assertTrue(self.security_manager.check_registry_security(
            'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Excel\\Options'
        ))
        
        # 차단된 레지스트리 키 테스트
        self.assertFalse(self.security_manager.check_registry_security(
            'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Excel\\Security\\VBAWarnings'
        ))
        
    def test_remote_session_detection(self):
        """원격 세션 감지 테스트"""
        # 원격 세션 감지 기능 테스트
        is_remote = self.security_manager._is_remote_session()
        self.assertIsInstance(is_remote, bool)
        
    def test_required_privileges(self):
        """필요한 권한 확인 테스트"""
        # 권한 확인 기능 테스트
        has_privileges = self.security_manager.check_required_privileges()
        self.assertIsInstance(has_privileges, bool)
        
    def test_registry_pattern_matching(self):
        """레지스트리 패턴 매칭 테스트"""
        # 와일드카드 패턴 매칭 테스트
        pattern = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\*\\Security\\VBAWarnings'
        key = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Excel\\Security\\VBAWarnings'
        self.assertTrue(self.security_manager._match_registry_pattern(key, pattern))
        
        # 일치하지 않는 패턴 테스트
        key = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Excel\\Options'
        self.assertFalse(self.security_manager._match_registry_pattern(key, pattern))

if __name__ == '__main__':
    unittest.main() 