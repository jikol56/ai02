import ctypes
import sys
import os
import logging
from typing import Optional

class SecurityManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_admin = self._is_admin()

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

    def check_required_privileges(self) -> bool:
        """필요한 권한이 있는지 확인"""
        if not self.is_admin:
            self.logger.warning("관리자 권한이 필요합니다.")
            return self.request_admin_privileges()
        return True

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