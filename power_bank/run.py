# -*- coding: utf-8 -*-
"""应用入口：使用应用工厂创建并运行 Flask 应用。"""

import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
