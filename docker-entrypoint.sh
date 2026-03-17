#!/bin/bash
set -e

echo "Starting Auto Content Publisher..."

# 初始化数据库
echo "Initializing database..."
python -c "from src.database import Database; Database({'path': 'data/content.db'}).init_db()"

# 启动应用
exec python src/main.py "$@"
