"""端到端测试 - 完整流程"""
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestE2E:
    """端到端测试"""

    @pytest.fixture
    def setup_env(self, tmp_path, monkeypatch):
        """设置测试环境"""
        # 使用临时目录
        db_path = tmp_path / "test.db"
        
        # Mock 配置
        import src.config
        monkeypatch.setattr(src.config.config, 'db_path', str(db_path))
        monkeypatch.setattr(src.config.config, 'crawl_interval', 60)
        monkeypatch.setattr(src.config.config, 'ai_api_key', 'test-key')
        
        return tmp_path

    def test_full_pipeline(self, tmp_path, monkeypatch):
        """测试完整流程：采集 -> 处理 -> 发布"""
        # 设置临时数据库
        db_path = tmp_path / "test.db"
        
        # 导入并初始化
        from src.database import Database
        from src.scraper import Crawler
        from src.processor import Processor
        from src.publisher import Publisher
        
        # 创建数据库
        db = Database(str(db_path))
        
        # 1. 添加数据源
        source_id = db.add_source(
            name="36氪",
            url="https://www.36kr.com/feed/",
            source_type="rss"
        )
        assert source_id > 0
        
        # 2. 模拟采集（不实际请求）
        # 由于实际采集需要网络，这里测试数据库层面的流程
        articles = db.get_articles()
        assert isinstance(articles, list)
        
        # 3. 添加测试文章
        article_id = db.add_article(
            source_id=source_id,
            source_url="https://example.com/test-article",
            title="测试文章标题",
            content="这是测试文章的内容，包含一些实际内容用于测试。"
        )
        
        # 验证文章状态
        article = db.get_article(article_id)
        assert article['status'] == 'pending'
        assert article['original_title'] == "测试文章标题"
        
        # 4. 标记为处理中
        db.mark_processing(article_id)
        article = db.get_article(article_id)
        assert article['status'] == 'processing'
        
        # 5. 模拟处理完成
        db.update_article(
            article_id,
            processed_title="【重写】测试文章标题",
            processed_content="这是处理后的内容。",
            summary="这是一句话摘要",
            processed_at="2024-01-01T00:00:00"
        )
        
        # 6. 标记发布
        db.mark_published(article_id)
        article = db.get_article(article_id)
        assert article['status'] == 'published'
        assert article['published_at'] is not None
        
        print("✓ 端到端流程测试通过")

    def test_error_handling(self, tmp_path):
        """测试错误处理"""
        from src.database import Database
        
        db = Database(str(tmp_path / "test.db"))
        
        # 测试获取不存在的文章
        article = db.get_article(9999)
        assert article is None
        
        # 测试删除不存在的数据源
        db.delete_source(9999)  # 不应该抛出异常
        
        print("✓ 错误处理测试通过")

    def test_article_status_flow(self, tmp_path):
        """测试文章状态流转"""
        from src.database import Database
        
        db = Database(str(tmp_path / "test.db"))
        
        source_id = db.add_source(name="测试", url="http://test.com", source_type="rss")
        article_id = db.add_article(source_id, "http://test.com/1", "标题", "内容")
        
        # pending -> processing -> published
        assert db.get_article(article_id)['status'] == 'pending'
        
        db.mark_processing(article_id)
        assert db.get_article(article_id)['status'] == 'processing'
        
        db.mark_published(article_id)
        assert db.get_article(article_id)['status'] == 'published'
        
        # 测试失败状态
        article_id2 = db.add_article(source_id, "http://test.com/2", "标题2", "内容2")
        db.mark_failed(article_id2, "测试错误")
        assert db.get_article(article_id2)['status'] == 'failed'
        
        print("✓ 状态流转测试通过")
