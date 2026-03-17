# Auto Content Publisher

全自动内容采集与发布系统

## 功能特性

- **RSS 订阅采集** - 支持 RSS/Atom 格式订阅源
- **网页抓取** - 支持任意网页内容提取
- **内容处理** - 去重、过滤、摘要提取
- **定时调度** - 灵活的任务调度
- **多平台发布** - 微信公众号、博客等

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

编辑 `config/settings.yaml`:

```yaml
rss_feeds:
  - https://example.com/feed.xml

http_urls:
  - https://example.com/blog

wechat:
  app_id: your_app_id
  app_secret: your_app_secret

blog:
  api_url: https://yourblog.com/wp-json
  api_key: your_api_key
```

### 运行

```bash
# API 模式
python src/main.py --mode api

# 调度器模式
python src/main.py --mode scheduler

# 手动采集
python src/main.py --mode fetch
```

## 项目结构

```
auto-content-publisher/
├── config/          # 配置文件
│   └── settings.yaml
├── src/             # 源代码
│   ├── api/         # API 接口
│   ├── scraper/     # 采集模块
│   ├── processor/   # 处理模块
│   ├── scheduler/   # 调度模块
│   ├── publisher/   # 发布模块
│   ├── config.py    # 配置管理
│   ├── database.py  # 数据库
│   ├── logger.py    # 日志
│   └── main.py      # 主程序
├── data/            # 数据目录
├── tests/           # 测试目录
└── requirements.txt # 依赖
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /health | GET | 健康检查 |
| /api/feeds | GET | 获取订阅源 |
| /api/feeds | POST | 添加订阅源 |
| /api/feeds/fetch | POST | 手动采集 |
| /api/articles | GET | 文章列表 |
| /api/publish | POST | 发布文章 |
| /api/scheduler/status | GET | 调度器状态 |

## License

MIT
