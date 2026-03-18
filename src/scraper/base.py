"""采集器基类"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Article:
    """文章数据结构"""
    url: str
    title: str
    content: str = ''
    summary: str = ''
    published_at: Optional[str] = None
    author: Optional[str] = None
    source_name: str = ''


class BaseScraper(ABC):
    """采集器基类"""

    def __init__(self, source_config: Dict):
        self.source_config = source_config
        self.name = source_config.get('name', 'unknown')
        self.url = source_config.get('url', '')
        self.source_id = source_config.get('id')

    @abstractmethod
    def fetch(self) -> List[Article]:
        """获取文章列表"""
        pass

    @abstractmethod
    def fetch_content(self, url: str) -> str:
        """获取文章详情"""
        pass

    def parse(self, html: str) -> List[Article]:
        """解析 HTML（可选实现）"""
        raise NotImplementedError
