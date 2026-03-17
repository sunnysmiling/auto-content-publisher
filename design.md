# Auto Content Publisher - 设计文档 (design.md)

## 1. 系统架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Auto Content Publisher                 │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │   Scheduler  │   │   Scheduler  │   │   Scheduler  │    │
│  │  (采集任务)   │   │  (处理任务)   │   │  (发布任务)   │    │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘    │
│         │                  │                  │            │
│  ┌──────┴──────────────────┴──────────────────┴──────┐    │
│  │                    Task Queue                       │    │
│  │              (APScheduler Job Store)                │    │
│  └──────────────────────┬─────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───┴────┐          ┌─────┴────┐          ┌─────┴────┐
│Scraper │          │  AI      │          │ Publisher│
│  Module│          │  Processor│         │  Module  │
└────────┘          └───────────┘          └──────────┘
    │                     │                     │
    ▼                     ▼                     ▼
┌────────┐          ┌───────────┐          ┌──────────┐
│  数据源 │          │  GPT API  │          │  公众号   │
│ (RSS/Web)         │           │          │   API    │
└────────┘          └───────────┘          └──────────┘
```

### 1.2 目录结构

```
auto-content-publisher/
├── src/
│   ├── __init__.py
│   ├── main.py                 # 入口文件
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库操作
│   │
│   ├── scraper/                # 采集模块
│   │   ├── __init__.py
│   │   ├── base.py             # 采集基类
│   │   ├── rss_scraper.py      # RSS 采集
│   │   └── http_scraper.py     # HTTP 网页采集
│   │
│   ├── processor/              # 内容处理模块
│   │   ├── __init__.py
│   │   ├── base.py             # 处理基类
│   │   ├── rewriter.py         # AI 改写
│   │   ├── summarizer.py       # 摘要生成
│   │   └── filter.py           # 敏感词过滤
│   │
│   ├── publisher/              # 发布模块
│   │   ├── __init__.py
│   │   ├── base.py             # 发布基类
│   │   └── wechat.py           # 公众号发布
│   │
│   └── scheduler/              # 调度模块
│       ├── __init__.py
│       └── jobs.py             # 定时任务
│
├── data/                       # 数据存储
│   ├── database.db             # SQLite 数据库
│   ├── logs/                   # 日志目录
│   └── cache/                  # 缓存目录
│
├── config/
│   └── settings.yaml           # 配置文件
│
├── tests/                      # 测试目录
│
├── requirements.txt            # Python 依赖
├── .env                        # 环境变量 (API keys)
└── README.md                   # 项目说明
```

---

## 2. 核心模块设计

### 2.1 配置管理 (config.py)

```python
# 配置结构
class Config:
    # 数据库
    DB_PATH: str = "data/database.db"
    
    # 采集配置
    CRAWL_INTERVAL: int = 120  # 分钟
    CRAWL_TIMEOUT: int = 30
    
    # AI 处理
    AI_PROVIDER: str = "openai"  # openai / anthropic / custom
    AI_API_KEY: str
    AI_MODEL: str = "gpt-4"
    AI_TEMPERATURE: float = 0.7
    
    # 公众号
    WECHAT_APP_ID: str
    WECHAT_APP_SECRET: str
    
    # 定时任务
    PUBLISH_TIMES: list = ["08:00", "12:00", "20:00"]
```

### 2.2 数据库设计 (database.py)

使用 SQLite + SQLAlchemy：

```python
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    source_url = Column(Text, nullable=False)
    source_name = Column(String(100))
    
    original_title = Column(String(500))
    original_content = Column(Text)
    
    processed_title = Column(String(500))
    processed_content = Column(Text)
    summary = Column(Text)
    
    cover_image = Column(String(500))  # 封面图 URL
    
    status = Column(String(20), default='pending')  # pending/processing/published/failed
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    published_at = Column(DateTime, nullable=True)

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    url = Column(Text, nullable=False)
    type = Column(String(20))  # rss / http
    enabled = Column(Boolean, default=True)
    crawl_interval = Column(Integer, default=120)
    last_crawl_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
```

### 2.3 采集模块 (scraper/)

#### 基类 (base.py)

```python
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    @abstractmethod
    def fetch(self, source: Source) -> List[Dict]:
        """获取文章列表"""
        pass
    
    @abstractmethod
    def fetch_content(self, url: str) -> Dict:
        """获取单篇文章详细内容"""
        pass
```

#### RSS 采集 (rss_scraper.py)

```python
import feedparser
from bs4 import BeautifulSoup

class RSSScraper(BaseScraper):
    def fetch(self, source: Source) -> List[Dict]:
        feed = feedparser.parse(source.url)
        articles = []
        for entry in feed.entries[:10]:  # 取最新10条
            articles.append({
                'title': entry.get('title', ''),
                'url': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', ''),
            })
        return articles
    
    def fetch_content(self, url: str) -> Dict:
        # RSS 一般不包含全文，需要用 HTTP 采集补充
        pass
```

#### HTTP 采集 (http_scraper.py)

```python
import requests
from bs4 import BeautifulSoup

class HTTPScraper(BaseScraper):
    def fetch(self, source: Source) -> List[Dict]:
        # 列表页采集逻辑
        pass
    
    def fetch_content(self, url: str) -> Dict:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取正文（需针对不同网站配置 selector）
        content = soup.select_one('article, .content, #article-content')
        
        return {
            'title': soup.title.string,
            'content': content.get_text(strip=True) if content else '',
            'images': [img['src'] for img in soup.select('article img')],
        }
```

### 2.4 内容处理模块 (processor/)

#### AI 改写 (rewriter.py)

```python
import openai
from typing import Dict

class AIRewriter:
    def __init__(self, config: Config):
        openai.api_key = config.AI_API_KEY
        self.model = config.AI_MODEL
    
    def rewrite(self, article: Article) -> Article:
        prompt = f"""请将以下文章进行伪原创改写，要求：
1. 保持核心意思不变
2. 更换表达方式和句式
3. 适当调整段落结构
4. 增加个人风格

原文标题：{article.original_title}
原文内容：{article.original_content}

请返回 JSON 格式：
{{
    "title": "改写后的标题",
    "content": "改写后的内容"
}}
"""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        
        result = json.loads(response.choices[0].message.content)
        article.processed_title = result['title']
        article.processed_content = result['content']
        
        return article
```

#### 敏感词过滤 (filter.py)

```python
import re

class ContentFilter:
    SENSITIVE_WORDS = []  # 可从文件加载
    
    def __init__(self):
        # 加载敏感词库
        self.sensitive_words = self._load_words()
    
    def check(self, text: str) -> bool:
        """返回是否包含敏感词"""
        for word in self.sensitive_words:
            if word in text:
                return True
        return False
    
    def filter(self, text: str) -> str:
        """过滤敏感词，替换为 * """
        for word in self.sensitive_words:
            text = text.replace(word, '*' * len(word))
        return text
```

### 2.5 发布模块 (publisher/)

#### 公众号发布 (wechat.py)

```python
import requests
from datetime import datetime

class WeChatPublisher:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
    
    def get_access_token(self) -> str:
        """获取 access_token"""
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        resp = requests.get(url).json()
        return resp['access_token']
    
    def create_draft(self, article: Article) -> int:
        """创建草稿箱"""
        token = self.get_access_token()
        
        # 上传图文消息素材
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        
        articles = [{
            "title": article.processed_title,
            "author": "Auto Publisher",
            "content": article.processed_content,
            "digest": article.summary[:120],
            "content_source_url": article.source_url,
            "thumb_media_id": "",  # 需要先上传封面图获取 media_id
        }]
        
        resp = requests.post(url, json={"articles": articles}).json()
        
        if 'media_id' in resp:
            return resp['media_id']
        else:
            raise Exception(f"创建草稿失败: {resp}")
    
    def publish(self, media_id: int) -> bool:
        """发布草稿"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}"
        
        resp = requests.post(url, json={"media_id": media_id}).json()
        return resp.get('errcode') == 0
```

### 2.6 调度模块 (scheduler/)

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class TaskScheduler:
    def __init__(self, config: Config):
        self.scheduler = BackgroundScheduler()
        self.config = config
    
    def start(self):
        # 采集任务 - 每 2 小时
        self.scheduler.add_job(
            self.crawl_task,
            'interval',
            minutes=self.config.CRAWL_INTERVAL,
            id='crawl'
        )
        
        # 发布任务 - 每天指定时间
        for time_str in self.config.PUBLISH_TIMES:
            hour, minute = map(int, time_str.split(':'))
            self.scheduler.add_job(
                self.publish_task,
                'cron',
                hour=hour,
                minute=minute,
                id=f'publish_{time_str}'
            )
        
        self.scheduler.start()
    
    def crawl_task(self):
        """采集任务"""
        pass
    
    def publish_task(self):
        """发布任务"""
        pass
```

---

## 3. 数据流

```
数据源 (RSS/HTTP)
    │
    ▼
Scraper.fetch() ──▶ 数据库 (Article.pending)
    │
    ▼
Processor.rewrite() ──▶ 数据库 (Article.processing)
    │
    ▼
Processor.summarize() ──▶ 数据库 (Article.ready)
    │
    ▼
Publisher.publish() ──▶ 公众号草稿箱
    │
    ▼
数据库 (Article.published)
```

---

## 4. 异常处理

| 场景 | 处理策略 |
|------|----------|
| 采集失败 | 重试 3 次，间隔 5 分钟，记录日志 |
| AI 处理失败 | 标记 status=failed，记录错误，人工处理 |
| 发布失败 | 记录错误，保留草稿，发钉钉/邮件通知 |
| API 限流 | 指数退避，暂停后继续 |

---

## 5. 配置示例 (config/settings.yaml)

```yaml
database:
  path: "data/database.db"

crawler:
  interval: 120  # 分钟
  timeout: 30
  retry_times: 3

ai:
  provider: "openai"
  api_key: "${AI_API_KEY}"
  model: "gpt-4"
  temperature: 0.7

wechat:
  app_id: "${WECHAT_APP_ID}"
  app_secret: "${WECHAT_APP_SECRET}"

scheduler:
  publish_times:
    - "08:00"
    - "12:00"
    - "20:00"

sources:
  - name: "科技前沿"
    url: "https://example.com/feed.xml"
    type: "rss"
    enabled: true
  - name: "商业洞察"
    url: "https://business.example.com/articles"
    type: "http"
    enabled: true
```

---

**文档版本**: v0.1  
**创建日期**: 2026-03-17
