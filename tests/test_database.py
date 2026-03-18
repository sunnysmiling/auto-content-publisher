"""测试数据库模块"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import Database


class TestDatabase:
    """测试数据库功能"""

    @pytest.fixture
    def db(self, tmp_path):
        """创建临时数据库"""
        db_path = tmp_path / "test.db"
        return Database(str(db_path))

    def test_add_source(self, db):
        """测试添加数据源"""
        source_id = db.add_source(
            name="测试源",
            url="https://example.com/feed.xml",
            source_type="rss",
            crawl_interval=60
        )
        assert source_id > 0

        sources = db.get_sources()
        assert len(sources) == 1
        assert sources[0]['name'] == "测试源"

    def test_add_article(self, db):
        """测试添加文章"""
        # 先添加数据源
        source_id = db.add_source(
            name="测试源",
            url="https://example.com/feed.xml",
            source_type="rss"
        )

        # 添加文章
        article_id = db.add_article(
            source_id=source_id,
            source_url="https://example.com/article/1",
            title="测试文章",
            content="测试内容"
        )
        assert article_id > 0

    def test_article_exists(self, db):
        """测试文章重复检查"""
        source_id = db.add_source(
            name="测试源",
            url="https://example.com/feed.xml",
            source_type="rss"
        )

        url = "https://example.com/article/1"
        db.add_article(source_id, url, "测试", "内容")

        assert db.article_exists(url) is True
        assert db.article_exists("https://not-exist.com") is False

    def test_update_article(self, db):
        """测试更新文章"""
        source_id = db.add_source(
            name="测试源",
            url="https://example.com/feed.xml",
            source_type="rss"
        )

        article_id = db.add_article(
            source_id, 
            "https://example.com/1",
            "原标题",
            "原内容"
        )

        db.update_article(
            article_id,
            processed_title="新标题",
            summary="新摘要"
        )

        article = db.get_article(article_id)
        assert article['processed_title'] == "新标题"
        assert article['summary'] == "新摘要"

    def test_mark_published(self, db):
        """测试标记发布状态"""
        source_id = db.add_source(name="测试", url="http://test.com", source_type="rss")
        article_id = db.add_article(source_id, "http://test.com/1", "标题", "内容")

        db.mark_published(article_id)
        article = db.get_article(article_id)
        
        assert article['status'] == 'published'
        assert article['published_at'] is not None

    def test_get_articles_by_status(self, db):
        """测试按状态获取文章"""
        source_id = db.add_source(name="测试", url="http://test.com", source_type="rss")
        
        # 添加不同状态的测试数据
        aid1 = db.add_article(source_id, "http://test.com/1", "文章1", "内容1")
        aid2 = db.add_article(source_id, "http://test.com/2", "文章2", "内容2")
        
        db.mark_published(aid1)
        
        pending = db.get_articles(status='pending')
        assert len(pending) == 1
        
        published = db.get_articles(status='published')
        assert len(published) == 1

    def test_delete_source(self, db):
        """测试删除数据源"""
        source_id = db.add_source(
            name="测试源",
            url="https://example.com/feed.xml",
            source_type="rss"
        )
        
        db.delete_source(source_id)
        sources = db.get_sources()
        assert len(sources) == 0
