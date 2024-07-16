from .agent import Agent
from agent_state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import os

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

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

class ShowDishAgent(Agent):
    def __init__(self):
        pass

    def run(self, state: AgentState):
        dishResearch = "\n\n".join(state['dishResearchResults'])
        response = model.invoke([
            SystemMessage(content = SHOW_DISH_PROMPT),
            HumanMessage(content = dishResearch)])
        print("\n" + response.content)