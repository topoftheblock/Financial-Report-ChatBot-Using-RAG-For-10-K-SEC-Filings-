import streamlit as st
import os

def render_sidebar():
    """Renders the sidebar with instructions, controls, and architecture visuals."""
    with st.sidebar:
        st.title("📊 Financial RAG Agent")
        st.markdown("""
        **Capabilities:**
        - Semantic Search (MD&A, Risk Factors)
        - Exact Table Lookups (Revenue, EPS)
        - Mathematical Calculations (YoY Growth, Margins)
        """)
        
        st.divider()
        
        # --- NEW: View Agent Interactions Visually ---
        st.markdown("### Agent Architecture")
        if st.checkbox("Show Multi-Agent Architecture"):
            if os.path.exists("main_agent_graph.png"):
                st.image("main_agent_graph.png", caption="Main Graph (Supervisor Agent)")
            if os.path.exists("subgraph.png"):
                st.image("subgraph.png", caption="Sub Graph (Worker Agent)")
                
        st.divider()
        
        if st.button("Clear Chat History", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        st.divider()
        st.caption("Powered by LangGraph, GPT-4o, and Streamlit.")

def render_agent_thoughts(intermediate_steps):
    """
    Renders LangGraph node executions to show how the agents interact.
    Expects a list of dictionaries where keys are the Node Names.
    """
    if not intermediate_steps:
        return

    with st.expander("🕵️‍♂️ View Multi-Agent Interaction Flow", expanded=False):
        for i, step in enumerate(intermediate_steps):
            # LangGraph stream events usually look like: {'node_name': {'state_key': 'state_value'}}
            if isinstance(step, dict):
                for node_name, state_update in step.items():
                    # Color code the nodes based on which agent they belong to
                    if node_name in ["summarize_history", "rewrite_query", "aggregate_answers"]:
                        agent_type = "👔 Supervisor Agent"
                        color = "blue"
                    elif node_name in ["orchestrator", "tools", "should_compress_context", "compress_context", "collect_answer"]:
                        agent_type = "👷 Worker Agent"
                        color = "green"
                    else:
                        agent_type = "⚙️ System Node"
                        color = "gray"

                    st.markdown(f"### :{color}[Step {i+1}: {agent_type} -> `{node_name}`]")
                    
                    # Extract useful state information to show the user
                    if "messages" in state_update:
                        last_msg = state_update["messages"][-1]
                        
                        # Handle Tool Calls
                        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                            for tool in last_msg.tool_calls:
                                st.write(f"**🛠️ Calling Tool:** `{tool['name']}`")
                                st.json(tool['args'])
                        # Handle Tool Responses
                        elif getattr(last_msg, "type", "") == "tool":
                            obs_str = str(last_msg.content)
                            if len(obs_str) > 300:
                                obs_str = obs_str[:300] + " ... [Truncated]"
                            st.info(f"**Tool Result:**\n{obs_str}")
                        # Handle standard AI messages
                        elif hasattr(last_msg, "content") and last_msg.content:
                            st.write(f"**Output:** {last_msg.content[:200]}...")

                    # Show rewritten queries from the supervisor
                    if "rewrittenQuestions" in state_update:
                        st.write("**📝 Supervisor drafted tasks for Worker:**")
                        for q in state_update["rewrittenQuestions"]:
                            st.write(f"- {q}")
                            
                    st.divider()