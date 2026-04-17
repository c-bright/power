from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.AI.modle.factory import llm_model
from app.AI.utils.path_tool import build_path
from app.AI.utils.file_handler import read_text_file


class IntentClassifier:
    """
    意图识别 LLM
    负责判断：DATABASE / KNOWLEDGE
    """

    def __init__(self):
        self.llm = llm_model
        self.parser = StrOutputParser()

        self.prompt = PromptTemplate.from_template(
            read_text_file(build_path("data/intent_router.md"))
        )

        self.chain = self.prompt | self.llm | self.parser

    def classify(self, question: str) -> str:
        try:
            intent = self.chain.invoke({
                "question": question
            }).strip().upper()

            # 标准化输出（非常关键）
            if "DATABASE" in intent:
                return "DATABASE"

            return "KNOWLEDGE"

        except Exception:
            # 兜底策略
            return "KNOWLEDGE"


