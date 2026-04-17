import hashlib
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from typing import List, Optional

from app.AI.utils.logger_handler import logger


def get_file_md5(file_path: str, chunk_size: int = 8192) -> Optional[str]:
    """
    计算文件 MD5（失败返回 None）
    """
    file = Path(file_path)

    try:
        if not file.exists() or not file.is_file():
            logger.error(f"文件不存在: {file_path}")
            return None

        md5 = hashlib.md5()

        with file.open("rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5.update(chunk)

        return md5.hexdigest()

    except Exception:
        logger.exception(f"MD5计算失败: {file_path}")
        return None


def text_loader(file_path: str) -> List[Document]:
    """
    加载文本文件（失败返回空列表）
    """
    file = Path(file_path)

    try:
        if not file.exists() or not file.is_file():
            logger.error(f"文件不存在: {file_path}")
            return []

        return TextLoader(str(file_path), encoding="utf-8").load()

    except Exception:
        logger.exception(f"文件加载失败: {file_path}")
        return []


def read_text_file(file_path: str, encoding: str = "utf-8", max_chars: Optional[int] = None) -> Optional[str]:
    """
    读取文本文件内容，失败返回 None，并记录日志。

    :param file_path: 文件路径
    :param encoding: 文本编码，默认 utf-8
    :param max_chars: 可选，最多读取字符数（用于避免一次性读入过大文件）
    """
    file = Path(file_path)

    try:
        if not file.exists() or not file.is_file():
            logger.error(f"文件不存在: {file_path}")
            return None

        content = file.read_text(encoding=encoding, errors="ignore")
        if max_chars is not None and max_chars >= 0:
            return content[:max_chars]
        return content

    except Exception:
        logger.exception(f"读取文件失败: {file_path}")
        return None


if __name__ == "__main__":
    path = "../logs/text.txt"

    # 计算 MD5
    md5 = get_file_md5(path)

    if md5:
        print("MD5:", md5)
    else:
        print("MD5计算失败")

    # 加载文档
    docs = text_loader(path)

    if docs:
        print("文档内容:")
        for doc in docs:
            print(doc.page_content)
    else:
        print("加载失败")
