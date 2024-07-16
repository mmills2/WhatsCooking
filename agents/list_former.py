from .agent import Agent
from agent_state import AgentState
from structured_outputs import Dishes
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import os

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

DISH_LIST_FORMER_PROMPT = """You are a documenter with the task of documenting food dishes. You must record the \
food dish name. Make sure the food dish name you record is a name of an actual food. You may be given preferences. \
If you are given prefernces, only record the food dish name if the food dish aligns with the given prefences. Do not \
include any information in the dish name besides the name of the dish. Do not include the word recipe in the dish name. \
Capitalize the dish names as if they were a title. Return a list of food dish names based on the information provided."""

class ListFormerAgent(Agent):
    def __init__(self):
        pass

    def run(self, state: AgentState):
        dishesResearch = "\n\n".join(state['dishSearchResults'])
        dishes = model.with_structured_output(Dishes).invoke([
            SystemMessage(content = DISH_LIST_FORMER_PROMPT),
            HumanMessage(content = f"Food dish prefences: {state['preferences']}\n{dishesResearch}")
        ])
        dishesToShow = list(set(dishes.dishesList) - set(state['dishesSeen'] or []))
        return {"dishesFromSearch": dishes.dishesList, "dishesToShow": dishesToShow}