# loads environment variables
from dotenv import load_dotenv
_ = load_dotenv()

# necessary imports
import os
import configparser
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from tavily import TavilyClient
from urllib.parse import urlparse

from agent_state import AgentState
from agents import *

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

# used to save states of graph to allow returning to previous states and modifying states
memory = SqliteSaver.from_conn_string(":memory:")

# initializes Tavily search engine tool
tavily = TavilyClient(api_key = os.environ["TAVILY_API_KEY"])

# store user's decision after being shown food dishes
class UserDecision(BaseModel):
    decision: str
    preferences: Optional[str]
    foodDish: Optional[str]
    clarifyingRespone: Optional[str]

# stores list of queries and provides structured output for generating queries
class Queries(BaseModel):
    queriesList: List[str]

# stores list of dishes and provides structured output for forming list
class Dishes(BaseModel):
    dishesList: List[str]

# system prompts for agents 

CHANGE_PREFERENCES_PROMPT = """You are a professional recipe recommender inquiring about what kind of recipe the user \
would like to cook. Ask what their new food preferences are. Don't say anything after asking for preferences. If the \
person gives preferences, make sure they are food related. If the preferences are food related or they have no preferences, \
respond with the following output:

{'decision': "valid",
'preferences': <user preferences>}

If the preferences are not food related, tell the person sorry and kindly say you can only accept food related preferences. \
Respond with the following output:

{'decision': "insufficientResponse",
'clarifyingRespone': <message to user>}
"""

SHOW_DISH_PROMPT = """You are a proffesional writer for a cook book. You will be given information about a specific food dish. You \
must write a 2-3 sentence description on the food dish. Then you must write a list of required ingredients. Then you must write step by step \
instructions on how to make the food dish. Don't say anything after the instructions. Use the below format for your output.

<2-3 sentence food description>

Ingredients:
- <ingredient 1>
- <ingredient 2>
...

Instructions
1. <step 1>
2. <step 2>
...
"""

POST_SHOW_DISH_PROMPT = """You are a manager deciding what action to take based on a user message. Ask the user if they \
would like to return to the list of dishes. Only accept definitive answers (no maybes or not sure or etc). If they give \
an insufficient answer, kindly ask them to please choose yes or no and repeat the question. Reply with one of the following \
outputs based on the user's answer:

{'decision': "yes"}

{'decision': "no"}

{'decision': "insufficientResponse",
'clarifyingRespone': <message to user>}
"""

# user input validation loop
def question_user(questionToUser: str, systemPrompt: str) -> UserDecision:
    print(questionToUser)

    messages = [
        SystemMessage(content = systemPrompt),
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
    return userDecision

# greeter agent
greeter_agent = GreeterAgent()

# dish searcher agent
dish_search_agent = DishSearchAgent()

# dish list former agent
list_former_agent = ListFormerAgent()

# dishes to show is greater than zero check
def check_dishes_to_show(state: AgentState):
    return len(state['dishesToShow']) > 0

# show dishes node
show_dishes_agent = ShowDishesAgent()

# checks if user wants to learn more about a dish, see more dishes, or change their preferences
def check_post_show_dishes_decision(state: AgentState):
    return state['userDecision'].decision

# research dish agent
research_dish_agent = ResearchDishAgent()

# adjust dish lists node
more_dishes_agent = MoreDishesAgent()

# change preferences agent
def change_preferences_node(state: AgentState):

    userDecision = question_user("\nWhat are your new food preferences?", CHANGE_PREFERENCES_PROMPT)

    dishesSeen = []
    domainsVisited = []
    return {"preferences": userDecision.preferences, "dishesSeen": dishesSeen, "domainsVisited": domainsVisited}

# show dish agent
def show_dish_node(state: AgentState):
    dishResearch = "\n\n".join(state['dishResearchResults'])
    response = model.invoke([
        SystemMessage(content = SHOW_DISH_PROMPT),
        HumanMessage(content = dishResearch)])
    print("\n" + response.content)

# post show dish agent
def post_show_dish_node(state: AgentState):

    userDecision = question_user("\nWould you like to return to the list of dishes?", POST_SHOW_DISH_PROMPT)

    return {"userDecision": userDecision}

# checks if user wants to return to dishes after view a specific dish
def check_post_show_dish_decision(state: AgentState):
    return state['userDecision'].decision

# builds workflow of graph from added nodes and edges
builder = StateGraph(AgentState)

# adds nodes to graph
builder.add_node("greeter", greeter_agent.run)
builder.add_node("dish_search", dish_search_agent.run)
builder.add_node("list_former", list_former_agent.run)
builder.add_node("show_dishes", show_dishes_agent.run)
builder.add_node("research_dish", ResearchDishAgent.run)
builder.add_node("more_dishes", more_dishes_agent.run)
builder.add_node("change_preferences", change_preferences_node)
builder.add_node("show_dish", show_dish_node)
builder.add_node("post_show_dish", post_show_dish_node)

# adds edges between nodes
builder.add_edge("greeter", "dish_search")
builder.add_edge("dish_search", "list_former")
builder.add_edge("research_dish", "show_dish")
builder.add_edge("show_dish", "post_show_dish")
builder.add_edge("change_preferences", "dish_search")

# adds conditional edges
builder.add_conditional_edges("list_former", check_dishes_to_show, {True: "show_dishes", False: "dish_search"})
builder.add_conditional_edges("show_dishes", check_post_show_dishes_decision, {"researchDish": "research_dish", "moreDishes": "more_dishes", "changePreferences": "change_preferences"})
builder.add_conditional_edges("post_show_dish", check_post_show_dish_decision, {"yes": "show_dishes", "no": END})
builder.add_conditional_edges("more_dishes", check_dishes_to_show, {True: "show_dishes", False: "dish_search"})

# sets start of graph
builder.set_entry_point("greeter")

# compiles graph so application can be run
graph = builder.compile(checkpointer = memory)

config = configparser.ConfigParser()
config.read('settings.ini')

graphInput = {
    "maxDishSearchResults": config['MAXES'].getint('dishSearchResults'),
    "maxRecommendations": config['MAXES'].getint('dishRecommendations'),
    "maxDishResearchResults": config['MAXES'].getint('dishResearchResults')
}

graphConfig = {
    "recursion_limit": config['MAXES'].getint('recursion_limit'),
    "configurable": {"thread_id": "1"}
}

# runs the application and prints out the AgentState after each node runs
for event in graph.stream(graphInput, graphConfig):
    # print(event)
    pass