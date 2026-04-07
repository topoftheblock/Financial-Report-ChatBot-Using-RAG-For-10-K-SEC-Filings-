import os
from typing import Dict, Any

# Import the compiled LangGraph from your builder script
from src.agent.build_the_langgraph_graphs import agent_graph

class FinancialRAGAgent:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.0):
        """
        Initializes the RAG Agent wrapper.
        (Note: The actual LLM configuration is handled inside main_graph_nodes_and_edges.py, 
        but we accept these parameters here for compatibility with app/main.py).
        """
        self.model_name = model_name
        self.temperature = temperature
        self.graph = agent_graph
        
        # LangGraph memory (checkpointer) requires a thread_id to track conversation history
        self.config = {"configurable": {"thread_id": "streamlit_ui_session"}}

    def query(self, prompt: str) -> Dict[str, Any]:
        """
        Executes the LangGraph with the user's prompt and streams the intermediate steps.
        Returns a dictionary containing the final output and all graph transition events.
        """
        events = []
        
        # 1. Initialize the state with the user's latest message
        initial_state = {
            "messages": [("user", prompt)]
        }
        
        # 2. Stream the graph execution step-by-step
        # stream_mode="updates" yields the state updates exactly as they leave each node
        try:
            for event in self.graph.stream(initial_state, config=self.config, stream_mode="updates"):
                events.append(event)
        except Exception as e:
            print(f"Error during graph execution: {e}")
            return {
                "output": f"An error occurred while routing the agents: {str(e)}",
                "intermediate_steps": events
            }
            
        # 3. Extract the final aggregated answer from the stream
        final_answer = "I could not formulate a complete answer."
        
        if events:
            # Look at the very last event in the stream
            last_event = events[-1]
            
            # The Main Graph ends with the 'aggregate_answers' node
            if "aggregate_answers" in last_event:
                messages = last_event["aggregate_answers"].get("messages", [])
                if messages:
                    final_answer = messages[-1].content
                    
            # Fallback in case the graph was interrupted or routed differently
            else:
                for event_dict in reversed(events):
                    for node_name, state_update in event_dict.items():
                        if "messages" in state_update and state_update["messages"]:
                            last_msg = state_update["messages"][-1]
                            if getattr(last_msg, "content", None):
                                final_answer = last_msg.content
                                break
                    if final_answer != "I could not formulate a complete answer.":
                        break

        # Return the exact dictionary structure expected by app/main.py
        return {
            "output": final_answer,
            "intermediate_steps": events
        }