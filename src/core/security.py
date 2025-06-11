import ctypes
import sys
import os
import logging
from typing import Optional, List, Dict
import win32security
import win32api
import win32con
import win32process
import win32ts
import win32event
import win32service
import win32serviceutil
import winerror
import hashlib
import json
from datetime import datetime
import psutil
from .logger import measure_time
import time

class SecurityManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_policy = self._load_security_policy()
        self.audit_log = []
        self.is_admin = self._is_admin()
        self._process_cache = None
        self._process_cache_time = 0
        self._process_cache_ttl = 1  # 1초 캐시

    def _is_admin(self) -> bool:
        """현재 프로세스가 관리자 권한으로 실행 중인지 확인"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            self.logger.error(f"관리자 권한 확인 실패: {e}")
            return False

    def request_admin_privileges(self) -> bool:
        """관리자 권한으로 프로그램 재실행"""
        if self.is_admin:
            return True

        try:
            # 현재 스크립트의 절대 경로
            script = os.path.abspath(sys.argv[0])
            params = ' '.join(sys.argv[1:])

            # 관리자 권한으로 재실행
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                f'"{script}" {params}', 
                None, 
                1  # SW_NORMAL
            )
            
            if ret > 32:  # 성공
                self.logger.info("관리자 권한으로 재실행 요청됨")
                sys.exit(0)
            else:
                self.logger.error(f"관리자 권한 요청 실패: {ret}")
                return False
        except Exception as e:
            self.logger.error(f"관리자 권한 요청 중 오류 발생: {e}")
            return False

    @measure_time
    def check_required_privileges(self) -> bool:
        """필요한 권한을 확인합니다."""
        try:
            # 관리자 권한 확인
            if self.security_policy["require_admin"]:
                if not self._is_admin():
                    self.logger.warning("관리자 권한이 필요합니다.")
                    return False
                    
            # 원격 접근 차단 확인
            if self.security_policy["block_remote_access"]:
                if self._is_remote_session():
                    self.logger.warning("원격 세션에서의 접근이 차단되었습니다.")
                    return False
                    
            return True
        except Exception as e:
            self.logger.error(f"권한 확인 중 오류 발생: {str(e)}")
            return False

    def get_current_user(self) -> Optional[str]:
        """현재 실행 중인 사용자 이름 반환"""
        try:
            return os.getenv('USERNAME')
        except Exception as e:
            self.logger.error(f"사용자 이름 확인 실패: {e}")
            return None

    def get_current_user_sid(self) -> Optional[str]:
        """현재 사용자의 SID 반환"""
        try:
            import win32security
            import win32api
            import win32con

            # 현재 사용자의 토큰 가져오기
            token = win32security.OpenProcessToken(
                win32api.GetCurrentProcess(),
                win32con.TOKEN_QUERY
            )

            # SID 가져오기
            sid = win32security.GetTokenInformation(token, win32security.TokenUser)[0]
            return win32security.ConvertSidToStringSid(sid)
        except Exception as e:
            self.logger.error(f"SID 확인 실패: {e}")
            return None 

    @measure_time
    def _load_security_policy(self) -> Dict:
        """보안 정책을 로드합니다."""
        try:
            policy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'security_policy.json')
            if os.path.exists(policy_path):
                with open(policy_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self._create_default_policy()
        except Exception as e:
            self.logger.error(f"보안 정책 로드 실패: {str(e)}")
            return self._create_default_policy()
            
    def _create_default_policy(self) -> Dict:
        """기본 보안 정책을 생성합니다."""
        return {
            "require_admin": True,
            "block_remote_access": True,
            "audit_changes": True,
            "max_failed_attempts": 3,
            "session_timeout": 3600,  # 1시간
            "allowed_processes": [
                "EXCEL.EXE",
                "WINWORD.EXE",
                "POWERPNT.EXE"
            ],
            "blocked_registry_keys": [
                "HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\*\\Security\\VBAWarnings",
                "HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\*\\Security\\AccessVBOM"
            ]
        }
        
    def _is_remote_session(self) -> bool:
        """원격 세션 여부를 확인합니다."""
        try:
            return win32ts.WTSQuerySessionInformation(None, win32ts.WTS_CURRENT_SESSION, win32ts.WTSClientAddress) is not None
        except Exception as e:
            self.logger.error(f"원격 세션 확인 중 오류 발생: {str(e)}")
            return False
            
    @measure_time
    def audit_action(self, action: str, details: Dict) -> None:
        """보안 관련 작업을 감사합니다."""
        if not self.security_policy["audit_changes"]:
            return
            
        try:
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "details": details,
                "user": os.getenv("USERNAME"),
                "session_id": win32ts.WTSGetActiveConsoleSessionId()
            }
            
            self.audit_log.append(audit_entry)
            self._save_audit_log()
            
            self.logger.info(f"감사 로그 기록: {action}")
        except Exception as e:
            self.logger.error(f"감사 로그 기록 중 오류 발생: {str(e)}")
            
    def _save_audit_log(self) -> None:
        """감사 로그를 파일에 저장합니다."""
        try:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, 'audit.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                json.dump(self.audit_log[-1], f)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"감사 로그 저장 중 오류 발생: {str(e)}")
            
    @measure_time
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """감사 로그를 조회합니다."""
        try:
            return self.audit_log[-limit:]
        except Exception as e:
            self.logger.error(f"감사 로그 조회 중 오류 발생: {str(e)}")
            return []
            
    @measure_time
    def clear_audit_log(self) -> None:
        """감사 로그를 초기화합니다."""
        try:
            self.audit_log.clear()
            log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'audit.log')
            if os.path.exists(log_file):
                os.remove(log_file)
            self.logger.info("감사 로그가 초기화되었습니다.")
        except Exception as e:
            self.logger.error(f"감사 로그 초기화 중 오류 발생: {str(e)}")
            
    @measure_time
    def check_process_security(self, process_name: str) -> bool:
        """프로세스 보안 검증 (캐시 적용)"""
        try:
            process_name = process_name.upper()
            if process_name not in self.security_policy["allowed_processes"]:
                self.logger.warning(f"허용되지 않은 프로세스: {process_name}")
                return False
            now = time.time()
            if self._process_cache is None or now - self._process_cache_time > self._process_cache_ttl:
                self._process_cache = [proc.info['name'].upper() for proc in psutil.process_iter(['name']) if proc.info['name']]
                self._process_cache_time = now
            if process_name in self._process_cache:
                return True
            self.logger.warning(f"프로세스 무결성 검증 실패: {process_name}")
            return False
        except Exception as e:
            self.logger.error(f"프로세스 보안 검증 중 오류 발생: {str(e)}")
            return False
            
    def _verify_process_integrity(self, process_name: str) -> bool:
        """프로세스의 무결성을 검증합니다."""
        try:
            # 프로세스 경로 확인
            process_path = self._get_process_path(process_name)
            if not process_path:
                return False
                
            # 파일 해시 검증
            if not self._verify_file_hash(process_path):
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"프로세스 무결성 검증 중 오류 발생: {str(e)}")
            return False
            
    def _get_process_path(self, process_name: str) -> Optional[str]:
        """프로세스의 실행 경로를 가져옵니다."""
        try:
            for proc in win32process.EnumProcesses():
                try:
                    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, proc)
                    if handle:
                        path = win32process.GetModuleFileNameEx(handle, 0)
                        if os.path.basename(path).upper() == process_name.upper():
                            return path
                except:
                    continue
            return None
        except Exception as e:
            self.logger.error(f"프로세스 경로 조회 중 오류 발생: {str(e)}")
            return None
            
    def _verify_file_hash(self, file_path: str) -> bool:
        """파일의 해시를 검증합니다."""
        try:
            # 실제 구현에서는 신뢰할 수 있는 해시값과 비교해야 합니다
            # 여기서는 간단한 검증만 수행
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                
            # TODO: 신뢰할 수 있는 해시값과 비교
            return True
        except Exception as e:
            self.logger.error(f"파일 해시 검증 중 오류 발생: {str(e)}")
            return False
            
    @measure_time
    def check_registry_security(self, key_path: str) -> bool:
        """레지스트리 키의 보안 상태를 확인합니다."""
        try:
            # 차단된 레지스트리 키 확인
            for blocked_key in self.security_policy["blocked_registry_keys"]:
                if self._match_registry_pattern(key_path, blocked_key):
                    self.logger.warning(f"차단된 레지스트리 키 접근: {key_path}")
                    return False
                    
            return True
        except Exception as e:
            self.logger.error(f"레지스트리 보안 확인 중 오류 발생: {str(e)}")
            return False
            
    def _match_registry_pattern(self, key: str, pattern: str) -> bool:
        """레지스트리 키가 패턴과 일치하는지 확인"""
        try:
            # 와일드카드 패턴을 정규식 패턴으로 변환
            pattern = pattern.replace('\\', '\\\\')  # 백슬래시 이스케이프
            pattern = pattern.replace('.', '\\.')    # 점 이스케이프
            pattern = pattern.replace('*', '.*')     # 와일드카드 변환
            pattern = f'^{pattern}$'                 # 전체 문자열 매칭
            
            import re
            return bool(re.match(pattern, key))
        except Exception as e:
            self.logger.error(f"레지스트리 패턴 매칭 중 오류 발생: {str(e)}")
            return False 