import os
import sys
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.generator import FinancialLangChainAgent
from app.components import render_sidebar, render_agent_thoughts
from langchain_core.messages import AIMessage, HumanMessage
from src.utils.logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

load_dotenv()

st.set_page_config(page_title="Financial Intelligence Platform", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Welcome! I am powered by LangChain. Ask me a financial question!",
        }
    ]

if "lc_history" not in st.session_state:
    st.session_state.lc_history = []  # LangChain specific message objects

if "agent" not in st.session_state:
    st.session_state.agent = FinancialLangChainAgent()

render_sidebar()
st.title("Financial AI Analyst")
st.divider()

# Re-render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "thoughts" in msg and msg["thoughts"]:
            render_agent_thoughts(msg["thoughts"])

if prompt := st.chat_input("Ask about Boeing's Net Income or Apple's risks..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Analyzing...", expanded=True) as status_box:
            try:
                # Pass prompt and history to LangChain Agent
                response = st.session_state.agent.query(
                    prompt, st.session_state.lc_history
                )

                final_answer = response.get("output", "Analysis complete.")

                # 1. ESCAPE DOLLAR SIGNS: Prevent currency from triggering inline math
                final_answer = final_answer.replace("$", r"\$")

                # 2. CONVERT LATEX MATH BLOCKS: Change \[ \] to $$ $$ so Streamlit renders them as UI math equations
                final_answer = final_answer.replace(r"\[", "$$").replace(r"\]", "$$")

                # (Optional) If your agent also outputs inline math like \( ... \), you can convert them to $
                final_answer = final_answer.replace(r"\(", "$").replace(r"\)", "$")

                agent_steps = response.get("intermediate_steps", [])

                status_box.update(
                    label="Analysis complete", state="complete", expanded=False
                )

            except Exception as e:
                final_answer = "System error occurred."
                agent_steps = []
                st.error(f"Error: {str(e)}")
                status_box.update(label="Analysis failed", state="error")

        # Render UI components
        render_agent_thoughts(agent_steps)
        st.markdown(final_answer)

    # Save assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": final_answer, "thoughts": agent_steps}
    )

    # Update LangChain specific memory
    st.session_state.lc_history.extend(
        [HumanMessage(content=prompt), AIMessage(content=final_answer)]
    )
