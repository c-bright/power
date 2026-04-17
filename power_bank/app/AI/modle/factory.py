
from abc import ABC, abstractmethod
import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings

from app.AI.utils.path_tool import build_path

load_dotenv()


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self):
        raise NotImplementedError


class EmbeddingFactory(BaseModelFactory):
    def __init__(
        self,
        model_path: str = r"my_model_cache\models--BAAI--bge-small-zh-v1.5\snapshots\7999e1d3359715c523056ef9478215996d62a620",
        device: str = "cpu",
    ):
        self.model_path = build_path(model_path)
        self.device = device

    def generator(self) -> HuggingFaceEmbeddings:
        return HuggingFaceEmbeddings(model_name=str(self.model_path), model_kwargs={"device": self.device})


class LLMFactory(BaseModelFactory):
    def __init__(
        self,
        model: str = "deepseek-chat",
        temperature: float = 0.3,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.model_name = model
        self.temperature = temperature
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    def generator(self) -> Optional[ChatOpenAI]:
        if not self.api_key:
            return None

        return ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.api_key,
            base_url=self.base_url,
            temperature=self.temperature,
        )


embedding_model = EmbeddingFactory().generator()
llm_model = LLMFactory().generator()


