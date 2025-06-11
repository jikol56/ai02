import sys
import logging
from gui.main_window import main

if __name__ == '__main__':
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('vba_blocker.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # GUI 실행
    main() 