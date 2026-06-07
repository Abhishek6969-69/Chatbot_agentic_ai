
from langgraph.graph import StateGraph,START,END
from typing import TypedDict
from pydantic import BaseModel, Field
from typing import Literal,Annotated
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
load_dotenv()
class Chatstate(TypedDict):
    message: Annotated[list[BaseMessage], add_messages]

# model instance at module level
model = ChatGroq(model="llama-3.1-8b-instant")

def chat_node(state: Chatstate):
    # Pass the entire conversation history to the model, not just the last message
    response = model.invoke(state["message"])
    # add to the state and return as AIMessage
    return {"message": [AIMessage(content=response.content)]}
checkpointer=MemorySaver()
graph=StateGraph(Chatstate)
graph.add_node("chat_node",chat_node)
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)
chat=graph.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    thread_id='1'
    while True:
        user_input = input("User: ")
        print("User:", user_input)  # Debugging statement
        if user_input.lower() in ['exit', 'quit','bye']:
            print("Exiting the chat.")
            break
        config={
            'configurable':{
                'thread_id': thread_id
            }
        }
        response=chat.invoke({'message':[HumanMessage(content=user_input)]}, config)
        # Print only the AI's last response (the newly generated one)
        print("AI:", response['message'][-1].content)
        print()  # Add blank line for readability