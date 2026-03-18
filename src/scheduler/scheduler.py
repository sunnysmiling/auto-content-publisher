"""任务调度器"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

from ..config import config
from ..logger import scheduler_log
from ..scraper import Crawler
from ..processor import Processor
from ..publisher import Publisher


class TaskMonitor:
    """任务监控"""

    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir or (config.base_dir / 'data' / 'logs' / 'tasks'))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.stats_file = self.log_dir / 'stats.json'
        self._stats = self._load_stats()

    def _load_stats(self) -> Dict:
        """加载统计数据"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'crawl': {'success': 0, 'failed': 0, 'last_run': None},
            'process': {'success': 0, 'failed': 0, 'last_run': None},
            'publish': {'success': 0, 'failed': 0, 'last_run': None},
        }

    def _save_stats(self):
        """保存统计数据"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self._stats, f, indent=2)
        except Exception as e:
            scheduler_log.warning(f"保存统计失败: {e}")

    def record(self, task_type: str, success: bool, count: int = 0):
        """记录任务执行结果"""
        if task_type not in self._stats:
            self._stats[task_type] = {'success': 0, 'failed': 0, 'last_run': None}
        
        if success:
            self._stats[task_type]['success'] += count
        else:
            self._stats[task_type]['failed'] += 1
        
        self._stats[task_type]['last_run'] = datetime.now().isoformat()
        self._save_stats()

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self._stats

    def get_task_history(self, task_type: str = None, days: int = 7) -> List[Dict]:
        """获取任务历史"""
        # 简化实现，返回当前统计
        if task_type:
            return [self._stats.get(task_type, {})]
        return list(self._stats.values())


class TaskScheduler:
    """定时任务调度器"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.crawler = Crawler()
        self.processor = Processor()
        self.publisher = Publisher()
        self.monitor = TaskMonitor()

    def start(self):
        """启动调度器"""
        # 采集任务 - 按配置间隔
        crawl_interval = config.crawl_interval
        self.scheduler.add_job(
            self.run_crawl,
            trigger=IntervalTrigger(minutes=crawl_interval),
            id='crawl',
            name='采集任务',
            replace_existing=True
        )

        # 发布任务 - 按配置时间
        for time_str in config.publish_times:
            hour, minute = map(int, time_str.split(':'))
            self.scheduler.add_job(
                self.run_publish,
                trigger=CronTrigger(hour=hour, minute=minute),
                id=f'publish_{time_str}',
                name=f'发布任务 {time_str}',
                replace_existing=True
            )

        # 处理任务 - 每小时一次
        self.scheduler.add_job(
            self.run_process,
            trigger=IntervalTrigger(hours=1),
            id='process',
            name='AI处理任务',
            replace_existing=True
        )

        # 重试失败任务 - 每2小时一次
        self.scheduler.add_job(
            self.run_retry,
            trigger=IntervalTrigger(hours=2),
            id='retry',
            name='失败重试任务',
            replace_existing=True
        )

        # 清理缓存 - 每天凌晨
        self.scheduler.add_job(
            self.run_cleanup,
            trigger=CronTrigger(hour=3, minute=0),
            id='cleanup',
            name='缓存清理任务',
            replace_existing=True
        )

        self.scheduler.start()
        scheduler_log.info("调度器启动成功")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        scheduler_log.info("调度器已停止")

    def run_crawl(self):
        """执行采集任务"""
        scheduler_log.info("开始采集任务")
        try:
            count = self.crawler.crawl_all()
            self.monitor.record('crawl', True, count)
            scheduler_log.info(f"采集完成，新增 {count} 篇")
        except Exception as e:
            self.monitor.record('crawl', False)
            scheduler_log.error(f"采集任务异常: {e}")

    def run_process(self):
        """执行处理任务"""
        scheduler_log.info("开始处理任务")
        try:
            count = self.processor.process_pending(limit=20)
            self.monitor.record('process', True, count)
            scheduler_log.info(f"处理完成，成功 {count} 篇")
        except Exception as e:
            self.monitor.record('process', False)
            scheduler_log.error(f"处理任务异常: {e}")

    def run_publish(self):
        """执行发布任务"""
        scheduler_log.info("开始发布任务")
        try:
            count = self.publisher.publish_pending(limit=10)
            self.monitor.record('publish', True, count)
            scheduler_log.info(f"发布完成，成功 {count} 篇")
        except Exception as e:
            self.monitor.record('publish', False)
            scheduler_log.error(f"发布任务异常: {e}")

    def run_retry(self):
        """执行失败重试任务"""
        scheduler_log.info("开始失败重试任务")
        try:
            # 重试处理失败的文章
            count = self.processor.retry_failed(limit=10)
            scheduler_log.info(f"重试处理完成，成功 {count} 篇")
            
            # TODO: 可添加发布失败重试
        except Exception as e:
            scheduler_log.error(f"重试任务异常: {e}")

    def run_cleanup(self):
        """执行缓存清理任务"""
        scheduler_log.info("开始缓存清理任务")
        try:
            from ..processor.image_handler import get_image_handler
            handler = get_image_handler()
            count = handler.cleanup_cache(max_age_days=30)
            scheduler_log.info(f"清理完成: {count} 个文件")
        except Exception as e:
            scheduler_log.error(f"清理任务异常: {e}")

    def get_jobs(self) -> List[Dict]:
        """获取任务列表"""
        return [
            {
                'id': job.id,
                'name': job.name,
                'next_run': str(job.next_run_time) if job.next_run_time else None
            }
            for job in self.scheduler.get_jobs()
        ]

    def get_stats(self) -> Dict:
        """获取任务统计"""
        return self.monitor.get_stats()
