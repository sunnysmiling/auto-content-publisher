"""配置管理模块"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """配置类"""

    def __init__(self, config_file: str = "config/settings.yaml"):
        self.base_dir = Path(__file__).parent.parent
        self.config_file = self.base_dir / config_file
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}

        # 从环境变量覆盖配置
        self._load_env_vars()

    def _load_env_vars(self):
        """加载环境变量到配置"""
        env_mappings = {
            'AI_API_KEY': ('ai', 'api_key'),
            'WECHAT_APP_ID': ('wechat', 'app_id'),
            'WECHAT_APP_SECRET': ('wechat', 'app_secret'),
        }

        for env_key, (section, key) in env_mappings.items():
            value = os.getenv(env_key)
            if value:
                if section not in self._config:
                    self._config[section] = {}
                self._config[section][key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项，支持点分隔的键名"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    @property
    def db_path(self) -> str:
        """数据库路径"""
        return str(self.base_dir / self.get('database.path', 'data/database.db'))

    @property
    def crawl_interval(self) -> int:
        """采集间隔（分钟）"""
        return self.get('crawler.interval', 120)

    @property
    def crawl_timeout(self) -> int:
        """采集超时（秒）"""
        return self.get('crawler.timeout', 30)

    @property
    def ai_api_key(self) -> str:
        """AI API Key"""
        return self.get('ai.api_key', '')

    @property
    def ai_model(self) -> str:
        """AI 模型"""
        return self.get('ai.model', 'gpt-4')

    @property
    def ai_temperature(self) -> float:
        """AI 温度"""
        return self.get('ai.temperature', 0.7)

    @property
    def wechat_app_id(self) -> str:
        """微信 App ID"""
        return self.get('wechat.app_id', '')

    @property
    def wechat_app_secret(self) -> str:
        """微信 App Secret"""
        return self.get('wechat.app_secret', '')

    @property
    def publish_times(self) -> List[str]:
        """发布时间列表"""
        return self.get('scheduler.publish_times', ['08:00', '12:00', '20:00'])

    @property
    def sources(self) -> List[Dict]:
        """数据源列表"""
        return self.get('sources', [])


# 全局配置实例
config = Config()
