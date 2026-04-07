import os
import sys
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Assuming your agent class wraps the LangGraph compiled graph
from src.agent.generator import FinancialRAGAgent
from app.components import render_sidebar, render_agent_thoughts

load_dotenv()

st.set_page_config(page_title="Financial Intelligence Platform", layout="centered")

st.markdown("""
<style>
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    h1 { font-weight: 600; color: #1f2937; padding-bottom: 0px; }
    .stChatInputContainer { border-radius: 8px; border: 1px solid #e5e7eb; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome! I am powered by a Multi-Agent architecture. Ask me a complex financial question!"}]

if "agent" not in st.session_state:
    st.session_state.agent = FinancialRAGAgent()

render_sidebar()

st.title("Financial AI Analyst")
st.divider()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "thoughts" in msg and msg["thoughts"]:
            render_agent_thoughts(msg["thoughts"])

if prompt := st.chat_input("Ask about Boeing's Net Income or Apple's risks..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        thoughts_placeholder = st.empty()
        
        with st.status("Agents are collaborating...", expanded=True) as status_box:
            try:
                # --- LangGraph Streaming ---
                # This assumes your agent.query method yields or returns the LangGraph event stream
                response = st.session_state.agent.query(prompt)
                
                # If your generator handles the graph.stream(stream_mode="updates"), 
                # response["intermediate_steps"] should be a list of dicts from LangGraph
                final_answer = response.get("output", "Analysis complete.")
                graph_events = response.get("intermediate_steps", [])
                
                status_box.update(label="Collaboration complete", state="complete", expanded=False)
                
            except Exception as e:
                final_answer = "System error occurred."
                graph_events = []
                st.error(f"Error: {str(e)}")
                status_box.update(label="Analysis failed", state="error")

        # Render the step-by-step agent hops
        render_agent_thoughts(graph_events)
        st.markdown(final_answer)
        
    st.session_state.messages.append({
        "role": "assistant", 
        "content": final_answer,
        "thoughts": graph_events
    })