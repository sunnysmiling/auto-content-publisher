"""
测试配置模块
"""
import pytest
import os
import sys

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config


class TestConfig:
    """测试配置模块"""
    
    def test_config_load(self):
        """测试配置加载"""
        config = Config('config/settings.yaml')
        assert config is not None
    
    def test_config_get(self):
        """测试配置获取"""
        config = Config('config/settings.yaml')
        # 测试获取不存在的键
        result = config.get('nonexistent_key')
        assert result is None
    
    def test_config_get_with_default(self):
        """测试带默认值的配置获取"""
        config = Config('config/settings.yaml')
        result = config.get('nonexistent_key', 'default_value')
        assert result == 'default_value'
    
    def test_config_file_exists(self):
        """测试配置文件存在"""
        config_path = 'config/settings.yaml'
        assert os.path.exists(config_path), f"配置文件 {config_path} 不存在"
