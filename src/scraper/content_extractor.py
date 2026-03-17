"""
内容提取器 - 从任意网页提取文章内容
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


class ContentExtractor:
    """智能内容提取器"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
    
    def extract(self, url: str) -> Dict:
        """
        从URL提取文章内容
        
        Args:
            url: 文章URL
            
        Returns:
            提取的文章数据
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取元数据
            metadata = self._extract_metadata(soup, url)
            
            # 提取正文
            content = self._extract_article_body(soup)
            
            # 提取图片
            images = self._extract_all_images(soup, url)
            
            return {
                'url': url,
                'title': metadata.get('title', ''),
                'author': metadata.get('author'),
                'publish_time': metadata.get('publish_time'),
                'description': metadata.get('description', ''),
                'content': content,
                'images': images,
                'source': metadata.get('site_name', ''),
            }
            
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            return {'url': url, 'error': str(e)}
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """提取元数据"""
        metadata = {}
        
        # Title
        if soup.title:
            metadata['title'] = soup.title.string.strip()
        
        # Meta tags
        for meta in soup.find_all('meta'):
            prop = meta.get('property') or meta.get('name', '')
            content = meta.get('content', '')
            
            if 'title' in prop.lower():
                metadata['title'] = content
            elif 'description' in prop.lower():
                metadata['description'] = content
            elif 'author' in prop.lower():
                metadata['author'] = content
            elif 'published' in prop.lower() or 'date' in prop.lower():
                metadata['publish_time'] = content
            elif 'site_name' in prop.lower():
                metadata['site_name'] = content
        
        # Open Graph title takes precedence
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            metadata['title'] = og_title['content']
        
        return metadata
    
    def _extract_article_body(self, soup: BeautifulSoup) -> str:
        """提取文章主体"""
        # 移除无关标签
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 
                        'aside', 'iframe', 'noscript', 'form']):
            tag.decompose()
        
        # 尝试多种选择器
        selectors = [
            'article',
            '[role="main"]',
            'main',
            '.post-content',
            '.article-content',
            '.entry-content',
            '.content',
            '#content',
            '.post',
            '.article',
        ]
        
        article_elem = None
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and len(elem.get_text(strip=True)) > 200:
                article_elem = elem
                break
        
        if not article_elem:
            article_elem = soup.body
        
        if not article_elem:
            return ''
        
        # 提取文本
        text = article_elem.get_text(separator='\n', strip=True)
        
        # 清理
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 去除重复行
        cleaned = []
        prev_line = ''
        for line in lines:
            if line != prev_line and len(line) > 10:
                cleaned.append(line)
                prev_line = line
        
        return '\n\n'.join(cleaned[:300])
    
    def _extract_all_images(self, soup: BeautifulSoup, base_url: str) -> list:
        """提取所有图片"""
        from urllib.parse import urljoin
        
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-original')
            if src and src.startswith('http'):
                images.append(src)
            elif src:
                full_url = urljoin(base_url, src)
                if full_url.startswith('http'):
                    images.append(full_url)
        
        # 去重
        return list(dict.fromkeys(images))[:20]


# 便捷函数
def extract_article(url: str) -> Dict:
    """提取单篇文章"""
    extractor = ContentExtractor()
    return extractor.extract(url)
