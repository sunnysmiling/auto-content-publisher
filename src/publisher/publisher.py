"""发布调度器"""
from typing import Dict, Optional
from datetime import datetime

from .wechat_publisher import WeChatPublisher
from ..database import db
from ..logger import publisher_log


class Publisher:
    """发布调度器"""

    def __init__(self, publisher: WeChatPublisher = None):
        self.db = db
        self.publisher = publisher or WeChatPublisher()

    def publish_pending(self, limit: int = 5) -> int:
        """发布待发布的文章"""
        # 获取已处理完成的文章
        articles = self.db.get_articles(status='processing', limit=limit)
        
        # 也获取处理完成但未发布的
        if not articles:
            articles = self.db.get_articles(status='published', limit=limit)
        
        success_count = 0

        for article in articles:
            try:
                if self.publish_article(article['id']):
                    success_count += 1
            except Exception as e:
                publisher_log.error(f"发布文章失败: {article['id']}, {e}")

        publisher_log.info(f"批量发布完成: 成功 {success_count}/{len(articles)} 篇")
        return success_count

    def publish_article(self, article_id: int) -> bool:
        """发布单篇文章到公众号"""
        article = self.db.get_article(article_id)
        if not article:
            return False

        # 检查文章状态
        if article['status'] not in ['processing', 'published']:
            publisher_log.warning(f"文章状态不对: {article['status']}")
            return False

        try:
            # 构建微信图文内容
            content = self._build_html_content(article)
            
            # 创建草稿
            media_id = self.publisher.create_draft(
                title=article.get('processed_title') or article.get('original_title', '无标题'),
                content=content,
                digest=article.get('summary', '')[:120],
                author='Auto Publisher'
            )

            if not media_id:
                publisher_log.error(f"创建草稿失败: {article_id}")
                self.db.mark_failed(article_id, "创建草稿失败")
                return False

            # 可选：直接发布
            # self.publisher.publish_draft(media_id)

            # 更新数据库
            self.db.update_article(
                article_id,
                status='published',
                published_at=datetime.now().isoformat()
            )

            publisher_log.info(f"文章发布成功: {article_id}, media_id: {media_id}")
            return True

        except Exception as e:
            publisher_log.error(f"发布文章异常: {article_id}, {e}")
            self.db.mark_failed(article_id, str(e))
            return False

    def _build_html_content(self, article: Dict) -> str:
        """构建微信图文 HTML 内容"""
        title = article.get('processed_title') or article.get('original_title', '')
        content = article.get('processed_content') or article.get('original_content', '')
        summary = article.get('summary', '')
        
        # 简单的 HTML 模板
        html = f"""
        <h2>{title}</h2>
        <p><strong>摘要：</strong>{summary}</p>
        <hr/>
        <div class="content">
            {content}
        </div>
        <p style="color:#999;font-size:12px;margin-top:20px;">
            本文由 Auto Content Publisher 自动发布
        </p>
        """
        return html

    def batch_publish(self, article_ids: list) -> Dict:
        """批量发布指定文章"""
        results = {'success': 0, 'failed': 0, 'total': len(article_ids)}

        for article_id in article_ids:
            if self.publish_article(article_id):
                results['success'] += 1
            else:
                results['failed'] += 1

        return results
