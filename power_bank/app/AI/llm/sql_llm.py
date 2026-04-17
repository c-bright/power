from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.AI.modle.factory import llm_model
from app.AI.utils.path_tool import build_path
from app.AI.utils.file_handler import read_text_file


class SQLGenerator:
    """
    专门负责 SQL 生成
    """

    def __init__(self):
        self.llm = llm_model
        self.parser = StrOutputParser()

        self.prompt = PromptTemplate.from_template(
            read_text_file(build_path("data/sql_generate.md"))
        )

        self.chain = self.prompt | self.llm | self.parser

    def generate(self, question: str, username: str):
        try:
            sql = self.chain.invoke({
                "question": question,
                "username": username
            }).strip()
            return sql
        except Exception:
            raise Exception("SQL生成失败")