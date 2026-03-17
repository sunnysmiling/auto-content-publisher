"""
内容处理模块 - AI 改写
"""
import hashlib
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ContentProcessor:
    """内容处理器 - 去重、过滤、改写"""
    
    def __init__(self):
        self.min_length = 100  # 最小内容长度
        self.max_length = 50000  # 最大内容长度
    
    def clean_html(self, html: str) -> str:
        """清理 HTML 标签"""
        # 移除脚本和样式
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.I)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.I)
        return html
    
    def extract_text(self, html: str) -> str:
        """从 HTML 提取纯文本"""
        import BeautifulSoup
        soup = BeautifulSoup.BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    
    def calculate_hash(self, content: str) -> str:
        """计算内容指纹"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, content: str, known_hashes: set) -> bool:
        """检查是否重复"""
        content_hash = self.calculate_hash(content)
        return content_hash in known_hashes
    
    def filter_by_length(self, content: str) -> bool:
        """按长度过滤"""
        length = len(content)
        return self.min_length <= length <= self.max_length
    
    def extract_summary(self, content: str, max_length: int = 200) -> str:
        """提取摘要"""
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        if len(content) <= max_length:
            return content
        
        # 截断到最后一个完整句
        summary = content[:max_length]
        last_period = max(summary.rfind('。'), summary.rfind('.'), summary.rfind('!'), summary.rfind('？'))
        
        if last_period > max_length * 0.5:
            return summary[:last_period + 1]
        
        return summary + '...'
    
    def keyword_filter(self, content: str, required_keywords: List[str] = None,
                       forbidden_keywords: List[str] = None) -> bool:
        """
        关键词过滤
        
        Args:
            content: 内容
            required_keywords: 必须包含的关键词
            forbidden_keywords: 禁止包含的关键词
            
        Returns:
            是否通过过滤
        """
        content_lower = content.lower()
        
        # 检查禁止关键词
        if forbidden_keywords:
            for kw in forbidden_keywords:
                if kw.lower() in content_lower:
                    logger.info(f"Content filtered by forbidden keyword: {kw}")
                    return False
        
        # 检查必需关键词
        if required_keywords:
            for kw in required_keywords:
                if kw.lower() not in content_lower:
                    logger.info(f"Content missing required keyword: {kw}")
                    return False
        
        return True
    
    def process_article(self, article: Dict, options: Dict = None) -> Optional[Dict]:
        """
        处理单篇文章
        
        Args:
            article: 原始文章数据
            options: 处理选项
            
        Returns:
            处理后的文章，None 表示被过滤
        """
        options = options or {}
        
        # 检查必填字段
        if not article.get('title') or not article.get('content'):
            logger.warning("Article missing title or content")
            return None
        
        content = article['content']
        
        # 长度过滤
        if not self.filter_by_length(content):
            logger.warning(f"Article length out of range: {len(content)}")
            return None
        
        # 关键词过滤
        required = options.get('required_keywords')
        forbidden = options.get('forbidden_keywords')
        if not self.keyword_filter(content, required, forbidden):
            return None
        
        # 提取摘要
        article['summary'] = self.extract_summary(content)
        
        # 计算指纹
        article['content_hash'] = self.calculate_hash(content)
        
        return article
    
    def batch_process(self, articles: List[Dict], options: Dict = None) -> List[Dict]:
        """
        批量处理文章
        
        Args:
            articles: 文章列表
            options: 处理选项
            
        Returns:
            处理后的文章列表
        """
        processed = []
        known_hashes = set()
        
        for article in articles:
            result = self.process_article(article, options)
            if result:
                # 去重
                if not self.is_duplicate(result['content'], known_hashes):
                    known_hashes.add(result['content_hash'])
                    processed.append(result)
        
        logger.info(f"Processed {len(articles)} articles, {len(processed)} passed")
        return processed


if __name__ == '__main__':
    # 测试
    processor = ContentProcessor()
    
    test_article = {
        'title': '测试文章',
        'content': '这是一篇测试文章内容。' * 50,
        'link': 'https://example.com/test'
    }
    
    result = processor.process_article(test_article)
    print(f"Processed: {result is not None}")
    if result:
        print(f"Summary: {result['summary'][:100]}...")
        print(f"Hash: {result['content_hash']}")
