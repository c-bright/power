

from typing import List

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from app.AI.modle.factory import llm_model
from app.AI.rag.vector_store import VectorStoreService
from app.AI.utils.file_handler import read_text_file
from app.AI.utils.path_tool import build_path

class RagSummarizeService(object):
    def __init__(self, path_txt: str = r"data\prompt_template.md"):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever(k=3)

        self.prompt_text = read_text_file(build_path(path_txt)) or ""
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)

        self.model = llm_model
        self.chain = self._build_chain()

    def _build_chain(self):
        return self.prompt_template | self.model | StrOutputParser()

    def retriever_docs(self, query: str) -> List[Document]:
        if not self.retriever:
            return []
        return self.retriever.invoke(query) or []

    def build_context(self, docs: List[Document]) -> str:
        if not docs:
            return ""

        parts: List[str] = []
        for i, doc in enumerate(docs, start=1):
            text = (doc.page_content or "").strip()
            if not text:
                continue
            parts.append(f"参考资料{i}：\n{text}")

        return "\n\n".join(parts).strip()

    def rag_summarize_with_context(self, query: str, extra_context: str = "") -> str:
        docs = self.retriever_docs(query)
        docs_context = self.build_context(docs)

        extra_context = (extra_context or "").strip()
        if extra_context and docs_context:
            context = extra_context + "\n\n" + docs_context
        else:
            context = extra_context or docs_context

        try:
            return self.chain.invoke({"input": query, "context": context})
        except Exception:
            return None

    def rag_summarize(self, query: str) -> str:
        return self.rag_summarize_with_context(query=query, extra_context="")


if __name__ == "__main__":
    rag = RagSummarizeService()
    print(rag.rag_summarize("什么时候退还押金"))
