import streamlit as st
from langgraph_backend import chat
from langchain_core.messages import HumanMessage

st.set_page_config(layout="wide")

config = {
    "configurable": {
        "thread_id": "1"
    }
}

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# Display old messages
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input box
user_input = st.chat_input("Your message:")

if user_input:
    # Show user message
    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    # Invoke LangGraph
    response = chat.invoke(
        {"message": [HumanMessage(content=user_input)]},
        config=config
    )

    ai_response = response["message"][-1].content

    # Store AI message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_response}
    )

    # Display AI message
    with st.chat_message("assistant"):
        st.write(ai_response)