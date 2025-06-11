import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class Logger:
    def __init__(self, name="vba_blocker"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 로그 디렉토리 생성
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 기본 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러 설정 (일별 로테이션)
        daily_file_handler = TimedRotatingFileHandler(
            filename=os.path.join(self.log_dir, 'vba_blocker.log'),
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        daily_file_handler.setLevel(logging.INFO)
        daily_file_handler.setFormatter(formatter)
        self.logger.addHandler(daily_file_handler)
        
        # 디버그 로그 파일 핸들러 (크기 기반 로테이션)
        debug_file_handler = RotatingFileHandler(
            filename=os.path.join(self.log_dir, 'debug.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(formatter)
        self.logger.addHandler(debug_file_handler)
        
        # 시스템 변경 사항 로그 파일 핸들러
        changes_file_handler = RotatingFileHandler(
            filename=os.path.join(self.log_dir, 'system_changes.log'),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        changes_file_handler.setLevel(logging.INFO)
        changes_file_handler.setFormatter(formatter)
        self.logger.addHandler(changes_file_handler)
        
    def debug(self, message):
        self.logger.debug(message)
        
    def info(self, message):
        self.logger.info(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def critical(self, message):
        self.logger.critical(message)
        
    def log_system_change(self, change_type, description):
        """시스템 변경 사항을 특별한 형식으로 로깅"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"시스템 변경 - {change_type}: {description}"
        self.info(message)
        
    def get_recent_logs(self, log_type='all', lines=100):
        """최근 로그 내용을 반환"""
        log_file = os.path.join(self.log_dir, f'{log_type}.log')
        if not os.path.exists(log_file):
            return []
            
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                return f.readlines()[-lines:]
        except Exception as e:
            self.error(f"로그 파일 읽기 실패: {str(e)}")
            return []
            
    def clear_logs(self, log_type='all'):
        """로그 파일 초기화"""
        if log_type == 'all':
            for handler in self.logger.handlers:
                if isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
                    try:
                        with open(handler.baseFilename, 'w', encoding='utf-8') as f:
                            f.write('')
                    except Exception as e:
                        self.error(f"로그 파일 초기화 실패: {str(e)}")
        else:
            log_file = os.path.join(self.log_dir, f'{log_type}.log')
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write('')
                except Exception as e:
                    self.error(f"로그 파일 초기화 실패: {str(e)}") 