"""
测试数据库模块
"""
import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database


class TestDatabase:
    """测试数据库模块"""
    
    def test_database_init(self):
        """测试数据库初始化"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False):
            db = Database({'path': ':memory:'})
            assert db is not None
    
    def test_database_tables(self):
        """测试数据库表创建"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False):
            db = Database({'path': ':memory:'})
            db.init_db()
            # 验证表已创建
            conn = db.conn
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert 'feeds' in tables or 'articles' in tables
    
    def test_save_article(self):
        """测试保存文章"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False):
            db = Database({'path': ':memory:'})
            db.init_db()
            
            article = {
                'title': '测试文章',
                'content': '测试内容',
                'url': 'https://example.com',
                'source': 'test'
            }
            # 保存文章
            db.save_article(article)
    
    def test_get_articles(self):
        """测试获取文章列表"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False):
            db = Database({'path': ':memory:'})
            db.init_db()
            
            articles = db.get_articles(limit=10)
            assert isinstance(articles, list)
