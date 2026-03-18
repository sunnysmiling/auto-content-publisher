"""公众号发布器 - 增强版"""
import json
import time
from typing import Dict, Optional, List
from datetime import datetime
import requests

from ..config import config
from ..logger import publisher_log


class WeChatPublisher:
    """微信公众号发布器"""

    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = app_id or config.wechat_app_id
        self.app_secret = app_secret or config.wechat_app_secret
        self.access_token = None
        self.token_expires = 0

    def _get_access_token(self) -> Optional[str]:
        """获取 access_token"""
        if self.access_token and time.time() < self.token_expires:
            return self.access_token

        url = f"https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.app_id,
            'secret': self.app_secret
        }

        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()

            if 'access_token' in data:
                self.access_token = data['access_token']
                self.token_expires = time.time() + data.get('expires_in', 7200) - 300
                return self.access_token
            else:
                publisher_log.error(f"获取 access_token 失败: {data}")
                return None
        except Exception as e:
            publisher_log.error(f"获取 access_token 异常: {e}")
            return None

    # ========== 草稿箱管理 ==========

    def create_draft(self, title: str, content: str, 
                     author: str = '', digest: str = '',
                     cover_media_id: str = None) -> Optional[str]:
        """创建草稿箱图文消息"""
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

        articles = [{
            "title": title,
            "author": author,
            "content": content,
            "digest": digest[:120],
            "content_source_url": "",
            "thumb_media_id": cover_media_id or "",
        }]

        try:
            resp = requests.post(url, json={"articles": articles}, timeout=30)
            result = resp.json()

            if 'media_id' in result:
                publisher_log.info(f"创建草稿成功: {result['media_id']}")
                return result['media_id']
            else:
                publisher_log.error(f"创建草稿失败: {result}")
                return None
        except Exception as e:
            publisher_log.error(f"创建草稿异常: {e}")
            return None

    def get_drafts(self, offset: int = 0, count: int = 20) -> List[Dict]:
        """获取草稿列表"""
        token = self._get_access_token()
        if not token:
            return []

        url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}"

        try:
            resp = requests.post(url, json={
                "offset": offset,
                "count": count,
                "no_content": 1  # 不获取内容以提高性能
            }, timeout=30)
            result = resp.json()

            if 'item' in result:
                return result['item']
            return []
        except Exception as e:
            publisher_log.error(f"获取草稿列表异常: {e}")
            return []

    def get_draft_content(self, media_id: str) -> Optional[Dict]:
        """获取草稿详情"""
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/draft/get?access_token={token}"

        try:
            resp = requests.post(url, json={"media_id": media_id}, timeout=30)
            result = resp.json()

            if 'news_item' in result:
                return result['news_item']
            return None
        except Exception as e:
            publisher_log.error(f"获取草稿详情异常: {e}")
            return None

    def delete_draft(self, media_id: str) -> bool:
        """删除草稿"""
        token = self._get_access_token()
        if not token:
            return False

        url = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={token}"

        try:
            resp = requests.post(url, json={"media_id": media_id}, timeout=30)
            result = resp.json()

            if result.get('errcode') == 0:
                publisher_log.info(f"删除草稿成功: {media_id}")
                return True
            else:
                publisher_log.error(f"删除草稿失败: {result}")
                return False
        except Exception as e:
            publisher_log.error(f"删除草稿异常: {e}")
            return False

    # ========== 发布 ==========

    def publish_draft(self, media_id: str) -> bool:
        """发布草稿到公众号"""
        token = self._get_access_token()
        if not token:
            return False

        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}"

        try:
            resp = requests.post(url, json={"media_id": media_id}, timeout=30)
            result = resp.json()

            if result.get('errcode') == 0:
                publisher_log.info(f"发布成功: {media_id}, msg_id: {result.get('msg_id')}")
                return True
            else:
                publisher_log.error(f"发布失败: {result}")
                return False
        except Exception as e:
            publisher_log.error(f"发布异常: {e}")
            return False

    def get_publish_status(self, msg_id: str) -> Optional[Dict]:
        """查询发布状态"""
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={token}"

        try:
            resp = requests.post(url, json={"msg_id": msg_id}, timeout=30)
            result = resp.json()

            if 'article_id' in result:
                return result
            return None
        except Exception as e:
            publisher_log.error(f"查询发布状态异常: {e}")
            return None

    # ========== 素材管理 ==========

    def upload_image(self, image_path: str) -> Optional[str]:
        """上传图片获取 URL（用于文章内图片）"""
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"

        try:
            with open(image_path, 'rb') as f:
                files = {'media': f}
                resp = requests.post(url, files=files, timeout=30)
                result = resp.json()

            if 'url' in result:
                publisher_log.info(f"图片上传成功: {result['url']}")
                return result['url']
            else:
                publisher_log.error(f"图片上传失败: {result}")
                return None
        except Exception as e:
            publisher_log.error(f"图片上传异常: {e}")
            return None

    def upload_cover(self, image_path: str) -> Optional[str]:
        """上传封面图获取 media_id"""
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"

        try:
            with open(image_path, 'rb') as f:
                files = {'media': f}
                resp = requests.post(url, files=files, timeout=60)
                result = resp.json()

            if 'media_id' in result:
                publisher_log.info(f"封面上传成功: {result['media_id']}")
                return result['media_id']
            else:
                publisher_log.error(f"封面上传失败: {result}")
                return None
        except Exception as e:
            publisher_log.error(f"封面上传异常: {e}")
            return None

    def get_articles(self, media_id: str) -> Optional[list]:
        """获取草稿箱图文"""
        return self.get_draft_content(media_id)
