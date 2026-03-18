"""OpenAI AI 处理器"""
import json
import re
from typing import Dict, Optional

from .base import BaseAIProcessor
from ..config import config
from ..logger import processor_log


class OpenAIProcessor(BaseAIProcessor):
    """OpenAI GPT 处理器"""

    def __init__(self, ai_config: Dict = None):
        # 优先使用传入配置，否则使用全局配置
        if ai_config:
            super().__init__(ai_config)
        else:
            super().__init__({
                'api_key': config.ai_api_key,
                'model': config.ai_model,
                'temperature': config.ai_temperature,
            })
        self._client = None

    def _get_client(self):
        """获取 OpenAI 客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                processor_log.error("请安装 openai: pip install openai")
                return None
            except Exception as e:
                processor_log.error(f"OpenAI 客户端初始化失败: {e}")
                return None
        return self._client

    def process(self, article: Dict) -> Dict:
        """处理文章：生成摘要、重写标题、提取封面"""
        result = {
            'processed_title': article.get('original_title', ''),
            'processed_content': article.get('original_content', ''),
            'summary': '',
            'cover_image': None,
        }

        client = self._get_client()
        if not client:
            return result

        content = article.get('original_content') or article.get('original_title', '')
        if not content:
            return result

        try:
            # 构建 prompt
            prompt = self._build_prompt(article)
            
            # 调用 API
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个内容编辑助手，擅长提取文章要点、生成吸引人的标题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=1000,
            )

            # 解析结果
            result_text = response.choices[0].message.content
            parsed = self._parse_response(result_text)
            
            result.update(parsed)
            processor_log.info(f"AI 处理完成: {article.get('id')}")

        except Exception as e:
            processor_log.error(f"AI 处理失败: {e}")

        return result

    def _build_prompt(self, article: Dict) -> str:
        """构建处理 prompt"""
        content = article.get('original_content') or article.get('original_title', '')
        # 截取内容前 3000 字符
        content = content[:3000]

        prompt = f"""请处理以下文章，输出 JSON 格式：
{{
    "summary": "一句话摘要（50字以内）",
    "title": "重写后的标题（20字以内，有吸引力）",
    "cover_prompt": "描述文章内容的封面图提示词（英文，可用于 AI 生成图片）"
}}

文章内容：
{content}

只输出 JSON，不要其他内容。"""
        return prompt

    def _parse_response(self, response: str) -> Dict:
        """解析 API 响应"""
        result = {'summary': '', 'processed_title': '', 'cover_image': None}
        
        try:
            # 尝试提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                result['summary'] = data.get('summary', '')
                result['processed_title'] = data.get('title', '')
                # cover_prompt 可用于后续生成封面图
                result['cover_prompt'] = data.get('cover_prompt', '')
        except Exception as e:
            processor_log.warning(f"解析 AI 响应失败: {e}")
        
        return result

    def generate_summary(self, content: str) -> str:
        """生成摘要"""
        client = self._get_client()
        if not client:
            return ''

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个内容编辑助手，擅长提取文章要点。"},
                    {"role": "user", "content": f"请用一句话概括以下内容的核心要点（50字以内）：\n\n{content[:3000]}"}
                ],
                temperature=self.temperature,
                max_tokens=100,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            processor_log.error(f"生成摘要失败: {e}")
            return ''

    def rewrite_title(self, title: str, content: str) -> str:
        """重写标题"""
        client = self._get_client()
        if not client:
            return title

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个标题党，擅长写吸引人的标题。"},
                    {"role": "user", "content": f"请将以下标题重写得更吸引人（20字以内）：\n{title}\n\n内容概要：{content[:500]}"}
                ],
                temperature=self.temperature,
                max_tokens=50,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            processor_log.error(f"重写标题失败: {e}")
            return title

    def extract_cover_image(self, content: str, url: str) -> Optional[str]:
        """提取封面图（从文章中提取图床链接）"""
        # 优先从 URL 提取
        import re
        # 常见图床域名
        img_domains = ['img.', 'cdn.', 'static.', 'pic.']
        
        # 如果有原文内容，尝试提取图片
        if content:
            img_matches = re.findall(r'https?://[^\s"\'<>]+\.(jpg|jpeg|png|gif|webp)', content, re.I)
            if img_matches:
                return img_matches[0]
        
        return None

    def generate_cover_image(self, prompt: str) -> Optional[str]:
        """使用 AI 生成封面图（可选功能）"""
        # 如果配置了 DALL-E，可以实现
        # 这里暂时返回 None
        return None
