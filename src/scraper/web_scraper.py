"""
HTML 网页抓取模块
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class WebScraper:
    """网页内容抓取器"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        获取网页 HTML 内容
        
        Args:
            url: 网页 URL
            
        Returns:
            HTML 内容，失败返回 None
        """
        try:
            logger.info(f"Fetching page: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def extract_article(self, url: str, selectors: Dict = None) -> Dict:
        """
        提取文章内容
        
        Args:
            url: 文章 URL
            selectors: 自定义 CSS 选择器
            
        Returns:
            提取的文章数据
        """
        html = self.fetch_page(url)
        if not html:
            return {'url': url, 'error': 'Failed to fetch page'}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 默认选择器
        default_selectors = {
            'title': 'h1',
            'content': ['article', '.content', '.post-content', '.article-content', 'main'],
            'author': ['.author', '.post-author', '[rel="author"]'],
            'date': ['.date', '.post-date', 'time']
        }
        
        selectors = selectors or default_selectors
        
        # 提取标题
        title = ''
        if selectors.get('title'):
            title_elem = soup.select_one(selectors['title'])
            if title_elem:
                title = title_elem.get_text(strip=True)
        
        # 提取正文
        content = ''
        contentSelectors = selectors.get('content', [])
        if isinstance(contentSelectors, str):
            contentSelectors = [contentSelectors]
        
        for sel in contentSelectors:
            content_elem = soup.select_one(sel)
            if content_elem:
                # 移除脚本和样式
                for tag in content_elem.find_all(['script', 'style']):
                    tag.decompose()
                content = content_elem.get_text(separator='\n', strip=True)
                break
        
        # 提取作者
        author = ''
        for sel in selectors.get('author', []):
            author_elem = soup.select_one(sel)
            if author_elem:
                author = author_elem.get_text(strip=True)
                break
        
        # 提取日期
        date = ''
        for sel in selectors.get('date', []):
            date_elem = soup.select_one(sel)
            if date_elem:
                date = date_elem.get_text(strip=True) or date_elem.get('datetime', '')
                break
        
        # 提取图片
        images = []
        if content_elem:
            for img in content_elem.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if src:
                    images.append(urljoin(url, src))
        
        return {
            'url': url,
            'title': title,
            'content': content,
            'author': author,
            'date': date,
            'images': images[:10]  # 最多10张图
        }
    
    def extract_links(self, url: str, selector: str = 'a') -> List[str]:
        """
        提取页面所有链接
        
        Args:
            url: 页面 URL
            selector: 链接选择器
            
        Returns:
            链接列表
        """
        html = self.fetch_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for a in soup.select(selector):
            href = a.get('href')
            if href:
                links.append(urljoin(url, href))
        
        return links


if __name__ == '__main__':
    # 测试
    scraper = WebScraper()
    # 测试提取链接
    links = scraper.extract_links('https://news.ycombinator.com/')
    print(f"Found {len(links)} links")
