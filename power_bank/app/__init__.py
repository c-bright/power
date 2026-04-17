# -*- coding: utf-8 -*-
"""Application factory: create_app() builds and configures the Flask app."""

import os
import threading

from flask import Flask
from flask_cors import CORS

from app.config import config_by_name, load_instance_config
from app.extensions import PowerMySQL


def _is_truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])
    load_instance_config(app)

    CORS(app)

    db = PowerMySQL()
    db.init_app(app)

    # --- Blueprints ---
    from app.auth import auth_bp
    from app.user.rent import user_rent_bp
    from app.user.query import user_rent_history_bp
    from app.user.user import user_bp
    from app.admin.device import device_manage_bp
    from app.admin.pricing import pricing_manage_bp
    from app.admin.visual import visual_manage_bp
    from app.admin.dispute import dispute_manage_bp
    from app.AI.agent.routes import assistant_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_rent_bp)
    app.register_blueprint(user_rent_history_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(device_manage_bp)
    app.register_blueprint(pricing_manage_bp)
    app.register_blueprint(visual_manage_bp)
    app.register_blueprint(dispute_manage_bp)
    app.register_blueprint(assistant_bp)

    disable_sync_worker = _is_truthy(os.environ.get("DISABLE_SYNC_WORKER", "0"))

    bank_data = None
    if not disable_sync_worker:
        try:
            from app.sysadmin.bank import get_webase_address

            bank_data = get_webase_address()
            print("获取地址", bank_data)
        except Exception as e:
            print(f"get_webase_address失败: {e}")
            bank_data = None

    app.config["BANK_DATA"] = bank_data

    def run_worker():
        from app.sysadmin.synchronization import run_dual_sync

        run_dual_sync()
        while True:
            try:
                from app.sysadmin.sync_worker import SuperSyncWorker
                print("++================================================")
                SuperSyncWorker().run()
            except Exception as e:
                print(f"Worker 异常: {e}")

    is_main = (not app.debug) or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    if is_main:
        db.execute_sql_file()
        if not disable_sync_worker:
            threading.Thread(target=run_worker, daemon=True).start()
            print("[OK] Worker started")
        else:
            print("[OK] Worker disabled")

    return app
