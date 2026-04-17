from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

from app.AI.modle.factory import llm_model
from app.AI.agent.tools import execute_sql, get_rag_answer
from app.AI.utils.file_handler import read_text_file
from app.AI.utils.path_tool import build_path


class UserAssistantAgent:
    """
    Tool Calling Agent + ReAct 风格提示增强
    """

    def __init__(self):
        self.llm = llm_model
        self.tools = [execute_sql, get_rag_answer]

        self.prompt = ChatPromptTemplate.from_messages([read_text_file(build_path("data/sys_prompt.md"))])


        self.agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            self.prompt
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )

    def ask(self, question: str, username: str = "李华") -> str:
        try:
            result = self.agent_executor.invoke({
                "input": question,
                "username": username
            })
            return result.get("output", str(result))
        except Exception as e:
            return f"ERROR: {str(e)}"


if __name__ == "__main__":
    agent = UserAssistantAgent()

    # print(agent.ask("我当前余额多少？", "李华"))
    print("===================================================================================")
    print(agent.ask("押金什么时候退？", "test_user"))