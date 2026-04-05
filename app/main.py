import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Ensure the root directory is in the path so we can import from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.generator import FinancialRAGAgent
from app.components import render_sidebar, render_agent_thoughts

# Load environment variables (API Keys)
load_dotenv()

# Set up the Streamlit page configuration
st.set_page_config(
    page_title="Financial Intelligence Platform",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for a modern, contemporary design ---
st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-family: 'Inter', 'Helvetica Neue', sans-serif;
    }
    h1 {
        font-weight: 600;
        color: #1f2937;
        padding-bottom: 0px;
    }
    .subtitle {
        color: #6b7280; 
        font-size: 1.1em; 
        margin-bottom: 2rem;
    }
    .stChatInputContainer {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 1. Initialize Session State
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to the Financial Intelligence Platform. I can query SEC filings, extract financial metrics, and calculate margins or growth. How can I assist you today?"}
    ]

if "agent" not in st.session_state:
    st.session_state.agent = FinancialRAGAgent(model_name="gpt-4o", temperature=0.0)

# -------------------------------------------------------------------
# 2. Render UI Components
# -------------------------------------------------------------------
render_sidebar()

st.title("Financial AI Analyst")
st.markdown('<p class="subtitle">Enterprise-grade financial data extraction and analysis.</p>', unsafe_allow_html=True)
st.divider()

# Display existing chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if "thoughts" in msg:
            render_agent_thoughts(msg["thoughts"])

# -------------------------------------------------------------------
# 3. Handle User Input & Agent Execution
# -------------------------------------------------------------------
if prompt := st.chat_input("Enter your query (e.g., 'What was Boeing's Net Income in 2025?')..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Processing financial data...", expanded=True) as status_box:
            
            try:
                response = st.session_state.agent.query(prompt)
                
                final_answer = response.get("output", "I could not generate an answer.")
                thoughts = response.get("intermediate_steps", [])
                
                status_box.update(label="Analysis complete", state="complete", expanded=False)
                
            except Exception as e:
                final_answer = "I encountered a system error while processing your request."
                thoughts = []
                st.error(f"System Error: {str(e)}")
                status_box.update(label="Analysis failed", state="error")

        render_agent_thoughts(thoughts)
        st.markdown(final_answer)
        
    st.session_state.messages.append({
        "role": "assistant", 
        "content": final_answer,
        "thoughts": thoughts
    })