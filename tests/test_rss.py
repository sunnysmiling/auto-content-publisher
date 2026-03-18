"""测试 RSS 解析模块"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scraper.rss_scraper import RSSScraper


class TestRSSParser:
    """测试 RSS 解析功能"""

    @pytest.fixture
    def sample_rss_feed(self):
        """示例 RSS 数据"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <item>
      <title>测试文章 1</title>
      <link>https://example.com/article/1</link>
      <pubDate>Wed, 18 Mar 2026 00:00:00 GMT</pubDate>
      <description>这是文章摘要</description>
      <guid>https://example.com/article/1</guid>
    </item>
    <item>
      <title>测试文章 2</title>
      <link>https://example.com/article/2</link>
      <pubDate>Tue, 17 Mar 2026 00:00:00 GMT</pubDate>
      <description>这是另一篇文章摘要</description>
    </item>
  </channel>
</rss>'''

    def test_parse_rss_feed(self, sample_rss_feed):
        """测试解析 RSS Feed"""
        scraper = RSSScraper("https://example.com/feed.xml")
        
        with patch.object(scraper, 'fetch') as mock_fetch:
            mock_fetch.return_value = sample_rss_feed
            articles = scraper.parse()
            
        assert len(articles) == 2
        assert articles[0]['title'] == "测试文章 1"
        assert articles[0]['link'] == "https://example.com/article/1"
        assert articles[0]['summary'] == "这是文章摘要"

    def test_parse_rss_with_missing_fields(self):
        """测试解析不完整的数据"""
        rss = '''<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>只有标题的文章</title>
    </item>
  </channel>
</rss>'''
        
        scraper = RSSScraper("https://example.com/feed.xml")
        with patch.object(scraper, 'fetch', return_value=rss):
            articles = scraper.parse()
            
        assert len(articles) == 1
        assert articles[0]['title'] == "只有标题的文章"
        assert articles[0].get('link') is None

    def test_parse_empty_feed(self):
        """测试解析空 RSS"""
        rss = '''<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>Empty Feed</title>
  </channel>
</rss>'''
        
        scraper = RSSScraper("https://example.com/feed.xml")
        with patch.object(scraper, 'fetch', return_value=rss):
            articles = scraper.parse()
            
        assert len(articles) == 0

    def test_date_parsing(self, sample_rss_feed):
        """测试日期解析"""
        scraper = RSSScraper("https://example.com/feed.xml")
        
        with patch.object(scraper, 'fetch', return_value=sample_rss_feed):
            articles = scraper.parse()
            
        # 验证日期被解析
        assert 'published' in articles[0]

    def test_multiple_sources(self):
        """测试多数据源"""
        scrapers = [
            RSSScraper("https://example.com/feed1.xml"),
            RSSScraper("https://example.com/feed2.xml"),
            RSSScraper("https://example.com/feed3.xml"),
        ]
        
        assert len(scrapers) == 3
        assert scrapers[0].url == "https://example.com/feed1.xml"
        assert scrapers[1].url == "https://example.com/feed2.xml"
