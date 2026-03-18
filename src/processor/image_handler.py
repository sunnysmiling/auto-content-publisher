"""封面图处理器"""
import os
import re
import hashlib
import shutil
from pathlib import Path
from typing import Optional
import requests
from urllib.parse import urlparse

from ..config import config
from ..logger import processor_log


class ImageHandler:
    """封面图处理器"""

    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir or (config.base_dir / 'data' / 'cache' / 'images'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def extract_from_content(self, content: str) -> Optional[str]:
        """从内容中提取图片 URL"""
        if not content:
            return None
        
        # 匹配常见的图片 URL 模式
        patterns = [
            r'https?://[^\s"\'<>]+\.(jpg|jpeg|png|gif|webp)',
            r'https?://[^\s"\'<>]+/img[^\s"\'<>]*\.(jpg|jpeg|png|gif|webp)',
            r'https?://[^\s"\'<>]+/image[^\s"\'<>]*\.(jpg|jpeg|png|gif|webp)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.I)
            if matches:
                return matches[0]
        
        return None

    def extract_from_html(self, html: str) -> Optional[str]:
        """从 HTML 中提取图片"""
        if not html:
            return None
        
        # 查找 og:image 或 twitter:image
        og_image = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
        if og_image:
            return og_image.group(1)
        
        twitter_image = re.search(r'<meta[^>]*name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
        if twitter_image:
            return twitter_image.group(1)
        
        # 查找第一张大图
        return self.extract_from_content(html)

    def download_image(self, url: str, article_id: int = None) -> Optional[str]:
        """下载图片到本地缓存"""
        if not url:
            return None
        
        try:
            # 生成文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            ext = Path(urlparse(url).path).suffix or '.jpg'
            if not ext.startswith('.'):
                ext = '.' + ext
            
            filename = f"{article_id or 'cover'}_{url_hash}{ext}"
            local_path = self.cache_dir / filename
            
            # 如果已存在，直接返回
            if local_path.exists():
                return str(local_path)
            
            # 下载图片
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # 保存图片
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            
            processor_log.info(f"下载封面图: {url} -> {local_path}")
            return str(local_path)
            
        except Exception as e:
            processor_log.warning(f"下载封面图失败: {url}, {e}")
            return None

    def process_cover_image(self, article: dict, html_content: str = None) -> Optional[str]:
        """处理文章封面图"""
        # 1. 优先使用已有的 cover_image
        cover_url = article.get('cover_image')
        
        # 2. 从内容中提取
        if not cover_url:
            content = article.get('original_content', '')
            cover_url = self.extract_from_content(content)
        
        # 3. 从 HTML 中提取
        if not cover_url and html_content:
            cover_url = self.extract_from_html(html_content)
        
        # 4. 下载到本地
        if cover_url:
            return self.download_image(cover_url, article.get('id'))
        
        return None

    def cleanup_cache(self, max_age_days: int = 30):
        """清理过期缓存图片"""
        import time
        
        now = time.time()
        max_age = max_age_days * 86400
        cleaned = 0
        
        for file in self.cache_dir.iterdir():
            if file.is_file():
                age = now - file.stat().st_mtime
                if age > max_age:
                    file.unlink()
                    cleaned += 1
        
        processor_log.info(f"清理缓存图片: {cleaned} 个")
        return cleaned


# 全局实例
_image_handler = None

def get_image_handler() -> ImageHandler:
    """获取图片处理器实例"""
    global _image_handler
    if _image_handler is None:
        _image_handler = ImageHandler()
    return _image_handler
