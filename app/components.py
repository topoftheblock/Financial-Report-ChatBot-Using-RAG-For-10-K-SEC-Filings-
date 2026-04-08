import streamlit as st

def render_sidebar():
    """Renders the sidebar with instructions, controls, and architecture visuals."""
    with st.sidebar:
        st.title("Financial RAG Agent")
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
        st.caption("Powered by LangChain, OpenAI/GPT, and Streamlit.")


def render_agent_thoughts(intermediate_steps):
    """
    Renders LangChain agent thoughts and tool calls to show how it thinks under the hood.
    Expects a list of tuples containing (AgentAction, Observation).
    """
    if not intermediate_steps:
        return

    with st.expander(" View Agent Thought Process", expanded=False):
        for i, step in enumerate(intermediate_steps):
            
            # Ensure it's the expected LangChain tuple format
            if isinstance(step, tuple) and len(step) == 2:
                action, observation = step
                
                st.markdown(f"### Step {i+1}: Agent Reasoning")
                
                # 1. Print the Agent's raw internal monologue (Thought)
                if hasattr(action, "log") and action.log:
                    # Escape dollar signs here as well so the UI doesn't break
                    safe_log = action.log.replace("$", r"\$")
                    st.info(f"**Internal Thought:**\n\n{safe_log}")
                
                # 2. Print the exact Tool and Input used
                tool_name = getattr(action, 'tool', 'Unknown')
                tool_input = getattr(action, 'tool_input', 'None')
                st.write(f"** Tool Called:** `{tool_name}`")
                st.write(f"** Tool Input:** `{tool_input}`")
                
                # 3. Print the Observation (What the database/calculator returned)
                # The truncation logic has been entirely removed here to display the complete response.
                obs_str = str(observation).replace("$", r"\$")
                
                st.success(f"**Observation (Result):**\n\n{obs_str}")
                
                st.divider()