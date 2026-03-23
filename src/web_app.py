# src/web_app.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.llm_client import LLMClient
from src.prompts import get_system_prompt, list_personas
from src.utils import start_history, append_user, append_assistant, truncate_history
import json

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance Chat",
    page_icon="💰",
    layout="centered",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💰 Finance Chat")
    st.markdown("---")

    persona = st.selectbox(
        "Choose your advisor",
        options=list_personas(),
        format_func=lambda x: x.capitalize(),
    )

    st.markdown("### About each persona")
    descriptions = {
        "professional": "Clear, practical tips on budgeting, saving, and investing.",
        "creative": "Money lessons through stories, metaphors, and analogies.",
        "technical": "Formulas, calculations, and step-by-step breakdowns.",
    }
    st.info(descriptions.get(persona, ""))

    st.markdown("---")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

    # Export conversation
    if st.session_state.get("messages"):
        st.markdown("### Export")
        txt = "\n\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in st.session_state.messages
        )
        st.download_button("Download as TXT", txt, file_name="conversation.txt")
        st.download_button(
            "Download as JSON",
            json.dumps(st.session_state.messages, indent=2),
            file_name="conversation.json",
        )

# ── Session state init ────────────────────────────────────────────────────────
# session_state persists across reruns — this is how Streamlit keeps chat history
if "messages" not in st.session_state:
    st.session_state.messages = []        # what we display (role + content dicts)

if "history" not in st.session_state:
    st.session_state.history = []         # what we send to the LLM (includes system prompt)

if "current_persona" not in st.session_state:
    st.session_state.current_persona = persona

# Reset history if persona changes mid-conversation
if st.session_state.current_persona != persona:
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.current_persona = persona

# Init LLM history with system prompt if empty
if not st.session_state.history:
    system_prompt = get_system_prompt(persona)
    st.session_state.history = start_history(system_prompt)

# ── Main chat area ────────────────────────────────────────────────────────────
st.title("Personal Finance Guide")
st.caption(f"Talking to: **{persona.capitalize()}** persona")

# Render all past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input — st.chat_input pins to the bottom of the page
if user_input := st.chat_input("Ask a finance question..."):
    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Add to LLM history and truncate to avoid huge context
    append_user(st.session_state.history, user_input)
    st.session_state.history = truncate_history(st.session_state.history)

    # Call the LLM and show the response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                client = LLMClient()
                reply = client.chat(st.session_state.history)
            except Exception as e:
                reply = f"Sorry, something went wrong: {e}"
        st.markdown(reply)

    append_assistant(st.session_state.history, reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})