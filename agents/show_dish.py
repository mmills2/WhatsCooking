# necessary imports
from .agent import Agent # parent class for agents
from agent_state import AgentState # stores input and output data for agent
from langchain_core.messages import SystemMessage, HumanMessage # used to define message types to AI model
from langchain_openai import ChatOpenAI # OpenAI model

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

# system prompt
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

# show dish agent
class ShowDishAgent(Agent): # inherits Agent class
    def __init__(self): # no data to initialize on initialization
        pass

    # shows a description, list of ingredients, and cooking instructions for a specific food dish - runs when node is called
    def run(self, state: AgentState):

        # concatenates food dish research results into one string
        dishResearch = "\n\n".join(state['dishResearchResults'])

        # invokes AI and returns food dish data
        response = model.invoke([
            SystemMessage(content = SHOW_DISH_PROMPT),
            HumanMessage(content = dishResearch)
        ])
        print("\n" + response.content) # prints food dish data

# next node: list_return