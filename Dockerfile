# Docker 配置

## 构建镜像

```bash
docker build -t auto-content-publisher .
```

## 运行容器

```bash
# 运行 API 服务
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  --name auto-content-publisher \
  auto-content-publisher
```

## Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```
