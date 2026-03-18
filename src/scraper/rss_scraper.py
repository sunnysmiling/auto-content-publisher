"""RSS 采集器"""
import feedparser
from datetime import datetime
from typing import List, Optional
import time

from .base import BaseScraper, Article
from ..config import config
from ..logger import crawler_log


class RSSScraper(BaseScraper):
    """RSS 采集器"""

    def __init__(self, source_config: dict):
        super().__init__(source_config)
        self.timeout = config.crawl_timeout

    def fetch(self) -> List[Article]:
        """获取 RSS 源文章列表"""
        articles = []
        crawler_log.info(f"开始采集 RSS: {self.name} - {self.url}")
        
        try:
            feed = feedparser.parse(
                self.url,
                timeout=self.timeout
            )
            
            if feed.bozo and not feed.entries:
                crawler_log.warning(f"RSS 解析异常: {self.name}, {feed.bozo_exception}")
                return []

            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry)
                    if article:
                        articles.append(article)
                except Exception as e:
                    crawler_log.warning(f"解析 RSS 条目失败: {e}")
                    continue

            crawler_log.info(f"RSS 采集完成: {self.name}, 获取 {len(articles)} 篇文章")
            
        except Exception as e:
            crawler_log.error(f"RSS 采集失败: {self.name}, {e}")
            
        return articles

    def _parse_entry(self, entry) -> Optional[Article]:
        """解析单个 RSS 条目"""
        # 获取标题
        title = entry.get('title', '').strip()
        if not title:
            return None

        # 获取链接
        link = entry.get('link', '')
        if not link:
            return None

        # 获取发布时间
        published = None
        if hasattr(entry, 'published'):
            published = entry.published
        elif hasattr(entry, 'updated'):
            published = entry.updated
        elif hasattr(entry, 'dc_date'):
            published = str(entry.dc_date)

        # 获取摘要/内容
        summary = ''
        if hasattr(entry, 'summary'):
            summary = entry.summary
        elif hasattr(entry, 'description'):
            summary = entry.description
        elif hasattr(entry, 'content'):
            # 某些 RSS 使用 content[0].value
            if entry.content:
                summary = entry.content[0].value

        # 清理 HTML 标签
        summary = self._clean_html(summary)

        return Article(
            url=link,
            title=title,
            summary=summary,
            published_at=published,
            source_name=self.name
        )

    def _clean_html(self, text: str) -> str:
        """简单的 HTML 清理"""
        import re
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def fetch_content(self, url: str) -> str:
        """获取文章详情（RSS 通常只返回摘要，如需全文可额外请求）"""
        import requests
        from bs4 import BeautifulSoup
        
        try:
            response = requests.get(
                url, 
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # 尝试提取文章内容（通用选择器，可能需根据具体站点调整）
            article = soup.find('article') or soup.find('div', class_='content')
            
            if article:
                return article.get_text(strip=True)
            
            return soup.get_text(strip=True)[:5000]  # 返回前 5000 字符
            
        except Exception as e:
            crawler_log.warning(f"获取文章内容失败: {url}, {e}")
            return ''
