#!/usr/bin/env python3
"""
Auto Content Publisher - 主程序入口
"""
import sys
import argparse
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import Config
from database import Database
from logger import setup_logger
from scraper import RSSScraper, WebScraper
from processor import ContentProcessor
from scheduler import TaskScheduler
from publisher import WeChatPublisher, BlogPublisher


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Auto Content Publisher')
    parser.add_argument('--config', '-c', default='config/settings.yaml', help='配置文件路径')
    parser.add_argument('--mode', '-m', choices=['single', 'daemon'], default='single',
                        help='运行模式: single=单次执行, daemon=守护进程')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    return parser.parse_args()


def run_single(config: Config, db: Database, logger):
    """单次运行模式"""
    logger.info("Running in single mode...")
    
    # 1. 抓取 RSS
    rss_scraper = RSSScraper()
    rss_urls = config.get('rss_feeds', [])
    articles = []
    
    for url in rss_urls:
        logger.info(f"Fetching RSS: {url}")
        feed = rss_scraper.fetch_feed(url)
        articles.extend(feed.get('entries', []))
    
    # 2. 抓取网页
    web_scraper = WebScraper()
    web_urls = config.get('web_feeds', [])
    
    for url in web_urls:
        logger.info(f"Fetching web: {url}")
        article = web_scraper.extract_article(url)
        if article.get('content'):
            articles.append(article)
    
    # 3. 处理内容
    processor = ContentProcessor()
    processed = processor.batch_process(articles, {
        'required_keywords': config.get('filter_keywords', []),
        'forbidden_keywords': config.get('block_keywords', [])
    })
    
    logger.info(f"Processed {len(processed)} articles")
    
    # 4. 保存到数据库
    for article in processed:
        db.save_article(article)
    
    # 5. 发布
    publish_enabled = config.get('publish_enabled', False)
    if publish_enabled:
        publisher = WeChatPublisher(
            app_id=config.get('wechat_app_id'),
            app_secret=config.get('wechat_app_secret')
        )
        result = publisher.batch_publish(processed)
        logger.info(f"Published: {result}")
    
    logger.info("Single run completed!")
    return len(processed)


def run_daemon(config: Config, db: Database, logger):
    """守护进程模式"""
    logger.info("Running in daemon mode...")
    
    scheduler = TaskScheduler()
    
    # 添加 RSS 抓取任务
    rss_urls = config.get('rss_feeds', [])
    if rss_urls:
        scheduler.add_rss_fetch_task('rss_fetch', rss_urls, 
                                     config.get('rss_interval', 60))
    
    # 添加网页抓取任务
    web_urls = config.get('web_feeds', [])
    if web_urls:
        scheduler.add_http_fetch_task('web_fetch', web_urls,
                                      config.get('web_interval', 60))
    
    # 启动调度器
    scheduler.start(blocking=True)


def main():
    """主函数"""
    args = parse_args()
    
    # 加载配置
    config = Config(args.config)
    
    # 设置日志
    logger = setup_logger(verbose=args.verbose)
    
    # 初始化数据库
    db = Database(config.get('database_path', 'data/articles.db'))
    
    logger.info(f"Auto Content Publisher v0.1.0 starting...")
    logger.info(f"Mode: {args.mode}")
    
    # 根据模式运行
    if args.mode == 'single':
        run_single(config, db, logger)
    else:
        run_daemon(config, db, logger)


if __name__ == '__main__':
    main()
