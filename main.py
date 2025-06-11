import sys
import os
import ctypes
import winreg
from src.gui.main_window import MainWindow
from src.core.logger import logger
from src.core.vba_blocker import VBABlocker

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_to_startup():
    """현재 실행 파일을 윈도우 시작프로그램에 등록"""
    exe_path = os.path.abspath(sys.argv[0])
    reg_key = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    app_name = "VBACodeBlocker"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
        logger.info(f"[자동실행] 시작프로그램에 등록됨: {exe_path}")
        return True
    except Exception as e:
        logger.error(f"[자동실행] 시작프로그램 등록 실패: {e}")
        return False

def main():
    if not is_admin():
        print("이 프로그램은 관리자 권한으로 실행해야 합니다.")
        print("프로그램을 종료합니다.")
        sys.exit(1)

    # EXE로 실행된 경우만 시작프로그램 등록 시도
    if getattr(sys, 'frozen', False):
        add_to_startup()

    # 관리자 권한이 있으면 자동으로 VBA 차단
    try:
        blocker = VBABlocker()
        result = blocker.block_vba_execution()
        if result:
            print("VBA가 자동으로 차단되었습니다.")
            logger.info("VBA가 자동으로 차단되었습니다.")
        else:
            print("자동 차단 실패. GUI에서 수동 차단을 시도하세요.")
            logger.warning("자동 차단 실패. GUI에서 수동 차단을 시도하세요.")
    except Exception as e:
        print(f"자동 차단 중 오류: {e}")
        logger.error(f"자동 차단 중 오류: {e}")

    # GUI 실행
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main() 