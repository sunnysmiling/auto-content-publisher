# Auto Content Publisher - 执行步骤文档

## 开发阶段

### Phase 1: 基础框架

**任务清单:**
- [x] 1.1 创建项目目录结构
- [x] 1.2 实现配置管理 (config.py)
- [x] 1.3 实现数据库模型 (database.py)
- [x] 1.4 实现日志系统 (logger.py)
- [x] 1.5 创建配置文件 (config/settings.yaml)
- [x] 1.6 编写 requirements.txt

**完成标准:**
- 配置文件能正常加载
- 数据库表能正常创建
- 日志能正常输出

---

### Phase 2: 采集模块

**任务清单:**
- [x] 2.1 实现 RSS 采集器 (scraper/rss_scraper.py)
  - [x] 支持 RSS 2.0 和 Atom 格式
  - [x] 支持多源批量采集
- [x] 2.2 实现网页抓取器 (scraper/web_scraper.py)
  - [x] 支持自定义 CSS 选择器
  - [x] 支持图片提取
- [x] 2.3 实现内容处理器 (processor/content_processor.py)
  - [x] 内容去重 (MD5 指纹)
  - [x] 关键词过滤
  - [x] 摘要提取
- [x] 2.4 实现任务调度器 (scheduler/task_scheduler.py)
  - [x] 支持定时任务
  - [x] 支持任务管理
- [x] 2.5 实现发布器 (publisher/)
  - [x] 微信公众号发布 (wechat_publisher.py)
  - [x] 博客发布 (blog_publisher.py)

**完成标准:**
- 能采集 RSS 源内容
- 能抓取网页内容
- 能检测重复内容
- 能按关键词过滤
- 能定时执行任务

---

### Phase 3: API 与主程序

**任务清单:**
- [x] 3.1 实现 Flask REST API (api/__init__.py)
  - [x] 订阅源管理接口
  - [x] 采集触发接口
  - [x] 文章查询接口
  - [x] 发布接口
  - [x] 调度器控制接口
- [x] 3.2 实现主程序入口 (main.py)
  - [x] CLI 参数解析
  - [x] 多模式运行 (api/scheduler/fetch/publish)
- [x] 3.3 完善 README 文档
- [x] 3.4 创建 SPEC.md 规格文档
- [x] 3.5 创建 requirements.md 需求文档
- [x] 3.6 创建 design.md 设计文档
- [x] 3.7 创建 task.md 执行文档

**完成标准:**
- API 服务能正常启动
- 各接口能正常工作
- CLI 命令能正常执行

---

## 部署步骤

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/sunnysmiling/auto-content-publisher.git
cd auto-content-publisher

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置

编辑 `config/settings.yaml`:

```yaml
rss_feeds:
  - https://example.com/feed.xml

http_urls:
  - https://example.com/article

wechat:
  app_id: your_app_id
  app_secret: your_app_secret

blog:
  api_url: https://yourblog.com/wp-json
  api_key: your_api_key
```

### 3. 运行

```bash
# 启动 API 服务
python src/main.py --mode api

# 启动定时调度
python src/main.py --mode scheduler

# 手动采集
python src/main.py --mode fetch

# 手动发布
python src/main.py --mode publish
```

### 4. API 调用

```bash
# 健康检查
curl http://localhost:5000/health

# 手动采集
curl -X POST http://localhost:5000/api/feeds/fetch \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com/feed.xml"]}'

# 发布文章
curl -X POST http://localhost:5000/api/publish \
  -H "Content-Type: application/json" \
  -d '{"article": {"title": "Test", "content": "Content"}}'
```

## 维护指南

### 查看日志

```bash
tail -f data/logs/app.log
```

### 备份数据

```bash
cp data/content.db data/content.db.backup
```

### 更新代码

```bash
git pull origin main
pip install -r requirements.txt
```
