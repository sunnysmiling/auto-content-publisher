# Auto Content Publisher - 任务清单 (task.md)

## 开发阶段

- [ ] **Phase 1: 基础设施** - 配置管理 + 数据库 + 日志
- [ ] **Phase 2: 采集模块** - RSS + HTTP 采集
- [ ] **Phase 3: 内容处理** - AI 改写 + 敏感词过滤 + 摘要
- [ ] **Phase 4: 发布模块** - 公众号 API 对接
- [ ] **Phase 5: 调度中心** - 定时任务
- [ ] **Phase 6: 集成测试** - 端到端测试

---

## Phase 1: 基础设施

### T1.1 项目初始化

- [ ] 创建 `src/` 目录结构
- [ ] 创建 `config/` 目录
- [ ] 创建 `data/logs/` 目录
- [ ] 创建 `requirements.txt`

```
requirements.txt 内容:
requests
feedparser
beautifulsoup4
sqlalchemy
pyyaml
python-dotenv
apscheduler
openai
```

### T1.2 配置管理

- [ ] 创建 `src/config.py`
  - [ ] 从 `settings.yaml` 加载配置
  - [ ] 从 `.env` 加载敏感配置
  - [ ] 提供 Config 类
- [ ] 创建 `config/settings.yaml` 示例配置

### T1.3 数据库

- [ ] 创建 `src/database.py`
  - [ ] Article 模型
  - [ ] Source 模型
  - [ ] 初始化数据库
  - [ ] CRUD 操作封装

### T1.4 日志

- [ ] 创建 `src/logger.py`
  - [ ] 文件日志 (按天轮转)
  - [ ] 控制台日志
  - [ ] 记录采集、处理、发布各环节日志

---

## Phase 2: 采集模块

### T2.1 采集基类

- [ ] 创建 `src/scraper/__init__.py`
- [ ] 创建 `src/scraper/base.py`
  - [ ] BaseScraper 抽象类

### T2.2 RSS 采集

- [ ] 创建 `src/scraper/rss_scraper.py`
  - [ ] fetch() 方法：获取文章列表
  - [ ] 解析 title, link, published, summary
  - [ ] 支持多个 RSS 源

### T2.3 HTTP 采集

- [ ] 创建 `src/scraper/http_scraper.py`
  - [ ] fetch() 方法：列表页采集
  - [ ] fetch_content() 方法：详情页采集
  - [ ] 可配置 CSS selector

### T2.4 采集调度

- [ ] 创建 `src/scraper/manager.py`
  - [ ] Source 管理：加载启用的数据源
  - [ ] 增量采集：只抓新内容
  - [ ] 重复检测：避免重复入库

---

## Phase 3: 内容处理

### T3.1 处理基类

- [ ] 创建 `src/processor/__init__.py`
- [ ] 创建 `src/processor/base.py`

### T3.2 AI 改写

- [ ] 创建 `src/processor/rewriter.py`
  - [ ] OpenAI API 调用
  - [ ] 改写 prompt 模板
  - [ ] JSON 响应解析
  - [ ] 支持流式输出（可选）

### T3.3 摘要生成

- [ ] 创建 `src/processor/summarizer.py`
  - [ ] 从原文生成摘要
  - [ ] 限制字数 (120-200字)

### T3.4 敏感词过滤

- [ ] 创建 `src/processor/filter.py`
  - [ ] 加载敏感词库
  - [ ] 检测敏感词
  - [ ] 过滤/替换敏感词

### T3.5 封面图处理

- [ ] 创建 `src/processor/image_handler.py`
  - [ ] 从原文提取图片
  - [ ] 下载到本地缓存
  - [ ] 上传到公众号获取 media_id

---

## Phase 4: 发布模块

### T4.1 发布基类

- [ ] 创建 `src/publisher/__init__.py`
- [ ] 创建 `src/publisher/base.py`

### T4.2 公众号 API

- [ ] 创建 `src/publisher/wechat.py`
  - [ ] get_access_token() - 获取调用凭证
  - [ ] upload_image() - 上传图片
  - [ ] create_draft() - 创建草稿
  - [ ] publish_draft() - 发布草稿 (可选)

### T4.3 发布管理

- [ ] 创建 `src/publisher/manager.py`
  - [ ] 选取待发布文章
  - [ ] 状态流转管理
  - [ ] 发布结果回执

---

## Phase 5: 调度中心

### T5.1 调度器

- [ ] 创建 `src/scheduler/__init__.py`
- [ ] 创建 `src/scheduler/jobs.py`
  - [ ] 采集任务 (interval)
  - [ ] 处理任务 (queue 驱动)
  - [ ] 发布任务 (cron)

### T5.2 主程序

- [ ] 创建 `src/main.py`
  - [ ] 初始化配置
  - [ ] 初始化数据库
  - [ ] 启动调度器
  - [ ] 信号处理 (优雅退出)

### T5.3 通知

- [ ] 创建 `src/notify.py`
  - [ ] 钉钉 webhook 通知
  - [ ] 邮件通知 (可选)
  - [ ] 失败告警

---

## Phase 6: 集成测试

### T6.1 单元测试

- [ ] 测试配置加载
- [ ] 测试 RSS 解析
- [ ] 测试数据库 CRUD
- [ ] 测试 AI 改写调用

### T6.2 集成测试

- [ ] 端到端采集测试
- [ ] 端到端处理测试
- [ ] 模拟发布测试

### T6.3 部署

- [ ] 编写 Dockerfile
- [ ] 编写 docker-compose.yml
- [ ] 编写启动脚本

---

## 任务依赖关系

```
T1.1 ──▶ T1.2 ──▶ T1.3 ──▶ T1.4
                    │
                    ▼
T2.1 ──▶ T2.2 ──▶ T2.3 ──▶ T2.4
                              │
                              ▼
T3.1 ──▶ T3.2 ──▶ T3.3 ──▶ T3.4 ──▶ T3.5
                                        │
                                        ▼
T4.1 ──▶ T4.2 ──▶ T4.3
                    │
                    ▼
T5.1 ──▶ T5.2 ──▶ T5.3
     │
     └──────────▶ T6.1 ──▶ T6.2 ──▶ T6.3
```

---

## 快速开始开发

```bash
# 1. 进入项目目录
cd /root/.openclaw/workspace/auto-content-publisher

# 2. 创建虚拟环境 (可选)
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 复制配置
cp config/settings.yaml config/settings.yaml.bak
# 编辑 settings.yaml 填入配置

# 5. 创建 .env 文件
echo "AI_API_KEY=your-key" > .env
echo "WECHAT_APP_ID=your-app-id" >> .env
echo "WECHAT_APP_SECRET=your-secret" >> .env

# 6. 运行
python src/main.py
```

---

**文档版本**: v0.1  
**创建日期**: 2026-03-17
**最后更新**: 2026-03-17
