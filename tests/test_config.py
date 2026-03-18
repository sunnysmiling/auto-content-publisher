"""测试配置模块"""
import pytest
import tempfile
import yaml
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestConfig:
    """测试配置功能"""

    def test_config_class_exists(self):
        """测试配置类存在"""
        from src.config import Config
        assert Config is not None

    def test_config_init(self, tmp_path, monkeypatch):
        """测试配置初始化"""
        # 创建临时配置
        config_data = {
            'database': {'path': 'test.db'},
            'crawler': {'interval': 60, 'timeout': 15},
            'ai': {'model': 'gpt-4'},
        }
        
        config_file = tmp_path / "settings.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # 切换工作目录
        monkeypatch.chdir(tmp_path)
        
        from src.config import Config
        config = Config(str(config_file))
        
        assert config.get('crawler.interval') == 60

    def test_get_nested_value(self):
        """测试嵌套值获取"""
        from src.config import Config
        
        config = Config.__new__(Config)
        config._config = {
            'database': {'path': 'test.db'},
            'ai': {'api_key': 'key', 'model': 'gpt-4'}
        }
        
        assert config.get('database.path') == 'test.db'
        assert config.get('ai.model') == 'gpt-4'
        assert config.get('not.exist', 'default') == 'default'

    def test_default_values(self):
        """测试默认值"""
        from src.config import Config
        
        config = Config.__new__(Config)
        config._config = {}
        
        assert config.get('crawler.interval', 120) == 120
