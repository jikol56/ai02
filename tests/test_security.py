import unittest
import os
import json
import tempfile
from datetime import datetime
from src.core.security import SecurityManager
from src.core.logger import perf_logger

class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.security_manager = SecurityManager()
        self.temp_dir = tempfile.mkdtemp()
        perf_logger.info("Test started: TestSecurityManager")
        
    def tearDown(self):
        # Clean up temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
        perf_logger.info("Test finished: TestSecurityManager")
        
    def test_security_policy_loading(self):
        """Test security policy loading"""
        perf_logger.info("Running test: test_security_policy_loading")
        policy = self.security_manager._load_security_policy()
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, dict))
        self.assertIn('require_admin', policy)
        self.assertIn('block_remote_access', policy)
        self.assertIn('audit_changes', policy)
        
    def test_default_policy_creation(self):
        """Test default policy creation"""
        perf_logger.info("Running test: test_default_policy_creation")
        policy = self.security_manager._create_default_policy()
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, dict))
        self.assertTrue(policy['require_admin'])
        self.assertTrue(policy['block_remote_access'])
        self.assertTrue(policy['audit_changes'])
        
    def test_audit_logging(self):
        """Test audit logging"""
        perf_logger.info("Running test: test_audit_logging")
        # Log audit action
        self.security_manager.audit_action('test_action', {'test': 'data'})
        
        # Check logs
        logs = self.security_manager.get_audit_log()
        self.assertTrue(len(logs) > 0)
        self.assertEqual(logs[-1]['action'], 'test_action')
        self.assertEqual(logs[-1]['details'], {'test': 'data'})
        
    def test_audit_log_clearing(self):
        """Test audit log clearing"""
        perf_logger.info("Running test: test_audit_log_clearing")
        # Log action
        self.security_manager.audit_action('test_action', {'test': 'data'})
        
        # Clear logs
        self.security_manager.clear_audit_log()
        
        # Check logs
        logs = self.security_manager.get_audit_log()
        self.assertEqual(len(logs), 0)
        
    def test_process_security(self):
        """Test process security"""
        perf_logger.info("Running test: test_process_security")
        # Test allowed process
        self.assertTrue(self.security_manager.check_process_security('EXCEL.EXE'))
        
        # Test disallowed process
        self.assertFalse(self.security_manager.check_process_security('NOTEPAD.EXE'))
        
    def test_registry_security(self):
        """Test registry security"""
        perf_logger.info("Running test: test_registry_security")
        # Test allowed registry key
        self.assertTrue(self.security_manager.check_registry_security(
            'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Excel\\Options'
        ))
        
        # Test blocked registry key
        self.assertFalse(self.security_manager.check_registry_security(
            'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Excel\\Security\\VBAWarnings'
        ))
        
    def test_remote_session_detection(self):
        """Test remote session detection"""
        perf_logger.info("Running test: test_remote_session_detection")
        # Test remote session detection
        is_remote = self.security_manager._is_remote_session()
        self.assertIsInstance(is_remote, bool)
        
    def test_required_privileges(self):
        """Test required privileges"""
        perf_logger.info("Running test: test_required_privileges")
        # Test privilege check
        has_privileges = self.security_manager.check_required_privileges()
        self.assertIsInstance(has_privileges, bool)
        
    def test_registry_pattern_matching(self):
        """Test registry pattern matching"""
        perf_logger.info("Running test: test_registry_pattern_matching")
        # Test wildcard pattern matching
        pattern = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\*\\Security\\VBAWarnings'
        key = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Excel\\Security\\VBAWarnings'
        self.assertTrue(self.security_manager._match_registry_pattern(key, pattern))
        
        # Test non-matching pattern
        key = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Excel\\Options'
        self.assertFalse(self.security_manager._match_registry_pattern(key, pattern))

if __name__ == '__main__':
    unittest.main() 