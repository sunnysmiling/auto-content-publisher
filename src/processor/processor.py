"""处理器调度器"""
from typing import List, Dict
from datetime import datetime
import time

from .base import BaseAIProcessor
from .openai_processor import OpenAIProcessor
from .filter import SensitiveWordFilter, get_filter
from .image_handler import ImageHandler, get_image_handler
from ..database import db
from ..logger import processor_log


class Processor:
    """文章处理器调度器"""

    def __init__(self, processor: BaseAIProcessor = None, filter_config: dict = None):
        self.db = db
        self.processor = processor or OpenAIProcessor()
        self.filter = SensitiveWordFilter() if not filter_config else get_filter(filter_config)
        self.image_handler = get_image_handler()

    def process_pending(self, limit: int = 10) -> int:
        """处理待处理的文章"""
        articles = self.db.get_articles(status='pending', limit=limit)
        success_count = 0

        for article in articles:
            try:
                if self.process_article(article['id']):
                    success_count += 1
            except Exception as e:
                processor_log.error(f"处理文章失败: {article['id']}, {e}")
                self.db.mark_failed(article['id'], str(e))

        processor_log.info(f"批量处理完成: 成功 {success_count}/{len(articles)} 篇")
        return success_count

    def process_article(self, article_id: int) -> bool:
        """处理单篇文章"""
        article = self.db.get_article(article_id)
        if not article:
            return False

        # 标记为处理中
        self.db.mark_processing(article_id)

        try:
            # 如果没有 original_content，先抓取
            if not article.get('original_content'):
                from ..scraper import Crawler
                crawler = Crawler()
                crawler.crawl_article_content(article_id)
                # 重新获取文章内容
                article = self.db.get_article(article_id)

            # ========== 处理步骤 ==========
            
            # 1. AI 处理：生成摘要、重写标题
            result = self.processor.process(article)
            
            # 2. 敏感词过滤
            original_title = article.get('original_title', '')
            processed_title = result.get('processed_title', original_title)
            processed_content = result.get('processed_content', article.get('original_content', ''))
            summary = result.get('summary', '')
            
            # 过滤标题
            if self.filter.contains(processed_title):
                processed_title = self.filter.filter(processed_title)
                processor_log.warning(f"文章标题包含敏感词，已过滤: {article_id}")
            
            # 过滤内容
            if self.filter.contains(processed_content):
                processed_content = self.filter.filter(processed_content)
                processor_log.warning(f"文章内容包含敏感词，已过滤: {article_id}")
            
            # 过滤摘要
            if self.filter.contains(summary):
                summary = self.filter.filter(summary)
            
            # 3. 封面图处理
            cover_image = self.image_handler.process_cover_image(article)

            # ========== 更新数据库 ==========
            self.db.update_article(
                article_id,
                processed_title=processed_title,
                processed_content=processed_content,
                summary=summary,
                cover_image=cover_image,
                processed_at=datetime.now().isoformat()
            )

            processor_log.info(f"文章处理完成: {article_id}")
            return True

        except Exception as e:
            processor_log.error(f"处理文章异常: {article_id}, {e}")
            self.db.mark_failed(article_id, str(e))
            return False

    def batch_process(self, article_ids: List[int]) -> Dict:
        """批量处理指定文章"""
        results = {'success': 0, 'failed': 0, 'total': len(article_ids)}

        for article_id in article_ids:
            if self.process_article(article_id):
                results['success'] += 1
            else:
                results['failed'] += 1

        return results
    
    def retry_failed(self, limit: int = 10) -> int:
        """重试失败的文章"""
        failed_articles = self.db.get_articles(status='failed', limit=limit)
        retry_count = 0
        
        for article in failed_articles:
            try:
                # 重置状态为 pending
                self.db.update_article(article['id'], status='pending', error_message=None)
                if self.process_article(article['id']):
                    retry_count += 1
            except Exception as e:
                processor_log.error(f"重试失败: {article['id']}, {e}")
        
        processor_log.info(f"重试完成: 成功 {retry_count}/{len(failed_articles)} 篇")
        return retry_count
