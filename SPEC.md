# Auto Content Publisher - 技术规格文档

## 项目概述

**项目名称**: Auto Content Publisher  
**项目类型**: 全自动内容采集与发布系统  
**版本**: v0.1.0

## 功能规格

### Phase 1: 基础框架

| 模块 | 功能 | 状态 |
|------|------|------|
| config.py | YAML 配置管理 | ✅ |
| database.py | SQLite 数据库模型 | ✅ |
| logger.py | 日志系统 | ✅ |

### Phase 2: 采集模块

| 模块 | 功能 | 状态 |
|------|------|------|
| scraper/rss_scraper.py | RSS/Atom 订阅采集 | ✅ |
| scraper/web_scraper.py | 网页 HTML 抓取 | ✅ |
| processor/content_processor.py | 内容去重、过滤、摘要 | ✅ |
| scheduler/task_scheduler.py | 定时任务调度 | ✅ |
| publisher/wechat_publisher.py | 公众号发布 | ✅ |
| publisher/blog_publisher.py | 博客发布 (WordPress) | ✅ |

### Phase 3: API 与主程序

| 模块 | 功能 | 状态 |
|------|------|------|
| api/__init__.py | Flask REST API | ✅ |
| main.py | 主程序入口 (CLI) | ✅ |

## 技术栈

- Python 3.8+
- Flask (API)
- feedparser (RSS)
- requests + BeautifulSoup (网页抓取)
- schedule (定时任务)
- SQLite (数据库)

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /health | GET | 健康检查 |
| /api/feeds | GET | 订阅源列表 |
| /api/feeds | POST | 添加订阅源 |
| /api/feeds/fetch | POST | 手动采集 |
| /api/articles | GET | 文章列表 |
| /api/publish | POST | 发布文章 |
| /api/scheduler/status | GET | 调度器状态 |
| /api/scheduler/start | POST | 启动调度 |
| /api/scheduler/stop | POST | 停止调度 |

## 运行模式

```bash
# API 模式
python src/main.py --mode api --port 5000

# 调度器模式
python src/main.py --mode scheduler

# 手动采集
python src/main.py --mode fetch

# 手动发布
python src/main.py --mode publish
```
