"""
单元测试
"""
import unittest
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scraper import RSSScraper, WebScraper
from processor import ContentProcessor
from scheduler import TaskScheduler


class TestRSSScraper(unittest.TestCase):
    """测试 RSS 采集器"""
    
    def test_scraper_init(self):
        """测试初始化"""
        scraper = RSSScraper()
        self.assertIsNotNone(scraper)
        self.assertEqual(scraper.timeout, 30)


class TestContentProcessor(unittest.TestCase):
    """测试内容处理器"""
    
    def test_processor_init(self):
        """测试初始化"""
        processor = ContentProcessor()
        self.assertIsNotNone(processor)
    
    def test_hash_calculation(self):
        """测试哈希计算"""
        processor = ContentProcessor()
        hash1 = processor.calculate_hash("test content")
        hash2 = processor.calculate_hash("test content")
        self.assertEqual(hash1, hash2)
    
    def test_summary_extraction(self):
        """测试摘要提取"""
        processor = ContentProcessor()
        long_text = "这是测试内容。" * 50
        summary = processor.extract_summary(long_text, max_length=50)
        self.assertLessEqual(len(summary), 53)  # 50 + "..."
    
    def test_length_filter(self):
        """测试长度过滤"""
        processor = ContentProcessor()
        
        # 短内容应该被过滤
        self.assertFalse(processor.filter_by_length("短"))
        
        # 正常长度应该通过
        self.assertTrue(processor.filter_by_length("正常内容" * 20))
    
    def test_keyword_filter(self):
        """测试关键词过滤"""
        processor = ContentProcessor()
        
        # 包含必需关键词
        self.assertTrue(processor.keyword_filter(
            "这是一篇关于Python的文章",
            required_keywords=["Python"]
        ))
        
        # 缺少必需关键词
        self.assertFalse(processor.keyword_filter(
            "这是一篇普通的文章",
            required_keywords=["Python"]
        ))
        
        # 包含禁止关键词
        self.assertFalse(processor.keyword_filter(
            "这是一篇广告文章",
            forbidden_keywords=["广告"]
        ))


class TestTaskScheduler(unittest.TestCase):
    """测试任务调度器"""
    
    def test_scheduler_init(self):
        """测试初始化"""
        scheduler = TaskScheduler()
        self.assertIsNotNone(scheduler)
        self.assertEqual(len(scheduler.tasks), 0)
        self.assertFalse(scheduler.running)
    
    def test_add_task(self):
        """测试添加任务"""
        scheduler = TaskScheduler()
        
        def dummy_task():
            return "test"
        
        scheduler.add_task("test_task", dummy_task, "every(1).minutes")
        self.assertEqual(len(scheduler.tasks), 1)
        self.assertIn("test_task", scheduler.tasks)


if __name__ == '__main__':
    unittest.main()
