# necessary imports
from .agent import Agent # parent class for agents
from agent_state import AgentState # stores input and output data for agent
from structured_outputs import Dishes # schema used for storing food dishes
from langchain_core.messages import SystemMessage, HumanMessage # used to define message types to AI model
from langchain_openai import ChatOpenAI # OpenAI model

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

# system prompt
DISH_LIST_FORMER_PROMPT = """You are a documenter with the task of documenting food dishes. You must record the \
food dish name. Make sure the food dish name you record is a name of an actual food. You may be given preferences. \
If you are given prefernces, only record the food dish name if the food dish aligns with the given prefences. Do not \
include any information in the dish name besides the name of the dish. Do not include the word recipe in the dish name. \
Capitalize the dish names as if they were a title. Return a list of food dish names based on the information provided."""

# list former agent
class ListFormerAgent(Agent):# inherits Agent class
    def __init__(self): # no data to initialize on initialization 
        pass

    # forms a list of food dish names to show user - runs when node is called
    def run(self, state: AgentState):
        
        # concatenates food dish search results into one string
        dishesResearch = "\n\n".join(state['dishSearchResults'])

        # invokes AI and returns list of dishes in Dishes schema
        dishes = model.with_structured_output(Dishes).invoke([
            SystemMessage(content = DISH_LIST_FORMER_PROMPT),
            HumanMessage(content = f"Food dish prefences: {state['preferences']}\n{dishesResearch}")
        ])

        # removes any dishes already seen by user to prevent seeing duplicate dishes
        dishesToShow = list(set(dishes.dishesList) - set(state['dishesSeen'] or []))

        # returned to AgentState
        return {"dishesFromSearch": dishes.dishesList, "dishesToShow": dishesToShow}