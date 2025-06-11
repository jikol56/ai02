import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import time
from functools import wraps

# 로그 디렉토리 생성
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 기존 로깅 설정
logger = logging.getLogger("vba_blocker")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(log_dir, "vba_blocker.log"), encoding="utf-8")
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

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

def measure_time(func):
    """Measure function execution time and log to performance log"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        perf_logger.info(f"{func.__qualname__} execution time: {end - start:.4f} seconds")
        return result
    return wrapper

# 성능 측정용 로거
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)
perf_file_handler = logging.FileHandler(os.path.join(log_dir, "performance.log"), encoding="utf-8", mode="w")
perf_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
perf_file_handler.setFormatter(perf_formatter)
perf_logger.addHandler(perf_file_handler) 