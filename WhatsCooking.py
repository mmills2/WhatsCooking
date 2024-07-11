# loads environment variables
from dotenv import load_dotenv
_ = load_dotenv()

# necessary imports
import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from tavily import TavilyClient

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# used to save states of graph to allow returning to previous states and modifying states
memory = SqliteSaver.from_conn_string(":memory:")

# initializes Tavily search engine tool
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])