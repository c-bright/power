# -*- coding: utf-8 -*-
from functools import wraps
from typing import Iterable, Optional

from flask import g, jsonify, request

from app.auth.token_service import verify_access_token


def require_auth(roles: Optional[Iterable[str]] = None):
    roles_set = set(roles) if roles else None

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"message": "未认证"}), 401
            token = auth[len("Bearer "):].strip()
            if not token:
                return jsonify({"message": "未认证"}), 401

            try:
                payload = verify_access_token(token)
            except PermissionError:
                return jsonify({"message": "未认证"}), 401

            role = payload.get("role")
            if roles_set and role not in roles_set:
                return jsonify({"message": "无权限"}), 403

            g.current_user = payload
            return fn(*args, **kwargs)

        return wrapper

    return decorator

