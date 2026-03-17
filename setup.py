"""
Auto Content Publisher
全自动内容采集与发布系统

功能：
- RSS/Atom 订阅源抓取
- 网页内容提取
- AI 内容处理与去重
- 微信公众号自动发布
- 定时任务调度
"""

from setuptools import setup, find_packages

setup(
    name='auto-content-publisher',
    version='0.1.0',
    description='全自动内容采集与发布系统',
    author='Auto Publisher',
    author_email='auto@example.com',
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'pyyaml>=6.0',
        'feedparser>=6.0.0',
        'beautifulsoup4>=4.12.0',
        'lxml>=4.9.0',
        'schedule>=1.2.0',
        'sqlalchemy>=2.0.0',
        'python-dateutil>=2.8.0',
    ],
    entry_points={
        'console_scripts': [
            'auto-publisher=src.main:main',
        ],
    },
    python_requires='>=3.8',
)
