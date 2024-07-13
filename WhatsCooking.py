# loads environment variables
from dotenv import load_dotenv
_ = load_dotenv()

# necessary imports
import os
import operator
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from tavily import TavilyClient
from urllib.parse import urlparse

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# used to save states of graph to allow returning to previous states and modifying states
memory = SqliteSaver.from_conn_string(":memory:")

# initializes Tavily search engine tool
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# stores list of queries and provides structured output for generating queries
class Queries(BaseModel):
    queriesList: List[str]

# stores list of dishes and provides structured output for forming list
class Dishes(BaseModel):
    dishesList: List[str]

# store user's decision after being shown food dishes
class UserDecision(BaseModel):
    decision: str
    foodDish: Optional[str]
    clarifyingRespone: Optional[str]

# stores inputs and outputs for nodes
class AgentState(TypedDict):
    preferences: str
    dishSearchResults: List[str]
    dishesFromSearch: List[str]
    dishesSeen: List[str]
    dishesToShow: List[str]
    domainsVisited: List[str]
    maxRecommendations: int
    userDecision: UserDecision
    dishResearchResults: List[str]

# system prompts for agents
GREETER_PROMPT = """You are a professional recipe recommender inquiring about what kind of recipe the user \
would like to cook. Make sure to greet the user. You must ask what kind of food they are in the mood for. Tell \
the user if they do not know what they are in the mood for that is ok. Ask if the user has any other preferences \
and give some examples of types of preferences. Don't say anything after asking for preferences. If the user gives preferences, \
make sure they are food related. If the preferences are food related or they have no preferences, respond with just \
the word "valid". If the preferences are not food related, tell the user sorry and kindly say you can only accept food \
related preferences."""

DISH_SEARCH_PROMPT = """You are a researcher with the task of finding food recipes. You may be given preferences \
about the types of food recipes to find. Generate a list of search queries to find relevant food recipes. Only generate \
1 query."""

DISH_LIST_FORMER_PROMPT = """You are a documenter with the task of documenting food dishes. You must record the \
food dish name. Make sure the food dish name you record is a name of an actual food. Do not include any information \
in the dish name besides the name of the dish. Do not include the word recipe in the dish name. Capitalize the dish \
names as if they were a title. Return a list of food dish names based on the information provided.""" 

POST_LIST_DISPLAY_PROMPT = """You are a manager deciding what action to take based on a user message. The user will say \
something similar to one of three things:
- They would like to learn more about a certain food dish
- They would like to see more food dishes
- They would like to change their food dish preferences
Based on their message, decide which of these three options they would like to do. Based on your decision, reply with one \
of these three options: 

{'decision': "researchDish",
'foodDish': <food dish name>}

{'decision': "seeMore"}

{'decision': "changePreference"}

If they would like to learn more about a dish but don't specify a food, ask them what dish they want to learn more about. \
If their message does not align with any of these options, tell the user you do not understand their response and kindly ask to \
please choose one of the options. In both of these cases, reply with:

{'decision': "insufficientResponse",
'clarifyingRespone': <message to user>}
"""

RESEARCH_DISH_PROMPT = """You are a researcher with the task of researching a specific food dish. You must find a description and \
recipe for the food dish. Generate a list of search queries to find this information on the given food dish. Only generate 2 queries."""

SHOW_DISH_PROMPT = """You are a proffesional writer for a cook book. You will be given information about a specific food dish. You \
must write a short description on the food dish. Then you must write step by step instructions on how to make the food dish."""

# greeter agent
def greeter_node(state: AgentState):

    messages = [SystemMessage(content = GREETER_PROMPT)]
    aiResponse = ""
    userInput = ""
    while(aiResponse != "valid"):
        response = model.invoke(messages)
        aiResponse = response.content
        if(aiResponse != "valid"):
            print(aiResponse)
            messages.append(AIMessage(content = aiResponse))
            userInput = input(": ")
            messages.append(HumanMessage(content = userInput))
    return {"preferences": userInput}

# dish searcher agent
def dish_searcher_node(state: AgentState):
    generatedQueries = model.with_structured_output(Queries).invoke([
        SystemMessage(content = DISH_SEARCH_PROMPT),
        HumanMessage(content = f"My food dish preferences are: {state['preferences']}")
    ])
    dishSearchResults = []
    domainsVisited = state['domainsVisited'] or []
    for generatedQuery in generatedQueries.queriesList:
        searchResults = tavily.search(query = generatedQuery, max_results = 1, exclude_domains = state['domainsVisited'])
        for searchResult in searchResults['results']:
            domainsVisited.append(urlparse(searchResult['url']).netloc)
            dishSearchResults.append(searchResult['content'])
    return {"dishSearchResults": dishSearchResults, "domainsVisited": domainsVisited}

# dish list former agent
def dish_list_former_node(state: AgentState):
    dishesResearch = "\n\n".join(state['dishSearchResults'])
    dishes = model.with_structured_output(Dishes).invoke([
        SystemMessage(content = DISH_LIST_FORMER_PROMPT),
        HumanMessage(content = dishesResearch)
    ])
    dishesToShow = list(set(dishes.dishesList) - set(state['dishesSeen'] or []))
    return {"dishesFromSearch": dishes.dishesList, "dishesToShow": dishesToShow}

# dishes to show is greater than zero check
def check_dishes_to_show(state: AgentState):
    return len(state['dishesToShow']) > 0

# show dishes node
def show_dishes_node(state: AgentState):
    dishesToShow = state['dishesToShow']
    print("Here are some dishes:")
    for x in range(min(len(dishesToShow), state['maxRecommendations'])):
        print(dishesToShow[x])

    questionToUser = "Would you like to learn more about one of these dishes, see more dishes, or change your preferences?"
    print(questionToUser)

    messages = [
        SystemMessage(content = POST_LIST_DISPLAY_PROMPT),
        AIMessage(content = questionToUser)
    ]

    userDecision = UserDecision(decision = "insufficientResponse")
    while(userDecision.decision == "insufficientResponse"):
        if(userDecision.clarifyingRespone):
            print(userDecision.clarifyingRespone)
            messages.append(AIMessage(content = userDecision.clarifyingRespone))
        userInput = input(": ")
        messages.append(HumanMessage(content = userInput))
        userDecision = model.with_structured_output(UserDecision).invoke(messages)
    return {"userDecision": userDecision}

# research dish agent
def research_dish_node(state: AgentState):
    generatedQueries = model.with_structured_output(Queries).invoke([
        SystemMessage(content = RESEARCH_DISH_PROMPT),
        HumanMessage(content = f"Food dish: {state['userDecision'].foodDish}")
    ])
    dishResearchResults = []
    for generatedQuery in generatedQueries.queriesList:
        searchResults = tavily.search(query = generatedQuery, max_results = 3)
        for searchResult in searchResults['results']:
            dishResearchResults.append(searchResult['content'])
    return {"dishResearchResults": dishResearchResults}

# builds workflow of graph from added nodes and edges
builder = StateGraph(AgentState)

# adds nodes to graph
builder.add_node("greeter", greeter_node)
builder.add_node("dish_search", dish_searcher_node)
builder.add_node("list_former", dish_list_former_node)
builder.add_node("show_dishes", show_dishes_node)
builder.add_node("research_dish", research_dish_node)

# adds edges between nodes
builder.add_edge("greeter", "dish_search")
builder.add_edge("dish_search", "list_former")
builder.add_edge("show_dishes", "research_dish")
builder.add_edge("research_dish", END)

# adds conditional edges
builder.add_conditional_edges("list_former", check_dishes_to_show, {True: "show_dishes", False: "dish_search"})

# sets start of graph
builder.set_entry_point("greeter")

# compiles graph so application can be run
graph = builder.compile(checkpointer = memory)

# stores history of graph states
thread = {"configurable": {"thread_id": "1"}}

# runs the application and prints out the AgentState after each node runs
for event in graph.stream({"maxRecommendations": 10}, thread):
    print(event)