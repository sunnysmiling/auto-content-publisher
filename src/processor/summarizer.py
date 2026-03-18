"""摘要生成器"""
from typing import Optional

from .base import BaseAIProcessor
from ..config import config
from ..logger import processor_log


class Summarizer:
    """摘要生成器"""

    def __init__(self, ai_processor: BaseAIProcessor = None):
        self.ai_processor = ai_processor

    def summarize(self, content: str, max_length: int = 100) -> str:
        """生成摘要"""
        if not content:
            return ""
        
        # 如果有 AI 处理器，使用 AI 生成
        if self.ai_processor:
            return self.ai_processor.generate_summary(content)
        
        # 否则使用简单提取
        return self._simple_summarize(content, max_length)

    def _simple_summarize(self, content: str, max_length: int = 100) -> str:
        """简单摘要提取（取前 N 个字符到句号）"""
        # 清理内容
        content = content.replace('\n', ' ').replace('\r', '')
        
        # 找到第一个句号
        sentences = content.split('。')
        if sentences and sentences[0]:
            summary = sentences[0].strip()
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            return summary
        
        # 没有句号，截取前 N 字符
        return content[:max_length] + ("..." if len(content) > max_length else "")

    def summarize_batch(self, contents: list) -> list:
        """批量生成摘要"""
        return [self.summarize(c) for c in contents]


def create_summarizer(ai_config: dict = None) -> Summarizer:
    """创建摘要生成器"""
    from .openai_processor import OpenAIProcessor
    
    ai_processor = None
    if ai_config and ai_config.get('api_key'):
        ai_processor = OpenAIProcessor(ai_config)
    
    return Summarizer(ai_processor)
