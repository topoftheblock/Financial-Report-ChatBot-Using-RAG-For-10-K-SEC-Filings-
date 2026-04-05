import os
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from src.agent.tools import get_financial_tools
from src.agent.prompt import get_agent_prompt

class FinancialRAGAgent:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.0):
        """
        Initializes the Financial Agent Executor.
        Temperature is set to 0.0 to ensure deterministic, factual responses.
        """
        self.llm = ChatOpenAI(
            model=model_name, 
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tools = get_financial_tools()
        self.prompt = get_agent_prompt()
        
        # Create the agent that knows how to use OpenAI's tool-calling feature
        self.agent = create_tool_calling_agent(
            llm=self.llm, 
            tools=self.tools, 
            prompt=self.prompt
        )
        
        # The executor runs the ReAct loop (Observe -> Think -> Act)
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True, 
            return_intermediate_steps=True, 
            max_iterations=5 
        )

    def query(self, user_question: str) -> dict:
        """Takes a user question and executes the agent pipeline."""
        try:
            response = self.agent_executor.invoke({"input": user_question})
            return response
        except Exception as e:
            print(f"Agent Execution Error: {str(e)}")
            return {"output": "I encountered an error processing your financial query."}