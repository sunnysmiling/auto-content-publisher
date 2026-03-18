#!/usr/bin/env python3
"""Auto Content Publisher - 主入口"""
import sys
import argparse
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.database import db
from src.logger import log, crawler_log
from src.scraper import Crawler
from src.processor import Processor
from src.publisher import Publisher
from src.scheduler import TaskScheduler


def main():
    parser = argparse.ArgumentParser(description='Auto Content Publisher')
    parser.add_argument('command', choices=['crawl', 'add-source', 'list-sources', 'serve', 'process', 'publish'],
                       help='要执行的命令')
    parser.add_argument('--name', help='数据源名称')
    parser.add_argument('--url', help='数据源 URL')
    parser.add_argument('--type', default='rss', choices=['rss', 'http'], 
                       help='数据源类型')
    parser.add_argument('--interval', type=int, default=120,
                       help='采集间隔（分钟）')
    parser.add_argument('--limit', type=int, default=10,
                       help='处理文章数量限制')
    
    args = parser.parse_args()
    
    if args.command == 'crawl':
        # 执行采集
        crawler = Crawler()
        count = crawler.crawl_all()
        log.info(f"采集完成，新增 {count} 篇文章")
        
    elif args.command == 'add-source':
        # 添加数据源
        if not args.name or not args.url:
            print("错误: --name 和 --url 是必填参数")
            sys.exit(1)
        
        source_id = db.add_source(
            name=args.name,
            url=args.url,
            source_type=args.type,
            crawl_interval=args.interval
        )
        log.info(f"数据源添加成功: {args.name}, ID: {source_id}")
        
    elif args.command == 'list-sources':
        # 列出数据源
        sources = db.get_sources()
        print(f"{'ID':<5} {'名称':<20} {'类型':<10} {'URL':<40} {'启用':<5}")
        print("-" * 85)
        for s in sources:
            print(f"{s['id']:<5} {s['name']:<20} {s['type']:<10} {s['url']:<40} {'是' if s['enabled'] else '否':<5}")
    
    elif args.command == 'serve':
        # 启动服务模式
        log.info("启动定时任务调度器...")
        scheduler = TaskScheduler()
        scheduler.start()
        
        # 输出任务列表
        print("\n已启动的任务:")
        for job in scheduler.get_jobs():
            print(f"  - {job['name']}: 下次执行 {job['next_run']}")
        print("\n按 Ctrl+C 停止服务")
        
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()
            log.info("服务已停止")

    elif args.command == 'process':
        # 处理文章
        processor = Processor()
        count = processor.process_pending(limit=args.limit)
        log.info(f"处理完成，成功 {count} 篇文章")

    elif args.command == 'publish':
        # 发布文章
        publisher = Publisher()
        count = publisher.publish_pending(limit=args.limit)
        log.info(f"发布完成，成功 {count} 篇文章")


if __name__ == '__main__':
    main()
