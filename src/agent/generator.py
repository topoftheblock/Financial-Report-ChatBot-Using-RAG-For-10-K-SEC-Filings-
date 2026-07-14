from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from src.agent.prompt import get_financial_agent_prompt

# Ensure all tools are imported
from src.agent.tools import (
    semantic_financial_search,
    multi_year_financial_search,
    calculate_financial_kpi,
    python_calculator,
)


class FinancialLangChainAgent:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.0):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

        # Add the missing tools to the agent's toolkit
        self.tools = [
            semantic_financial_search,
            multi_year_financial_search,
            calculate_financial_kpi,
            python_calculator,
        ]

        self.prompt = get_financial_agent_prompt()
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
        )

    def query(self, prompt: str, chat_history: list = None) -> Dict[str, Any]:
        if chat_history is None:
            chat_history = []

        try:
            response = self.agent_executor.invoke(
                {"input": prompt, "chat_history": chat_history}
            )

            return {
                "output": response["output"],
                "intermediate_steps": response.get("intermediate_steps", []),
            }
        except Exception as e:
            print(f"Error during agent execution: {e}")
            return {
                "output": f"System error occurred: {str(e)}",
                "intermediate_steps": [],
            }
