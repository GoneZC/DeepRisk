from flask import Blueprint, jsonify
from .consumer import consumer

bp = Blueprint('consumer', __name__)

@bp.route('/status')
def consumer_status():
    return jsonify({
        'consumer_status': consumer.get_status(),
        'queue_status': consumer.get_consumer_status()
    })

@bp.route('/test-connection')
def test_connection():
    try:
        with consumer._get_connection() as conn:
            return jsonify({
                "status": "success",
                "message": f"成功连接到 {consumer._connection_params.host}:{consumer._connection_params.port}"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@bp.route('/start', methods=['POST'])
def start_consumer():
    """手动启动消费者"""
    try:
        consumer.start_consuming()
        return jsonify({
            "status": "success",
            "message": "消费者已启动"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500 