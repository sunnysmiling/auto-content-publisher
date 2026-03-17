"""
测试发布模块
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from publisher import WeChatPublisher, BlogPublisher


class TestWeChatPublisher:
    """测试微信公众号发布器"""
    
    def test_wechat_publisher_init(self):
        """测试公众号发布器初始化"""
        publisher = WeChatPublisher()
        assert publisher is not None
    
    def test_wechat_publisher_with_credentials(self):
        """测试带凭证的初始化"""
        publisher = WeChatPublisher(
            app_id='test_app_id',
            app_secret='test_app_secret'
        )
        assert publisher.app_id == 'test_app_id'
        assert publisher.app_secret == 'test_app_secret'
    
    def test_wechat_publisher_login(self):
        """测试公众号登录"""
        publisher = WeChatPublisher()
        result = publisher.login()
        assert result == True
    
    def test_wechat_publisher_publish_article(self):
        """测试发布文章"""
        publisher = WeChatPublisher()
        
        article = {
            'title': '测试文章',
            'content': '这是测试内容',
            'url': 'https://example.com'
        }
        
        result = publisher.publish_article(article)
        assert result == True
    
    def test_wechat_publisher_batch_publish(self):
        """测试批量发布"""
        publisher = WeChatPublisher()
        
        articles = [
            {'title': f'文章{i}', 'content': f'内容{i}'}
            for i in range(3)
        ]
        
        result = publisher.batch_publish(articles)
        
        assert 'total' in result
        assert 'success' in result
        assert 'failed' in result
        assert result['total'] == 3


class TestBlogPublisher:
    """测试博客发布器"""
    
    def test_blog_publisher_init(self):
        """测试博客发布器初始化"""
        publisher = BlogPublisher()
        assert publisher is not None
    
    def test_blog_publisher_with_credentials(self):
        """测试带凭证的初始化"""
        publisher = BlogPublisher(
            api_url='https://example.com/wp-json',
            api_key='test_api_key'
        )
        assert publisher.api_url == 'https://example.com/wp-json'
        assert publisher.api_key == 'test_api_key'
    
    def test_blog_publisher_publish(self):
        """测试发布文章"""
        publisher = BlogPublisher()
        
        article = {
            'title': '测试博客文章',
            'content': '这是博客内容'
        }
        
        result = publisher.publish(article)
        assert result == True
