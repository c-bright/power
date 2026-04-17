

import os
import re
from typing import List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.AI.modle.factory import embedding_model
from app.AI.utils.file_handler import get_file_md5, text_loader
from app.AI.utils.logger_handler import logger
from app.AI.utils.path_tool import build_path


def split_faq(text: str) -> List[Document]:

    if not text:
        return []

    pattern = r"(?ms)^问题：.*?(?=^问题：|\Z)"
    blocks = re.findall(pattern, text)
    return [Document(page_content=b.strip()) for b in blocks if b.strip()]


class VectorStoreService:
    def __init__(self, index_path: str = r"faiss_index", auto_build: bool = True):
        self.index_path = build_path(index_path)
        self.vector_store = None

        self._load_index()

        if auto_build:
            self.build_index()

    def _load_index(self):
        index_file = os.path.join(self.index_path, "index.faiss")
        pkl_file = os.path.join(self.index_path, "index.pkl")

        if os.path.exists(index_file) and os.path.exists(pkl_file):
            try:
                self.vector_store = FAISS.load_local(
                    self.index_path,
                    embeddings=embedding_model,
                    allow_dangerous_deserialization=True,
                )
                logger.info(f"加载已有索引: {self.index_path}")
            except Exception as e:
                logger.error(f"加载失败: {e}")
                self.vector_store = None
        else:
            logger.info("未发现索引，将新建")

    def get_retriever(self, k: int = 1):
        if self.vector_store is None:
            logger.warning("向量库未初始化")
            return None

        return self.vector_store.as_retriever(search_kwargs={"k": k})

    def _check_md5_exists(self, md5_hex: str) -> bool:
        md5_file_path = build_path("md5_records.txt")
        if not os.path.exists(md5_file_path):
            return False

        with open(md5_file_path, "r", encoding="utf-8") as f:
            return md5_hex in {line.strip() for line in f}

    def _save_md5(self, md5_hex: str):
        md5_file_path = build_path("md5_records.txt")
        with open(md5_file_path, "a", encoding="utf-8") as f:
            f.write(md5_hex + "\n")

    def _load_documents_from_folder(self, folder_path: str = "data"):
        abs_folder = build_path(folder_path)

        if not os.path.exists(abs_folder):
            logger.error(f"文件夹不存在: {abs_folder}")
            return []

        all_documents: List[Document] = []
        new_count = 0

        for filename in os.listdir(abs_folder):
            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(abs_folder, filename)

            md5_hex = get_file_md5(file_path)
            if not md5_hex:
                continue

            if self._check_md5_exists(md5_hex):
                continue

            docs = text_loader(file_path)
            if not docs:
                continue

            text = docs[0].page_content

            faq_docs = split_faq(text)
            final_docs = faq_docs if faq_docs else [Document(page_content=text)]

            for doc in final_docs:
                doc.metadata.update(
                    {
                        "来源": filename,
                        "路径": file_path,
                        "指纹": md5_hex,
                    }
                )

            all_documents.extend(final_docs)
            self._save_md5(md5_hex)

            new_count += 1

        logger.info(f"新增文件: {new_count}")
        return all_documents

    def build_index(self):
        documents = self._load_documents_from_folder()

        if not documents:
            logger.info("没有新文档")
            return

        logger.info(f"写入向量库: {len(documents)} 条数据")

        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents=documents, embedding=embedding_model)
            logger.info("创建新索引")
        else:
            self.vector_store.add_documents(documents)
            logger.info("追加索引")

        os.makedirs(self.index_path, exist_ok=True)
        self.vector_store.save_local(self.index_path)

        logger.info("索引保存完成")


if __name__ == "__main__":
    vector_service = VectorStoreService(auto_build=True)
    retriever = vector_service.get_retriever(k=2)

    if retriever:
        results = retriever.invoke("如何充值")
        for doc in results:
            print(doc.page_content)
            print(doc.metadata)
