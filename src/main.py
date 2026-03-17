#!/usr/bin/env python3
"""
Auto Content Publisher - 主程序入口
"""
import os
import sys
import argparse
import logging
from datetime import datetime

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.database import Database
from src.logger import setup_logger
from src.scraper import RSSScraper, WebScraper
from src.processor import ContentProcessor
from src.scheduler import TaskScheduler
from src.publisher import WeChatPublisher, BlogPublisher
from src.api import run_api


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Auto Content Publisher')
    parser.add_argument('--config', '-c', default='config/settings.yaml', help='配置文件路径')
    parser.add_argument('--mode', '-m', choices=['api', 'scheduler', 'fetch', 'publish'], 
                        default='api', help='运行模式')
    parser.add_argument('--debug', '-d', action='store_true', help='调试模式')
    parser.add_argument('--port', '-p', type=int, default=5000, help='API 服务端口')
    return parser.parse_args()


def init_components(config: Config):
    """初始化所有组件"""
    logger = logging.getLogger(__name__)
    logger.info("Initializing components...")
    
    # 数据库
    db = Database(config.get('database', {}))
    
    # 采集器
    rss_scraper = RSSScraper()
    web_scraper = WebScraper()
    
    # 处理器
    processor = ContentProcessor()
    
    # 调度器
    scheduler = TaskScheduler()
    
    # 发布器
    wechat_publisher = WeChatPublisher(
        app_id=config.get('wechat.app_id'),
        app_secret=config.get('wechat.app_secret')
    )
    blog_publisher = BlogPublisher(
        api_url=config.get('blog.api_url'),
        api_key=config.get('blog.api_key')
    )
    
    logger.info("All components initialized")
    
    return {
        'db': db,
        'rss_scraper': rss_scraper,
        'web_scraper': web_scraper,
        'processor': processor,
        'scheduler': scheduler,
        'wechat_publisher': wechat_publisher,
        'blog_publisher': blog_publisher
    }


def run_scheduler_mode(components, config):
    """调度器模式"""
    scheduler = components['scheduler']
    
    # 添加 RSS 采集任务
    rss_feeds = config.get('rss_feeds', [])
    if rss_feeds:
        scheduler.add_rss_fetch_task('rss_fetch', rss_feeds, interval_minutes=60)
    
    # 添加 HTTP 采集任务
    http_urls = config.get('http_urls', [])
    if http_urls:
        scheduler.add_http_fetch_task('http_fetch', http_urls, interval_minutes=60)
    
    # 启动调度器
    logger.info("Starting scheduler...")
    scheduler.start(blocking=True)


def run_fetch_mode(components, config):
    """采集模式 - 执行一次采集"""
    rss_scraper = components['rss_scraper']
    web_scraper = components['web_scraper']
    processor = components['processor']
    
    articles = []
    
    # 采集 RSS
    rss_feeds = config.get('rss_feeds', [])
    if rss_feeds:
        rss_articles = rss_scraper.fetch_multiple(rss_feeds)
        articles.extend(rss_articles)
    
    # 采集网页
    http_urls = config.get('http_urls', [])
    for url in http_urls:
        article = web_scraper.extract_article(url)
        if article.get('content'):
            articles.append(article)
    
    # 处理文章
    processed = processor.batch_process(articles)
    
    print(f"Fetched {len(articles)} articles, {len(processed)} after processing")
    
    return processed


def run_publish_mode(components, config):
    """发布模式 - 执行一次发布"""
    publisher = components['wechat_publisher']
    
    # TODO: 从数据库获取待发布文章
    articles = []
    
    result = publisher.batch_publish(articles)
    print(f"Published: {result}")


def run_api_mode(components, config, port):
    """API 模式"""
    from src.api import init_api
    
    # 初始化 API
    init_api(
        components['rss_scraper'],
        components['processor'],
        components['scheduler'],
        components['wechat_publisher']
    )
    
    # 启动 API 服务
    run_api(port=port, debug=config.get('debug', False))


def main():
    """主函数"""
    args = parse_args()
    
    # 加载配置
    config = Config(args.config)
    
    # 设置日志
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logger(level=log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Auto Content Publisher in {args.mode} mode")
    
    # 初始化组件
    components = init_components(config)
    
    # 根据模式运行
    if args.mode == 'scheduler':
        run_scheduler_mode(components, config)
    elif args.mode == 'fetch':
        run_fetch_mode(components, config)
    elif args.mode == 'publish':
        run_publish_mode(components, config)
    elif args.mode == 'api':
        run_api_mode(components, config, args.port)


if __name__ == '__main__':
    main()
