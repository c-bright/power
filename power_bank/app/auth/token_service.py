# -*- coding: utf-8 -*-
import time
from typing import Any, Dict, Optional

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


def _serializer() -> URLSafeTimedSerializer:
    secret_key = current_app.config.get("SECRET_KEY", "")
    salt = current_app.config.get("ACCESS_TOKEN_SALT", "access-token")
    return URLSafeTimedSerializer(secret_key=secret_key, salt=salt)


def create_access_token(payload: Dict[str, Any], expires_in: Optional[int] = None) -> str:
    if expires_in is None:
        expires_in = int(current_app.config.get("ACCESS_TOKEN_EXPIRES", 1800))
    data = dict(payload)
    data["iat"] = int(time.time())
    data["exp"] = int(time.time()) + int(expires_in)
    return _serializer().dumps(data)


def verify_access_token(token: str) -> Dict[str, Any]:
    expires_in = int(current_app.config.get("ACCESS_TOKEN_EXPIRES", 1800))
    try:
        data = _serializer().loads(token, max_age=expires_in)
    except SignatureExpired as e:
        raise PermissionError("token_expired") from e
    except BadSignature as e:
        raise PermissionError("token_invalid") from e

    exp = int(data.get("exp") or 0)
    if exp and int(time.time()) > exp:
        raise PermissionError("token_expired")
    return data

