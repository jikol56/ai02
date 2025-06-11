import sys
import os
import ctypes
from src.gui.main_window import MainWindow

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    if not is_admin():
        print("이 프로그램은 관리자 권한으로 실행해야 합니다.")
        print("프로그램을 종료합니다.")
        sys.exit(1)
    
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main() 