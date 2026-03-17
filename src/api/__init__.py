"""
API 接口模块
"""
from flask import Flask, request, jsonify
import logging
from typing import Dict

logger = logging.getLogger(__name__)

app = Flask(__name__)

# 存储采集器实例
scraper = None
processor = None
scheduler = None
publisher = None


def init_api(scraper_inst, processor_inst, scheduler_inst, publisher_inst):
    """初始化 API"""
    global scraper, processor, scheduler, publisher
    scraper = scraper_inst
    processor = processor_inst
    scheduler = scheduler_inst
    publisher = publisher_inst


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'service': 'auto-content-publisher'})


@app.route('/api/feeds', methods=['GET'])
def list_feeds():
    """获取订阅源列表"""
    # TODO: 从数据库获取
    return jsonify({'feeds': []})


@app.route('/api/feeds', methods=['POST'])
def add_feed():
    """添加订阅源"""
    data = request.json
    url = data.get('url')
    name = data.get('name')
    
    if not url:
        return jsonify({'error': 'url is required'}), 400
    
    # TODO: 保存到数据库
    logger.info(f"Added feed: {name} - {url}")
    
    return jsonify({'success': True, 'feed': {'url': url, 'name': name}})


@app.route('/api/feeds/fetch', methods=['POST'])
def fetch_feeds():
    """手动触发采集"""
    data = request.json
    feed_urls = data.get('urls', [])
    
    if not feed_urls:
        return jsonify({'error': 'urls is required'}), 400
    
    articles = scraper.fetch_multiple(feed_urls)
    processed = processor.batch_process(articles)
    
    return jsonify({
        'total': len(articles),
        'processed': len(processed),
        'articles': processed[:10]  # 返回前10条
    })


@app.route('/api/articles', methods=['GET'])
def list_articles():
    """获取文章列表"""
    # TODO: 从数据库查询
    return jsonify({'articles': []})


@app.route('/api/articles/<article_id>', methods=['GET'])
def get_article(article_id):
    """获取单篇文章"""
    # TODO: 从数据库查询
    return jsonify({'id': article_id, 'title': 'Sample Article'})


@app.route('/api/publish', methods=['POST'])
def publish_article():
    """发布文章"""
    data = request.json
    article = data.get('article')
    
    if not article:
        return jsonify({'error': 'article is required'}), 400
    
    success = publisher.publish_article(article)
    
    return jsonify({'success': success})


@app.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    """获取调度器状态"""
    status = scheduler.get_status()
    return jsonify(status)


@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """启动调度器"""
    scheduler.start(blocking=False)
    return jsonify({'success': True})


@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """停止调度器"""
    scheduler.stop()
    return jsonify({'success': True})


def run_api(host='0.0.0.0', port=5000, debug=False):
    """运行 API 服务"""
    logger.info(f"Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_api()
