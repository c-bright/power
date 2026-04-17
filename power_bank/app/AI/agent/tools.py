from typing import List, Dict
from langchain_core.tools import tool

from app.AI.rag.rag_service import RagSummarizeService
from app.extensions import get_db
from app.AI.llm.sql_llm import SQLGenerator

rag_service = RagSummarizeService()
sql_service = SQLGenerator()


@tool
def execute_sql(question: str, username: str = "") -> str:
    """
    根据用户问题生成SQL并查询数据库，仅允许SELECT操作，返回结构化结果
    """
    try:
        raw_sql = sql_service.generate(question=question, username=username)
        sql_lower = raw_sql.strip().lower()
        print(f"[SQL] 执行: {raw_sql}")

        if not sql_lower.startswith("select"):
            return "ERROR: only SELECT allowed"

        if ";" in sql_lower.rstrip(";"):
            return "ERROR: multiple statements not allowed"

        forbidden = ["delete", "update", "insert", "drop", "alter", "truncate"]
        if any(k in sql_lower for k in forbidden):
            return "ERROR: dangerous SQL detected"

        db = get_db()

        db.execute(raw_sql)
        rows = db.fetchall()

        if not rows:
            return "RESULT: empty"

        if rows and isinstance(rows[0], dict):
            columns = list(rows[0].keys())
        else:
            columns = [f"col_{i}" for i in range(len(rows[0]))] if rows else []

        return f"RESULT:\ncolumns: {columns}\nrows: {rows}"

    except Exception as e:
        return f"ERROR: {str(e)}"


@tool
def get_rag_answer(query: str) -> str:
    """
    查询共享充电宝规则、收费、押金、退款等知识库内容
    """
    try:
        result = rag_service.rag_summarize(query)

        if not result:
            return "RESULT: empty"

        return f"RESULT:\n{result}"

    except Exception as e:
        return f"ERROR: {str(e)}"