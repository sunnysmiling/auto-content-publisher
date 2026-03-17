"""
网页抓取模块
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import logging
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class HTTPScraper:
    """HTTP 网页抓取器"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def fetch_page(self, url: str) -> Dict:
        """
        获取网页内容
        
        Args:
            url: 目标URL
            
        Returns:
            页面数据字典
        """
        try:
            logger.info(f"Fetching page: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 检测编码
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = soup.title.string if soup.title else ''
            if not title:
                title = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''
            
            # 提取正文内容
            content = self._extract_content(soup)
            
            # 提取图片
            images = self._extract_images(soup, url)
            
            # 提取发布时间
            pub_time = self._extract_publish_time(soup)
            
            # 提取作者
            author = self._extract_author(soup)
            
            result = {
                'url': url,
                'title': title,
                'content': content,
                'images': images,
                'publish_time': pub_time,
                'author': author,
                'html': response.text[:50000]  # 保存部分HTML用于后续处理
            }
            
            logger.info(f"Successfully fetched: {url}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch page {url}: {e}")
            return {'url': url, 'error': str(e)}
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取正文内容"""
        # 移除脚本和样式
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        # 尝试找主要内容区域
        main_content = (
            soup.find('article') or 
            soup.find('main') or 
            soup.find('div', class_=re.compile(r'content|article|post|entry', re.I)) or
            soup.find('div', id=re.compile(r'content|article|post|entry', re.I))
        )
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        
        # 清理空白
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines[:500])  # 限制长度
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """提取图片URL列表"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                full_url = urljoin(base_url, src)
                if full_url.startswith('http'):
                    images.append(full_url)
        return images[:10]  # 最多10张
    
    def _extract_publish_time(self, soup: BeautifulSoup) -> Optional[str]:
        """提取发布时间"""
        # 尝试多种标签
        time_tag = soup.find('time')
        if time_tag and time_tag.get('datetime'):
            return time_tag['datetime']
        
        # 查找 meta 标签
        for meta in soup.find_all('meta'):
            if meta.get('property') in ['article:published_time', 'og:updated_time']:
                return meta.get('content')
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """提取作者"""
        # 查找作者信息
        author_tag = soup.find('meta', attrs={'name': 'author'})
        if author_tag:
            return author_tag.get('content')
        
        author_tag = soup.find('span', class_=re.compile(r'author', re.I))
        if author_tag:
            return author_tag.get_text(strip=True)
        
        return None
    
    def fetch_multiple(self, urls: List[str]) -> List[Dict]:
        """批量获取多个页面"""
        results = []
        for url in urls:
            page_data = self.fetch_page(url)
            if not page_data.get('error'):
                results.append(page_data)
        return results


# 测试
if __name__ == '__main__':
    scraper = HTTPScraper()
    result = scraper.fetch_page('https://example.com')
    print(f"Title: {result.get('title')}")
    print(f"Content length: {len(result.get('content', ''))}")
