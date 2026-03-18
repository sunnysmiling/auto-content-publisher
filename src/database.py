"""数据库模块"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

from .config import config


class Database:
    """数据库管理类"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _cursor(self):
        """上下文管理器：自动提交/回滚"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_db(self):
        """初始化数据库表"""
        with self._cursor() as cursor:
            # Sources 表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('rss', 'http')),
                    enabled INTEGER DEFAULT 1,
                    crawl_interval INTEGER DEFAULT 120,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Articles 表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER,
                    source_url TEXT NOT NULL,
                    original_title TEXT,
                    original_content TEXT,
                    processed_title TEXT,
                    processed_content TEXT,
                    summary TEXT,
                    cover_image TEXT,
                    status TEXT DEFAULT 'pending' 
                        CHECK(status IN ('pending', 'processing', 'published', 'failed')),
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    published_at TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES sources(id),
                    UNIQUE(source_url)
                )
            ''')

            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_articles_status 
                ON articles(status)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_articles_source_url 
                ON articles(source_url)
            ''')

    # ========== Source CRUD ==========

    def add_source(self, name: str, url: str, source_type: str, 
                   crawl_interval: int = 120, enabled: bool = True) -> int:
        """添加数据源"""
        with self._cursor() as cursor:
            cursor.execute('''
                INSERT INTO sources (name, url, type, enabled, crawl_interval)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, url, source_type, 1 if enabled else 0, crawl_interval))
            return cursor.lastrowid

    def get_sources(self, enabled_only: bool = False) -> List[Dict]:
        """获取数据源列表"""
        with self._cursor() as cursor:
            sql = 'SELECT * FROM sources'
            if enabled_only:
                sql += ' WHERE enabled = 1'
            cursor.execute(sql)
            return [dict(row) for row in cursor.fetchall()]

    def update_source(self, source_id: int, **kwargs):
        """更新数据源"""
        fields = ', '.join(f'{k} = ?' for k in kwargs.keys())
        values = list(kwargs.values()) + [source_id]
        with self._cursor() as cursor:
            cursor.execute(f'UPDATE sources SET {fields} WHERE id = ?', values)

    def delete_source(self, source_id: int):
        """删除数据源"""
        with self._cursor() as cursor:
            cursor.execute('DELETE FROM sources WHERE id = ?', (source_id,))

    # ========== Article CRUD ==========

    def add_article(self, source_id: Optional[int], source_url: str,
                    title: str = '', content: str = '') -> int:
        """添加文章"""
        with self._cursor() as cursor:
            cursor.execute('''
                INSERT OR IGNORE INTO articles 
                (source_id, source_url, original_title, original_content, status)
                VALUES (?, ?, ?, ?, 'pending')
            ''', (source_id, source_url, title, content))
            return cursor.lastrowid

    def get_article(self, article_id: int) -> Optional[Dict]:
        """获取单篇文章"""
        with self._cursor() as cursor:
            cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_articles(self, status: Optional[str] = None, 
                     limit: int = 100) -> List[Dict]:
        """获取文章列表"""
        with self._cursor() as cursor:
            sql = 'SELECT * FROM articles'
            params = []
            if status:
                sql += ' WHERE status = ?'
                params.append(status)
            sql += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def update_article(self, article_id: int, **kwargs):
        """更新文章"""
        if not kwargs:
            return
        fields = ', '.join(f'{k} = ?' for k in kwargs.keys())
        values = list(kwargs.values()) + [article_id]
        with self._cursor() as cursor:
            cursor.execute(f'UPDATE articles SET {fields} WHERE id = ?', values)

    def delete_article(self, article_id: int):
        """删除文章"""
        with self._cursor() as cursor:
            cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))

    def article_exists(self, source_url: str) -> bool:
        """检查文章是否已存在"""
        with self._cursor() as cursor:
            cursor.execute(
                'SELECT 1 FROM articles WHERE source_url = ?', 
                (source_url,)
            )
            return cursor.fetchone() is not None

    def mark_processing(self, article_id: int):
        """标记文章为处理中"""
        self.update_article(article_id, status='processing')

    def mark_published(self, article_id: int):
        """标记文章为已发布"""
        self.update_article(
            article_id, 
            status='published',
            published_at=datetime.now().isoformat()
        )

    def mark_failed(self, article_id: int, error: str):
        """标记文章为失败"""
        self.update_article(
            article_id,
            status='failed',
            error_message=error
        )


# 全局数据库实例
db = Database()
