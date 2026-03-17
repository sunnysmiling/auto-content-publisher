"""
测试处理模块
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from processor import ContentProcessor


class TestContentProcessor:
    """测试内容处理器"""
    
    def test_processor_init(self):
        """测试处理器初始化"""
        processor = ContentProcessor()
        assert processor is not None
    
    def test_calculate_hash(self):
        """测试内容指纹计算"""
        processor = ContentProcessor()
        hash1 = processor.calculate_hash('test content')
        hash2 = processor.calculate_hash('test content')
        hash3 = processor.calculate_hash('different content')
        
        assert hash1 == hash2  # 相同内容应该产生相同指纹
        assert hash1 != hash3  # 不同内容应该产生不同指纹
    
    def test_is_duplicate(self):
        """测试重复检测"""
        processor = ContentProcessor()
        known_hashes = {'abc123', 'def456'}
        
        assert processor.is_duplicate('abc123', known_hashes) == True
        assert processor.is_duplicate('xyz789', known_hashes) == False
    
    def test_filter_by_length(self):
        """测试长度过滤"""
        processor = ContentProcessor()
        
        # 设置最小长度为 10
        processor.min_length = 10
        processor.max_length = 1000
        
        assert processor.filter_by_length('short') == False
        assert processor.filter_by_length('this is a longer content') == True
    
    def test_extract_summary(self):
        """测试摘要提取"""
        processor = ContentProcessor()
        
        # 长内容
        long_content = '这是第一句话。这是第二句话。这是第三句话。' * 10
        
        summary = processor.extract_summary(long_content, max_length=50)
        assert isinstance(summary, str)
        assert len(summary) <= 53  # 50 + '...'
    
    def test_keyword_filter(self):
        """测试关键词过滤"""
        processor = ContentProcessor()
        
        # 测试必需关键词
        assert processor.keyword_filter(
            '这是一篇关于Python的文章',
            required_keywords=['Python']
        ) == True
        
        assert processor.keyword_filter(
            '这是一篇关于Java的文章',
            required_keywords=['Python']
        ) == False
        
        # 测试禁止关键词
        assert processor.keyword_filter(
            '这是一篇包含广告的文章',
            forbidden_keywords=['广告']
        ) == False
        
        assert processor.keyword_filter(
            '这是一篇正常的文章',
            forbidden_keywords=['广告']
        ) == True
    
    def test_process_article(self):
        """测试文章处理"""
        processor = ContentProcessor()
        
        # 有效文章
        article = {
            'title': '测试文章',
            'content': '这是文章内容。' * 20,  # 足够长
            'link': 'https://example.com'
        }
        
        result = processor.process_article(article)
        assert result is not None
        assert 'summary' in result
        assert 'content_hash' in result
    
    def test_process_article_short_content(self):
        """测试文章处理 - 内容过短"""
        processor = ContentProcessor()
        
        article = {
            'title': '测试文章',
            'content': '短',  # 太短
            'link': 'https://example.com'
        }
        
        result = processor.process_article(article)
        assert result is None  # 应该被过滤
    
    def test_batch_process(self):
        """测试批量处理"""
        processor = ContentProcessor()
        
        articles = [
            {
                'title': f'文章{i}',
                'content': '这是文章内容。' * 20,
                'link': f'https://example.com/{i}'
            }
            for i in range(5)
        ]
        
        # 添加一个重复的
        articles.append(articles[0])
        
        results = processor.batch_process(articles)
        assert len(results) <= 5  # 可能有重复被过滤
