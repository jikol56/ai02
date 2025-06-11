import unittest
import os
from src.core.registry import RegistryManager

class TestRegistryManager(unittest.TestCase):
    def setUp(self):
        self.registry_manager = RegistryManager()
        self.test_key = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\16.0\\Excel\\Security'
        self.test_values = {
            'VBAWarnings': 2,
            'AccessVBOM': 0
        }

    def test_backup_registry(self):
        """레지스트리 백업 기능 테스트"""
        result = self.registry_manager.backup_registry()
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.registry_manager.backup_path))

    def test_modify_registry(self):
        """레지스트리 수정 기능 테스트"""
        result = self.registry_manager.modify_registry()
        self.assertTrue(result)
        
        # 수정된 값 확인
        status = self.registry_manager.check_registry_status()
        self.assertTrue(status)

    def test_restore_registry(self):
        """레지스트리 복원 기능 테스트"""
        # 먼저 백업
        self.registry_manager.backup_registry()
        
        # 수정
        self.registry_manager.modify_registry()
        
        # 복원
        result = self.registry_manager.restore_registry()
        self.assertTrue(result)

    def test_check_registry_status(self):
        """레지스트리 상태 확인 기능 테스트"""
        # 수정 전 상태 확인
        initial_status = self.registry_manager.check_registry_status()
        
        # 수정
        self.registry_manager.modify_registry()
        
        # 수정 후 상태 확인
        modified_status = self.registry_manager.check_registry_status()
        
        self.assertNotEqual(initial_status, modified_status)

if __name__ == '__main__':
    unittest.main() 