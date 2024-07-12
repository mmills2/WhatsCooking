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

# stores inputs and outputs for nodes
class AgentState(TypedDict):
    preferences: str
    dishSearchResults: List[str]

# stores list of queries and is provides structured output for generating queries
class Queries(BaseModel):
    queriesList: List[str]

# system prompts for agents
GREETER_PROMPT = """You are a professional recipe recommender inquiring about what kind of recipe the user \
would like to cook. Make sure to greet the user. You must ask what kind of food they are in the mood for. Tell \
the user if they do not know what they are in the mood for that is ok. Ask if the user has any other preferences. \
Don't say anything after asking for preferences."""

DISH_SEARCH_PROMPT = """You are a researcher with the task of finding food dishes. You may be given preferences \
about the types of food dishes to find. Generate a list of search queries to find relevant food dishes. Only generate \
1 query."""

# greeter agent
def greeter_node(state: AgentState):
    response = model.invoke([
        SystemMessage(content = GREETER_PROMPT)
    ])
    print(response.content)
    userInput = input(": ")
    return {"preferences": userInput}

# dish searcher agent
def dish_searcher_node(state: AgentState):
    generatedQueries = model.with_structured_output(Queries).invoke([
        SystemMessage(content = DISH_SEARCH_PROMPT),
        HumanMessage(content = f"My food dish preferences are: {state['preferences']}")
    ])
    dishSearchResults = []
    for generatedQuery in generatedQueries.queriesList:
        searchResults = tavily.search(query = generatedQuery, max_results = 1)
        for searchResult in searchResults['results']:
            dishSearchResults.append(searchResult['content'])
    return {"dishSearchResults": dishSearchResults}

# builds workflow of graph from added nodes and edges
builder = StateGraph(AgentState)

# adds nodes to graph
builder.add_node("greeter", greeter_node)
builder.add_node("dish_search", dish_searcher_node)

# adds edges between nodes
builder.add_edge("greeter", "dish_search")
builder.add_edge("dish_search", END)

# sets start of graph
builder.set_entry_point("greeter")

# compiles graph so application can be run
graph = builder.compile(checkpointer = memory)

# stores history of graph states
thread = {"configurable": {"thread_id": "1"}}

# runs the application and prints out the AgentState after each node runs
for event in graph.stream({"preferences": None}, thread):
    print(event)