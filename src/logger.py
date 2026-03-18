"""日志模块"""
import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

from .config import config


class Logger:
    """日志管理类"""

    _instance = None
    _loggers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._setup_loggers()

    def _setup_loggers(self):
        """设置日志记录器"""
        log_dir = Path(config.base_dir) / 'data' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        # 根日志配置
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'

        # 创建不同的日志记录器
        loggers_config = {
            'root': {
                'level': logging.INFO,
                'file': 'app.log',
                'console': True
            },
            'crawler': {
                'level': logging.INFO,
                'file': 'crawler.log',
                'console': False
            },
            'processor': {
                'level': logging.INFO,
                'file': 'processor.log',
                'console': False
            },
            'publisher': {
                'level': logging.INFO,
                'file': 'publisher.log',
                'console': False
            },
            'scheduler': {
                'level': logging.INFO,
                'file': 'scheduler.log',
                'console': False
            },
        }

        for name, cfg in loggers_config.items():
            logger = logging.getLogger(name)
            logger.setLevel(cfg['level'])
            logger.propagate = False

            # 清除已有的 handlers
            logger.handlers.clear()

            # 文件 handler - 按天轮转
            if cfg.get('file'):
                file_path = log_dir / cfg['file']
                file_handler = TimedRotatingFileHandler(
                    file_path,
                    when='midnight',
                    interval=1,
                    backupCount=30,
                    encoding='utf-8'
                )
                file_handler.setLevel(cfg['level'])
                file_handler.setFormatter(
                    logging.Formatter(log_format, date_format)
                )
                logger.addHandler(file_handler)

            # 控制台 handler
            if cfg.get('console'):
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(cfg['level'])
                console_handler.setFormatter(
                    logging.Formatter(log_format, date_format)
                )
                logger.addHandler(console_handler)

            self._loggers[name] = logger

    def get_logger(self, name: str = 'root') -> logging.Logger:
        """获取日志记录器"""
        return self._loggers.get(name, logging.getLogger(name))


# 全局日志实例
logger = Logger()
log = logger.get_logger('root')
crawler_log = logger.get_logger('crawler')
processor_log = logger.get_logger('processor')
publisher_log = logger.get_logger('publisher')
scheduler_log = logger.get_logger('scheduler')
