"""AI 处理器基类"""
from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseAIProcessor(ABC):
    """AI 处理器基类"""

    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', 'gpt-4')
        self.temperature = config.get('temperature', 0.7)

    @abstractmethod
    def process(self, article: Dict) -> Dict:
        """处理文章，返回处理后的结果"""
        pass

    @abstractmethod
    def generate_summary(self, content: str) -> str:
        """生成摘要"""
        pass

    @abstractmethod
    def rewrite_title(self, title: str, content: str) -> str:
        """重写标题"""
        pass

    @abstractmethod
    def extract_cover_image(self, content: str, url: str) -> Optional[str]:
        """提取封面图"""
        pass
