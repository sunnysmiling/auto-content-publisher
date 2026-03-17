# 数据库模块
import os
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from .config import config

Base = declarative_base()

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    source_url = Column(Text, nullable=False)
    source_name = Column(String(100))
    original_title = Column(String(500))
    original_content = Column(Text)
    original_summary = Column(Text)
    processed_title = Column(String(500))
    processed_content = Column(Text)
    summary = Column(Text)
    cover_image = Column(String(500))
    status = Column(String(20), default='pending')
    error_message = Column(Text)
    wechat_media_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    published_at = Column(DateTime, nullable=True)


class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    url = Column(Text, nullable=False)
    source_type = Column(String(20))
    enabled = Column(Boolean, default=True)
    crawl_interval = Column(Integer, default=120)
    css_selector = Column(String(200))
    last_crawl_at = Column(DateTime, nullable=True)
    last_status = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = config.db_path
        
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def add_article(self, article: Article) -> Article:
        with self.get_session() as session:
            session.add(article)
            session.commit()
            session.refresh(article)
            return article
    
    def get_article_by_url(self, url: str) -> Optional[Article]:
        with self.get_session() as session:
            return session.query(Article).filter(Article.source_url == url).first()
    
    def get_articles_by_status(self, status: str, limit: int = 10) -> List[Article]:
        with self.get_session() as session:
            return session.query(Article).filter(Article.status == status).order_by(Article.created_at.desc()).limit(limit).all()
    
    def update_article(self, article_id: int, **kwargs) -> Optional[Article]:
        with self.get_session() as session:
            article = session.query(Article).filter(Article.id == article_id).first()
            if article:
                for key, value in kwargs.items():
                    if hasattr(article, key):
                        setattr(article, key, value)
                article.updated_at = datetime.now()
                session.commit()
                session.refresh(article)
            return article
    
    def sync_sources_from_config(self, sources: List[dict]):
        with self.get_session() as session:
            for source_config in sources:
                existing = session.query(Source).filter(Source.url == source_config['url']).first()
                if existing:
                    existing.name = source_config.get('name', existing.name)
                    existing.source_type = source_config.get('type', existing.source_type)
                    existing.enabled = source_config.get('enabled', existing.enabled)
                else:
                    source = Source(
                        name=source_config['name'],
                        url=source_config['url'],
                        source_type=source_config.get('type', 'rss'),
                        enabled=source_config.get('enabled', True),
                    )
                    session.add(source)
            session.commit()


db = Database()
