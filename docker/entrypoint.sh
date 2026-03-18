#!/bin/bash
set -e

echo "========================================="
echo "  Auto Content Publisher 启动中..."
echo "========================================="

# 等待数据库就绪
echo "等待数据库初始化..."
sleep 2

# 检查配置文件
if [ -f "$CONFIG_PATH" ]; then
    echo "✓ 配置文件已找到: $CONFIG_PATH"
else
    echo "⚠ 配置文件不存在，使用默认配置"
fi

# 检查必要的环境变量
if [ -z "$DATABASE_PATH" ]; then
    export DATABASE_PATH=/app/data/content.db
    echo "✓ 使用默认数据库路径: $DATABASE_PATH"
fi

# 启动应用
echo "========================================="
echo "  启动服务..."
echo "========================================="

# 根据环境变量选择运行模式
if [ "$MODE" = "scheduler" ]; then
    echo "运行模式: 定时调度器"
    exec python -m src.scheduler.scheduler
elif [ "$MODE" = "server" ]; then
    echo "运行模式: Web 服务器"
    exec uvicorn main:app --host 0.0.0.0 --port 8080
else
    # 默认模式：同时运行调度器和服务
    echo "运行模式: 完整模式 (调度器 + API)"
    # 后台运行调度器
    python -m src.scheduler.scheduler &
    # 前台运行 Web 服务
    exec uvicorn main:app --host 0.0.0.0 --port 8080
fi
