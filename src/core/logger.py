import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import time
from functools import wraps

# 로그 디렉토리 생성
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 기본 포맷터 설정
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# 기본 로거 설정
logger = logging.getLogger('vba_blocker')
logger.setLevel(logging.INFO)

class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 파일 핸들러 설정
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f"{name}.log"),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

def setup_logging():
    """로깅 설정 초기화"""
    # vba_blocker 로거 설정
    vba_logger = logging.getLogger('vba_blocker')
    vba_logger.setLevel(logging.INFO)
    vba_file_handler = logging.FileHandler(
        os.path.join(log_dir, 'vba_blocker.log'),
        encoding='utf-8'
    )
    vba_file_handler.setFormatter(formatter)
    vba_logger.addHandler(vba_file_handler)
    
    # performance 로거 설정
    perf_logger = logging.getLogger('performance')
    perf_logger.setLevel(logging.INFO)
    perf_file_handler = logging.FileHandler(
        os.path.join(log_dir, 'performance.log'),
        encoding='utf-8',
        mode='w'
    )
    perf_file_handler.setFormatter(formatter)
    perf_logger.addHandler(perf_file_handler)

def measure_time(func):
    """함수 실행 시간을 측정하는 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger = logging.getLogger('performance')
        logger.info(f"{func.__name__} execution time: {execution_time:.4f} seconds")
        
        return result
    return wrapper

# 파일 핸들러 설정 (일별 로테이션)
daily_file_handler = TimedRotatingFileHandler(
    filename=os.path.join(log_dir, 'vba_blocker.log'),
    when='midnight',
    interval=1,
    backupCount=30,
    encoding='utf-8'
)
daily_file_handler.setLevel(logging.INFO)
daily_file_handler.setFormatter(formatter)
logger.addHandler(daily_file_handler)

# 디버그 로그 파일 핸들러 (크기 기반 로테이션)
debug_file_handler = RotatingFileHandler(
    filename=os.path.join(log_dir, 'debug.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
debug_file_handler.setLevel(logging.DEBUG)
debug_file_handler.setFormatter(formatter)
logger.addHandler(debug_file_handler)

# 시스템 변경 사항 로그 파일 핸들러
changes_file_handler = RotatingFileHandler(
    filename=os.path.join(log_dir, 'system_changes.log'),
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3,
    encoding='utf-8'
)
changes_file_handler.setLevel(logging.INFO)
changes_file_handler.setFormatter(formatter)
logger.addHandler(changes_file_handler) 