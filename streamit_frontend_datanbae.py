import streamlit as st
from langgraph_backend_sqlite import chat,retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid


# ********************************utility functions***********************
def generate_thread_id():
    return str(uuid.uuid4())
def reset_chat():
    thread_id=generate_thread_id()
    st.session_state["thread_id"]=thread_id
     
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"]=[]

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)
def load_conversation(thread_id):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    try:
        state = chat.get_state(config=config)
        return state.values.get("message", [])
    except:
        return []
st.set_page_config(layout="wide")



if "message_history" not in st.session_state:
    st.session_state["message_history"] = []
if "thread_id" not in st.session_state:
    st.session_state["thread_id"]=generate_thread_id()
if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"]=retrieve_all_threads()
add_thread(st.session_state["thread_id"])
config = {
    "configurable": {
        "thread_id": st.session_state["thread_id"],
        "metadata":{
            "thread_id": st.session_state["thread_id"]
        },
        "run_name":"chat_turn"
    }
}

# ***********sidebarui****************
st.sidebar.title("Langraph Chatbot")
if st.sidebar.button("Start new chat"):
    reset_chat()
   
st.sidebar.header("My conversations")
for thread in st.session_state["chat_threads"][::-1]:
    conversation = load_conversation(thread)
    title = (
        " ".join(conversation[-1].content.split()[:10])
        if conversation
        else "Empty conversation"
    )

    if st.sidebar.button(title, key=thread):
        st.session_state["thread_id"] = thread
        messages = load_conversation(thread)
        temp_messages = []
        for message in messages:
            if hasattr(message, 'content'):
                temp_messages.append({"role": "assistant", "content": message.content})
            else:
                temp_messages.append({"role": "user", "content": message.content})
        st.session_state["message_history"] = temp_messages




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

    # Display AI message with streaming
    with st.chat_message("assistant"):
        # Stream the response
        full_response = ""
        placeholder = st.empty()
        
        for event in chat.stream(
            {"message": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="values",
        ):
            if "message" in event:
                # Get the last message (AI response)
                last_message = event["message"][-1]
                if hasattr(last_message, 'content'):
                    full_response = last_message.content
                    placeholder.write(full_response)
        
    # Store AI message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": full_response}
    )
