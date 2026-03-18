"""敏感词过滤器"""
import re
from typing import List, Set, Optional
from pathlib import Path

from ..logger import processor_log


class SensitiveWordFilter:
    """敏感词过滤器"""

    def __init__(self, word_list: List[str] = None, dict_path: str = None):
        self.words: Set[str] = set()
        self._pattern = None
        
        if word_list:
            self.load_words(word_list)
        elif dict_path:
            self.load_from_file(dict_path)
        else:
            # 默认敏感词列表（示例）
            self.load_default_words()

    def load_words(self, words: List[str]):
        """加载敏感词列表"""
        self.words = set(words)
        self._build_pattern()
        processor_log.info(f"加载 {len(self.words)} 个敏感词")

    def load_from_file(self, file_path: str):
        """从文件加载敏感词"""
        path = Path(file_path)
        if not path.exists():
            processor_log.warning(f"敏感词文件不存在: {file_path}")
            return
        
        words = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word and not word.startswith('#'):
                    words.append(word)
        
        self.load_words(words)

    def load_default_words(self):
        """加载默认敏感词（示例列表，实际使用请替换）"""
        # 这是一个示例列表，实际应该从配置文件或数据库加载
        default_words = [
            "政治敏感词1", "政治敏感词2",
            "违规词1", "违规词2",
        ]
        self.load_words(default_words)

    def _build_pattern(self):
        """构建匹配模式"""
        if not self.words:
            self._pattern = None
            return
        
        # 按长度排序，优先匹配长词
        sorted_words = sorted(self.words, key=len, reverse=True)
        pattern = '|'.join(re.escape(w) for w in sorted_words)
        self._pattern = re.compile(pattern)

    def filter(self, text: str, replace_char: str = '*') -> str:
        """过滤敏感词"""
        if not self._pattern or not text:
            return text
        
        def replace_func(match):
            word = match.group()
            return replace_char * len(word)
        
        return self._pattern.sub(replace_func, text)

    def contains(self, text: str) -> bool:
        """检查是否包含敏感词"""
        if not self._pattern or not text:
            return False
        return bool(self._pattern.search(text))

    def find_all(self, text: str) -> List[str]:
        """查找所有敏感词"""
        if not self._pattern or not text:
            return []
        return self._pattern.findall(text)

    def add_word(self, word: str):
        """添加敏感词"""
        self.words.add(word)
        self._build_pattern()

    def remove_word(self, word: str):
        """移除敏感词"""
        self.words.discard(word)
        self._build_pattern()


# 全局过滤器实例（可配置）
_filter = None

def get_filter(config: dict = None) -> SensitiveWordFilter:
    """获取全局过滤器"""
    global _filter
    if _filter is None:
        word_list = config.get('sensitive_words', []) if config else []
        dict_path = config.get('sensitive_words_file') if config else None
        _filter = SensitiveWordFilter(word_list, dict_path)
    return _filter
