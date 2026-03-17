"""
测试采集模块
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper import RSSScraper, WebScraper


class TestRSSScraper:
    """测试 RSS 采集器"""
    
    def test_rss_scraper_init(self):
        """测试 RSS 采集器初始化"""
        scraper = RSSScraper()
        assert scraper is not None
        assert hasattr(scraper, 'fetch')
    
    def test_rss_scraper_fetch(self):
        """测试 RSS 采集"""
        scraper = RSSScraper()
        # 使用一个公开的 RSS 源测试
        articles = scraper.fetch('https://hnrss.org/newest')
        assert isinstance(articles, list)
    
    def test_rss_scraper_fetch_multiple(self):
        """测试多 RSS 源采集"""
        scraper = RSSScraper()
        urls = [
            'https://hnrss.org/newest',
        ]
        articles = scraper.fetch_multiple(urls)
        assert isinstance(articles, list)


class TestWebScraper:
    """测试网页抓取器"""
    
    def test_web_scraper_init(self):
        """测试网页抓取器初始化"""
        scraper = WebScraper()
        assert scraper is not None
        assert hasattr(scraper, 'fetch_page')
    
    def test_web_scraper_fetch_page(self):
        """测试网页获取"""
        scraper = WebScraper()
        html = scraper.fetch_page('https://example.com')
        assert html is not None
        assert len(html) > 0
    
    def test_web_scraper_extract_article(self):
        """测试文章提取"""
        scraper = WebScraper()
        # 测试提取 example.com
        result = scraper.extract_article('https://example.com')
        assert isinstance(result, dict)
        assert 'url' in result
    
    def test_web_scraper_extract_links(self):
        """测试链接提取"""
        scraper = WebScraper()
        links = scraper.extract_links('https://example.com')
        assert isinstance(links, list)
