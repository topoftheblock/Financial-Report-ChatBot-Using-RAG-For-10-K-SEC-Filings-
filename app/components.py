import streamlit as st

def render_sidebar():
    """Renders the sidebar with instructions and controls."""
    with st.sidebar:
        st.title(" Financial RAG Agent")
        st.markdown("""
        **Capabilities:**
        - Semantic Search (MD&A, Risk Factors)
        - Exact Table Lookups (Revenue, EPS)
        - Mathematical Calculations (YoY Growth, Margins)
        """)
        
        st.divider()
        
        if st.button("Clear Chat History", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
        st.divider()
        st.caption("Powered by LangChain, GPT-4o, and Streamlit.")

def render_agent_thoughts(intermediate_steps):
    """
    Takes the intermediate steps from the LangChain agent and renders them 
    in a clean UI expander so the user can see the search and math operations.
    """
    if not intermediate_steps:
        return

    with st.expander(" View Agent's Thought Process & Calculations", expanded=False):
        for step in intermediate_steps:
            # step is a tuple: (AgentAction, Observation)
            action, observation = step
            
            st.markdown(f"**Tool Used:** `{action.tool}`")
            st.markdown(f"**Input Parameters:** `{action.tool_input}`")
            
            # If the tool returned a massive chunk of text, truncate it for the UI
            obs_str = str(observation)
            if len(obs_str) > 500:
                obs_str = obs_str[:500] + " ... [Truncated for brevity]"
                
            st.info(f"**Result:**\n{obs_str}")
            st.divider()