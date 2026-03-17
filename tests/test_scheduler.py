"""
测试调度模块
"""
import pytest
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scheduler import TaskScheduler


class TestTaskScheduler:
    """测试任务调度器"""
    
    def test_scheduler_init(self):
        """测试调度器初始化"""
        scheduler = TaskScheduler()
        assert scheduler is not None
        assert scheduler.tasks == {}
        assert scheduler.running == False
    
    def test_add_task(self):
        """测试添加任务"""
        scheduler = TaskScheduler()
        
        def test_func():
            return "test"
        
        scheduler.add_task('test_task', test_func, "every(1).minutes")
        
        assert 'test_task' in scheduler.tasks
        assert scheduler.tasks['test_task']['interval'] == "every(1).minutes"
    
    def test_get_status(self):
        """测试获取状态"""
        scheduler = TaskScheduler()
        
        def test_func():
            return "test"
        
        scheduler.add_task('test_task', test_func, "every(1).minutes")
        
        status = scheduler.get_status()
        
        assert status['running'] == False
        assert status['task_count'] == 1
        assert len(status['tasks']) == 1
        assert status['tasks'][0]['name'] == 'test_task'
    
    def test_run_all(self):
        """测试手动运行所有任务"""
        scheduler = TaskScheduler()
        
        # 使用一个简单的计数器
        counter = {'value': 0}
        
        def increment_task():
            counter['value'] += 1
            return counter['value']
        
        scheduler.add_task('counter_task', increment_task, "every(1).minutes")
        
        # 手动运行一次
        scheduler.run_all()
        
        assert counter['value'] == 1
    
    def test_scheduler_start_stop(self):
        """测试调度器启动停止"""
        scheduler = TaskScheduler()
        
        def dummy_task():
            pass
        
        scheduler.add_task('dummy', dummy_task, "every(1).minutes")
        
        # 调度器不应该阻塞，我们只测试它能正常启动和停止
        scheduler.start(blocking=False)
        assert scheduler.running == True
        
        scheduler.stop()
        assert scheduler.running == False
