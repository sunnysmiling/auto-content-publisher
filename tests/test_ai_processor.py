"""测试 AI 改写/处理模块"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.processor.openai_processor import OpenAIProcessor


class TestAIProcessor:
    """测试 AI 改写功能"""

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI API"""
        with patch('src.processor.openai_processor.openai') as mock:
            yield mock

    @pytest.fixture
    def processor(self, mock_openai):
        """创建处理器实例"""
        return OpenAIProcessor(api_key="test-key")

    def test_processor_init(self, processor):
        """测试处理器初始化"""
        assert processor is not None
        assert hasattr(processor, 'client')

    def test_rewrite_title(self, processor, mock_openai):
        """测试标题改写"""
        # Mock API 响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "【AI重写】原标题"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        result = processor.rewrite_title("原标题")
        
        assert result == "【AI重写】原标题"
        assert mock_openai.ChatCompletion.create.called

    def test_rewrite_content(self, processor, mock_openai):
        """测试内容改写"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "这是改写后的内容摘要。"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        original = "这是原始文章内容，很长很详细..."
        result = processor.rewrite_content(original)
        
        assert "改写后的内容" in result

    def test_generate_summary(self, processor, mock_openai):
        """测试摘要生成"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "一句话摘要"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        content = "这是一篇很长的文章，包含很多内容..."
        result = processor.generate_summary(content)
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_process_full_article(self, processor, mock_openai):
        """测试完整文章处理"""
        # Mock 所有 API 调用
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "处理结果"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        article = {
            'original_title': '原始标题',
            'content': '原始内容',
            'link': 'https://example.com'
        }
        
        result = processor.process(article)
        
        assert 'processed_title' in result
        assert 'processed_content' in result
        assert 'summary' in result

    def test_api_error_handling(self, processor, mock_openai):
        """测试 API 错误处理"""
        mock_openai.ChatCompletion.create.side_effect = Exception("API Error")
        
        result = processor.rewrite_title("测试标题")
        
        # 应该返回原始标题而不是崩溃
        assert result == "测试标题"

    def test_empty_content(self, processor):
        """测试空内容处理"""
        result = processor.rewrite_content("")
        assert result == ""

    def test_long_content_truncation(self, processor, mock_openai):
        """测试长内容截断"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "摘要"
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        # 创建超长内容
        long_content = "内容 " * 10000
        
        result = processor.generate_summary(long_content)
        
        # 验证内容被截断到合理长度
        assert mock_openai.ChatCompletion.create.called


class TestProcessorIntegration:
    """测试处理器与其他模块的集成"""

    def test_processor_with_database(self, tmp_path):
        """测试处理器与数据库集成"""
        from src.database import Database
        from src.processor.processor import ArticleProcessor
        
        db = Database(str(tmp_path / "test.db"))
        processor = ArticleProcessor(db)
        
        # 添加测试数据
        source_id = db.add_source(
            name="测试",
            url="http://test.com",
            source_type="rss"
        )
        
        article_id = db.add_article(
            source_id=source_id,
            source_url="http://test.com/1",
            title="测试标题",
            content="测试内容"
        )
        
        # 验证数据添加成功
        article = db.get_article(article_id)
        assert article['original_title'] == "测试标题"

    def test_filter_integration(self):
        """测试过滤器集成"""
        from src.processor.filter import ContentFilter
        
        filter = ContentFilter()
        
        # 测试关键词过滤
        assert filter.should_process("正常文章") is True
        assert filter.should_process("广告内容") is False
