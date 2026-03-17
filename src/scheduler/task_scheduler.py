"""
定时任务调度器
"""
import schedule
import time
from datetime import datetime
import logging
from typing import Dict, List, Callable
import threading
import queue

logger = logging.getLogger(__name__)


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.tasks: Dict[str, dict] = {}
        self.running = False
        self.thread = None
        self.task_queue = queue.Queue()
    
    def add_task(self, name: str, func: Callable, interval: str, **kwargs):
        """
        添加定时任务
        
        Args:
            name: 任务名称
            func: 任务函数
            interval: 间隔表达式 (如 "every().hour", "every(30).minutes")
        """
        self.tasks[name] = {
            'func': func,
            'interval': interval,
            'kwargs': kwargs,
            'last_run': None,
            'next_run': None
        }
        logger.info(f"Added task: {name} ({interval})")
    
    def add_rss_fetch_task(self, name: str, feed_urls: List[str], interval_minutes: int = 60):
        """添加 RSS 抓取任务"""
        def task():
            from .scraper import RSSScraper
            scraper = RSSScraper()
            articles = scraper.fetch_multiple(feed_urls)
            logger.info(f"Fetched {len(articles)} articles from {feed_urls}")
            return articles
        
        self.add_task(name, task, f"every({interval_minutes}).minutes")
    
    def add_http_fetch_task(self, name: str, urls: List[str], interval_minutes: int = 60):
        """添加 HTTP 抓取任务"""
        def task():
            from .scraper import WebScraper
            scraper = WebScraper()
            articles = []
            for url in urls:
                article = scraper.extract_article(url)
                if article.get('content'):
                    articles.append(article)
            logger.info(f"Fetched {len(articles)} articles from {urls}")
            return articles
        
        self.add_task(name, task, f"every({interval_minutes}).minutes")
    
    def run_pending(self):
        """执行所有待运行的任务"""
        schedule.run_pending()
    
    def run_all(self):
        """立即运行所有任务一次"""
        logger.info("Running all tasks manually...")
        for name, task_info in self.tasks.items():
            try:
                logger.info(f"Executing task: {name}")
                result = task_info['func']()
                task_info['last_run'] = datetime.now()
                logger.info(f"Task {name} completed, result: {result}")
            except Exception as e:
                logger.error(f"Task {name} failed: {e}")
    
    def start(self, blocking: bool = True):
        """
        启动调度器
        
        Args:
            blocking: 是否阻塞主线程
        """
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        # 注册所有任务到 schedule
        for name, task_info in self.tasks.items():
            interval = task_info['interval']
            func = task_info['func']
            
            # 解析间隔并注册
            if 'every()' in interval:
                schedule.every().hour.do(func)
            elif 'minutes' in interval:
                import re
                match = re.search(r'(\d+)', interval)
                if match:
                    minutes = int(match.group(1))
                    schedule.every(minutes).minutes.do(func)
            elif 'hours' in interval:
                import re
                match = re.search(r'(\d+)', interval)
                if match:
                    hours = int(match.group(1))
                    schedule.every(hours).hours.do(func)
            elif 'day' in interval:
                schedule.every().day.do(func)
        
        self.running = True
        logger.info(f"Scheduler started with {len(self.tasks)} tasks")
        
        if blocking:
            try:
                while self.running:
                    self.run_pending()
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self):
        """停止调度器"""
        self.running = False
        schedule.clear()
        logger.info("Scheduler stopped")
    
    def get_status(self) -> Dict:
        """获取调度器状态"""
        return {
            'running': self.running,
            'task_count': len(self.tasks),
            'tasks': [
                {
                    'name': name,
                    'interval': info['interval'],
                    'last_run': info['last_run'].isoformat() if info['last_run'] else None
                }
                for name, info in self.tasks.items()
            ]
        }


if __name__ == '__main__':
    # 测试
    scheduler = TaskScheduler()
    
    def test_task():
        print(f"Task ran at {datetime.now()}")
    
    scheduler.add_task('test', test_task, "every(1).minutes")
    scheduler.run_all()
