"""HTTP 网页采集器"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Dict
import hashlib
import time

from .base import BaseScraper, Article
from ..config import config
from ..logger import crawler_log


class HTTPScraper(BaseScraper):
    """HTTP 网页采集器"""

    def __init__(self, source_config: dict):
        super().__init__(source_config)
        self.timeout = config.crawl_timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })

    def fetch(self) -> List[Article]:
        """获取网页文章列表"""
        articles = []
        crawler_log.info(f"开始采集网页: {self.name} - {self.url}")
        
        try:
            response = self.session.get(self.url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            article_links = self._extract_article_links(soup)
            
            for link in article_links[:20]:  # 限制数量
                try:
                    article = self._fetch_article(link)
                    if article:
                        articles.append(article)
                    time.sleep(0.5)  # 避免请求过快
                except Exception as e:
                    crawler_log.warning(f"采集文章失败: {link}, {e}")
                    continue

            crawler_log.info(f"网页采集完成: {self.name}, 获取 {len(articles)} 篇文章")
            
        except Exception as e:
            crawler_log.error(f"网页采集失败: {self.name}, {e}")
            
        return articles

    def _extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """提取文章链接"""
        links = []
        
        # 查找文章列表区域
        selectors = [
            'article a',
            '.post-list a',
            '.article-list a',
            '.entry-title a',
            'h2 a',
            '.title a',
            '.post-title a',
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                href = elem.get('href')
                if href and href.startswith('http'):
                    links.append(href)
        
        # 去重
        return list(dict.fromkeys(links))

    def _fetch_article(self, url: str) -> Optional[Article]:
        """获取单篇文章"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = self._extract_title(soup)
            if not title:
                return None
            
            # 提取内容
            content = self._extract_content(soup)
            
            # 提取发布时间
            published = self._extract_date(soup)
            
            return Article(
                url=url,
                title=title,
                content=content,
                published_at=published,
                source_name=self.name
            )
            
        except Exception as e:
            crawler_log.warning(f"获取文章失败: {url}, {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取标题"""
        selectors = [
            'h1.title',
            'h1.entry-title',
            'article h1',
            '.post-title h1',
            'h1',
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        
        # Fallback to title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return ''

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取文章内容"""
        selectors = [
            'article .content',
            'article .post-content',
            'article .entry-content',
            '.post-body',
            '.article-content',
            '.article-body',
            'article',
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                # 移除脚本和样式
                for tag in elem(['script', 'style', 'nav', 'footer', 'header']):
                    tag.decompose()
                return elem.get_text(strip=True)
        
        # Fallback to body
        body = soup.find('body')
        if body:
            return body.get_text(strip=True)[:10000]
        
        return ''

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """提取发布时间"""
        selectors = [
            'time[datetime]',
            '.published',
            '.date',
            '.post-date',
            'meta[property="article:published_time"]',
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                if elem.name == 'meta':
                    return elem.get('content', '')
                return elem.get('datetime', '') or elem.get_text(strip=True)
        
        return None

    def fetch_content(self, url: str) -> str:
        """获取文章详情"""
        article = self._fetch_article(url)
        return article.content if article else ''
