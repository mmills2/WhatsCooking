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
    dishesFromSearch: List[str]
    dishesSeen: List[str]
    dishesToShow: List[str]

# stores list of queries and provides structured output for generating queries
class Queries(BaseModel):
    queriesList: List[str]

# stores list of dishes and provides structured output for forming list
class Dishes(BaseModel):
    dishesList: List[str]

# system prompts for agents
GREETER_PROMPT = """You are a professional recipe recommender inquiring about what kind of recipe the user \
would like to cook. Make sure to greet the user. You must ask what kind of food they are in the mood for. Tell \
the user if they do not know what they are in the mood for that is ok. Ask if the user has any other preferences. \
Don't say anything after asking for preferences."""

DISH_SEARCH_PROMPT = """You are a researcher with the task of finding food recipes. You may be given preferences \
about the types of food recipes to find. Generate a list of search queries to find relevant food recipes. Only generate \
1 query."""

DISH_LIST_FORMER_PROMPT = """You are a documenter with the task of documenting food dishes. You must record the \
food dish name. Make sure the food dish name you record is a name of an actual food. Do not include any information \
in the dish name besides the name of the dish. Do not include the word recipe in the dish name. Capitalize the dish \
names as if they were a title. Return a list of food dish names based on the information provided."""

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
        searchResults = tavily.search(query = generatedQuery, max_results = 3)
        for searchResult in searchResults['results']:
            dishSearchResults.append(searchResult['content'])
    return {"dishSearchResults": dishSearchResults}

# dish list former agent
def dish_list_former_node(state: AgentState):
    dishesResearch = "\n\n".join(state['dishSearchResults'])
    dishes = model.with_structured_output(Dishes).invoke([
        SystemMessage(content = DISH_LIST_FORMER_PROMPT),
        HumanMessage(content = dishesResearch)
    ])
    return {"dishesFromSearch": dishes.dishesList}

# dish list comparing tool
def dish_list_comparer_node(state: AgentState):
    dishesToShow = list(set(state['dishesFromSearch']) - set(state['dishesSeen']))
    return {"dishesToShow": dishesToShow}

# dishes to show is greater than zero check
def check_dishes_to_show(state: AgentState):
    return len(state['dishesToShow']) > 0

# builds workflow of graph from added nodes and edges
builder = StateGraph(AgentState)

# adds nodes to graph
builder.add_node("greeter", greeter_node)
builder.add_node("dish_search", dish_searcher_node)
builder.add_node("list_former", dish_list_former_node)
builder.add_node("list_comparer", dish_list_comparer_node)

# adds edges between nodes
builder.add_edge("greeter", "dish_search")
builder.add_edge("dish_search", "list_former")
builder.add_edge("list_former", "list_comparer")

# adds conditional edges
builder.add_conditional_edges("list_comparer", check_dishes_to_show, {True: END, False: "dish_search"})

# sets start of graph
builder.set_entry_point("greeter")

# compiles graph so application can be run
graph = builder.compile(checkpointer = memory)

# stores history of graph states
thread = {"configurable": {"thread_id": "1"}}

# runs the application and prints out the AgentState after each node runs
for event in graph.stream({"dishesSeen": []}, thread):
    print(event)