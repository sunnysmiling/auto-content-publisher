# 配置管理模块
import os
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent


class Config:
    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = PROJECT_ROOT / "config" / "settings.yaml"
        self._config = self._load_config(config_file)
        self._apply_env_overrides()
    
    def _load_config(self, config_file: Path) -> Dict:
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _apply_env_overrides(self):
        if os.getenv('AI_API_KEY'):
            self._config.setdefault('ai', {})['api_key'] = os.getenv('AI_API_KEY')
        if os.getenv('AI_MODEL'):
            self._config['ai']['model'] = os.getenv('AI_MODEL')
        if os.getenv('WECHAT_APP_ID'):
            self._config.setdefault('wechat', {})['app_id'] = os.getenv('WECHAT_APP_ID')
        if os.getenv('WECHAT_APP_SECRET'):
            self._config.setdefault('wechat', {})['app_secret'] = os.getenv('WECHAT_APP_SECRET')
        if os.getenv('DINGTALK_WEBHOOK'):
            self._config.setdefault('notify', {}).setdefault('dingtalk', {})['webhook'] = os.getenv('DINGTALK_WEBHOOK')
    
    @property
    def db_path(self) -> str:
        db_path = self._config.get('database', {}).get('path', 'data/database.db')
        return str(PROJECT_ROOT / db_path)
    
    @property
    def crawl_interval(self) -> int:
        return self._config.get('crawler', {}).get('interval', 120)
    
    @property
    def crawl_timeout(self) -> int:
        return self._config.get('crawler', {}).get('timeout', 30)
    
    @property
    def ai_api_key(self) -> Optional[str]:
        return self._config.get('ai', {}).get('api_key')
    
    @property
    def ai_model(self) -> str:
        return self._config.get('ai', {}).get('model', 'gpt-4')
    
    @property
    def wechat_app_id(self) -> Optional[str]:
        return self._config.get('wechat', {}).get('app_id')
    
    @property
    def wechat_app_secret(self) -> Optional[str]:
        return self._config.get('wechat', {}).get('app_secret')
    
    @property
    def publish_times(self) -> List[str]:
        return self._config.get('scheduler', {}).get('publish_times', ['08:00', '12:00', '20:00'])
    
    @property
    def sources(self) -> List[Dict[str, Any]]:
        return self._config.get('sources', [])
    
    def get_enabled_sources(self) -> List[Dict[str, Any]]:
        return [s for s in self.sources if s.get('enabled', False)]


config = Config()
