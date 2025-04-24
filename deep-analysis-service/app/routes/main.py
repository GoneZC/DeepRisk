from flask import Blueprint, render_template, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页"""
    return render_template('index.html')

@main_bp.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({"status": "healthy"}) 