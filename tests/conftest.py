"""测试配置"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试配置
TEST_DB_PATH = ":memory:"  # 使用内存数据库
TEST_CONFIG = {
    'database': {'path': TEST_DB_PATH},
    'crawler': {'interval': 60, 'timeout': 10, 'retry_times': 1},
    'ai': {'api_key': 'test-key', 'model': 'gpt-4', 'temperature': 0.7},
    'wechat': {'app_id': 'test_app_id', 'app_secret': 'test_secret'},
}
