# Auto Content Publisher - 设计文档

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Auto Content Publisher               │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐ │
│  │  RSS    │  │   Web    │  │  API    │  │   CLI    │ │
│  │ Scraper │  │ Scraper  │  │ Server  │  │  Entry   │ │
│  └────┬────┘  └────┬─────┘  └────┬────┘  └────┬─────┘ │
│       │            │             │            │        │
│       └────────────┴──────┬──────┴────────────┘        │
│                           │                             │
│                    ┌──────▼──────┐                     │
│                    │  Processor  │                     │
│                    │ (去重/过滤)  │                     │
│                    └──────┬──────┘                     │
│                           │                             │
│       ┌───────────────────┼───────────────────┐       │
│       │                   │                   │       │
│  ┌────▼────┐        ┌─────▼─────┐       ┌────▼────┐   │
│  │ WeChat  │        │  Database │       │  Blog   │   │
│  │Publisher│        │  (SQLite) │       │Publisher│   │
│  └─────────┘        └───────────┘       └─────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────┐     │
│  │           Task Scheduler (调度器)             │     │
│  └──────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## 模块设计

### 1. 配置模块 (config.py)

```python
class Config:
    def __init__(self, config_path: str)
    def get(self, key: str, default=None)
    def reload()
```

### 2. 数据库模块 (database.py)

```python
class Database:
    def __init__(self, config: dict)
    def init_db()
    def save_article(article: dict)
    def get_articles(limit: int = 100)
    def is_duplicate(content_hash: str) -> bool
```

### 3. 采集模块 (scraper/)

| 类 | 职责 |
|---|------|
| RSSScraper | 解析 RSS/Atom 订阅源 |
| WebScraper | 抓取网页内容，提取文章 |

### 4. 处理模块 (processor/)

```python
class ContentProcessor:
    def process_article(article, options) -> dict
    def batch_process(articles, options) -> list
    def keyword_filter(content, required, forbidden) -> bool
    def extract_summary(content, max_length) -> str
```

### 5. 调度模块 (scheduler/)

```python
class TaskScheduler:
    def add_task(name, func, interval)
    def start(blocking=True)
    def stop()
    def get_status() -> dict
```

### 6. 发布模块 (publisher/)

```python
class WeChatPublisher:
    def publish_article(article) -> bool
    
class BlogPublisher:
    def publish(article) -> bool
```

### 7. API 模块 (api/)

Flask REST API，提供以下端点：
- `GET /health` - 健康检查
- `GET/POST /api/feeds` - 订阅源管理
- `POST /api/feeds/fetch` - 手动采集
- `GET /api/articles` - 文章列表
- `POST /api/publish` - 发布文章
- `GET/POST /api/scheduler/*` - 调度器控制

## 数据模型

### Article 文章

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| title | TEXT | 标题 |
| content | TEXT | 内容 |
| summary | TEXT | 摘要 |
| url | TEXT | 原文链接 |
| source | TEXT | 来源 |
| author | TEXT | 作者 |
| published_at | DATETIME | 发布时间 |
| content_hash | TEXT | 内容指纹 |
| status | TEXT | 状态 (pending/published) |
| created_at | DATETIME | 创建时间 |

### Feed 订阅源

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 名称 |
| url | TEXT | URL |
| type | TEXT | 类型 (rss/http) |
| enabled | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
