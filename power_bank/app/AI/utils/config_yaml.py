import yaml
from pathlib import Path
from path_tool import build_path


_config_cache = None  # 缓存（避免重复读取）


def load_config():
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    config_path: Path = build_path("config", "config.yaml")

    with open(config_path, "r", encoding="utf-8") as f:
        _config_cache = yaml.safe_load(f)

    return _config_cache


def get_config(path: str, default=None):
    """
    支持用 'a.b.c' 方式读取
    """
    config = load_config()

    keys = path.split(".")
    value = config

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value

