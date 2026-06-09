
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from pydantic import BaseModel, Field
from typing import Literal, Annotated
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

class Chatstate(TypedDict):
    message: Annotated[list[BaseMessage], add_messages]

# model instance at module level
model = ChatGroq(model="llama-3.1-8b-instant")

def chat_node(state: Chatstate):
    # Pass the entire conversation history to the model, not just the last message
    # Use stream to get streaming response
    full_response = ""
    for chunk in model.stream(state["message"]):
        full_response += chunk.content
    # add to the state and return as AIMessage
    return {"message": [AIMessage(content=full_response)]}
conn=sqlite3.connect(database="chatbot.db",check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
graph = StateGraph(Chatstate)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)
chat = graph.compile(checkpointer=checkpointer)
def retrieve_all_threads():
    all_thread = set()
    for checkpoint in checkpointer.list(None):
        all_thread.add(checkpoint.config['configurable']["thread_id"])
    return list(all_thread)

# config = {
#     "configurable": {
#         "thread_id": "1"
#     }
# }
# res=chat.invoke(
#     {"message": [HumanMessage(content="what is capital od delhi?")]},
#     config=config
# )
# print(res)
