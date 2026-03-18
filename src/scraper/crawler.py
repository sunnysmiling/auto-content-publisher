"""采集器工厂"""
from typing import List, Dict

from .base import BaseScraper, Article
from .rss_scraper import RSSScraper
from .http_scraper import HTTPScraper
from ..database import db
from ..logger import crawler_log


class ScraperFactory:
    """采集器工厂"""

    _scrapers = {
        'rss': RSSScraper,
        'http': HTTPScraper,
    }

    @classmethod
    def create(cls, source_config: Dict) -> BaseScraper:
        """创建采集器"""
        source_type = source_config.get('type', 'rss')
        scraper_class = cls._scrapers.get(source_type, RSSScraper)
        return scraper_class(source_config)

    @classmethod
    def register(cls, name: str, scraper_class: type):
        """注册自定义采集器"""
        cls._scrapers[name] = scraper_class


class Crawler:
    """采集调度器"""

    def __init__(self):
        self.db = db
        self.factory = ScraperFactory()

    def crawl_all(self) -> int:
        """采集所有启用的数据源"""
        sources = self.db.get_sources(enabled_only=True)
        total_articles = 0

        for source in sources:
            try:
                count = self.crawl_source(source['id'])
                total_articles += count
            except Exception as e:
                crawler_log.error(f"采集数据源失败: {source['name']}, {e}")

        crawler_log.info(f"采集完成，共获取 {total_articles} 篇文章")
        return total_articles

    def crawl_source(self, source_id: int) -> int:
        """采集指定数据源"""
        sources = self.db.get_sources()
        source = next((s for s in sources if s['id'] == source_id), None)
        
        if not source:
            crawler_log.error(f"数据源不存在: {source_id}")
            return 0

        if not source['enabled']:
            crawler_log.info(f"数据源未启用: {source['name']}")
            return 0

        # 创建采集器
        scraper = self.factory.create(source)
        
        # 采集文章
        articles = scraper.fetch()
        
        # 存储文章
        count = 0
        for article in articles:
            if not self.db.article_exists(article.url):
                self.db.add_article(
                    source_id=source['id'],
                    source_url=article.url,
                    title=article.title,
                    content=article.summary or article.content
                )
                count += 1

        crawler_log.info(
            f"数据源采集完成: {source['name']}, "
            f"新增 {count}/{len(articles)} 篇"
        )
        return count

    def crawl_article_content(self, article_id: int) -> bool:
        """抓取文章详细内容"""
        article = self.db.get_article(article_id)
        if not article:
            return False

        # 获取数据源
        sources = self.db.get_sources()
        source = next(
            (s for s in sources if s['id'] == article['source_id']), 
            None
        )
        
        if not source:
            return False

        scraper = self.factory.create(source)
        content = scraper.fetch_content(article['source_url'])
        
        if content:
            self.db.update_article(
                article_id,
                original_content=content,
                processed_content=content
            )
            return True
        
        return False
