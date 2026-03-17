"""
RSS 订阅源抓取模块
"""
import feedparser
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RSSScraper:
    """RSS/Atom 订阅源抓取器"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_feed(self, url: str) -> Dict:
        """
        获取订阅源内容
        
        Args:
            url: RSS/Atom 链接
            
        Returns:
            解析后的订阅源数据
        """
        try:
            logger.info(f"Fetching RSS feed: {url}")
            feed = feedparser.parse(url, timeout=self.timeout)
            
            result = {
                'url': url,
                'title': feed.feed.get('title', ''),
                'description': feed.feed.get('description', ''),
                'entries': []
            }
            
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'guid': entry.get('id', entry.get('link', '')),
                }
                # 尝试获取正文内容
                if hasattr(entry, 'content'):
                    article['content'] = entry.content[0].value
                elif hasattr(entry, 'summary_detail'):
                    article['content'] = entry.summary_detail.value
                else:
                    article['content'] = article['summary']
                
                result['entries'].append(article)
            
            logger.info(f"Fetched {len(result['entries'])} entries from {url}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch RSS feed {url}: {e}")
            return {'url': url, 'error': str(e), 'entries': []}
    
    def fetch_multiple(self, urls: List[str]) -> List[Dict]:
        """
        批量获取多个订阅源
        
        Args:
            urls: RSS 链接列表
            
        Returns:
            所有订阅源的文章列表
        """
        results = []
        for url in urls:
            feed_data = self.fetch_feed(url)
            if feed_data.get('entries'):
                results.extend(feed_data['entries'])
        return results
    
    def get_new_entries(self, url: str, known_guids: set) -> List[Dict]:
        """
        只获取新文章（去重）
        
        Args:
            url: RSS 链接
            known_guids: 已知的文章 GUID 集合
            
        Returns:
            新文章列表
        """
        feed_data = self.fetch_feed(url)
        new_entries = [
            e for e in feed_data.get('entries', [])
            if e['guid'] not in known_guids
        ]
        logger.info(f"Found {len(new_entries)} new entries from {url}")
        return new_entries


# 测试
if __name__ == '__main__':
    # 测试抓取技术博客
    scraper = RSSScraper()
    result = scraper.fetch_feed('https://blog.rss.ac/feed.xml')
    print(f"Title: {result.get('title')}")
    print(f"Entries: {len(result.get('entries', []))}")
    if result.get('entries'):
        print(f"First entry: {result['entries'][0]['title']}")
