import sys
import os
# 添加app目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# 添加app/models到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app/models'))

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 