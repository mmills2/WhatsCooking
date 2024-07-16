# necessary imports
from .agent import Agent # parent class for agents
from agent_state import AgentState # stores input and output data for agent

# system prompt
# output style defined in prompt defines what fields in UserDecision to fill
POST_SHOW_DISHES_PROMPT = """You are a manager deciding what action to take based on a user message. The user will say \
something similar to one of three things:
- They would like to learn more about a certain food dish
- They would like to see more food dishes
- They would like to change their food dish preferences
Based on their message, decide which of these three options they would like to do. Based on your decision, reply with one \
of these three options: 

{'decision': "researchDish",
'foodDish': <food dish name>}

{'decision': "moreDishes"}

{'decision': "changePreferences"}

If they would like to learn more about a dish but don't specify a food, ask them what dish they want to learn more about. \
If their message does not align with any of these options, tell the user you do not understand their response and kindly ask to \
please choose one of the options. In both of these cases, reply with:

{'decision': "insufficientResponse",
'clarifyingRespone': <message to user>}
"""

# show dishes agent
class ShowDishesAgent(Agent): # inherits Agent class
    def __init__(self): # no data to initialize on initialization 
        pass

    # shows maxRecommendations number of dishes and questions user if they want to learn more about a dish, see more like dishes, or change their food preferences
    def run(self, state: AgentState):

        dishesToShow = state['dishesToShow']
        print("\nHere are some dishes:")

        # prints either maxRecommendations dishes or however many is left in the list if their are less than maxRecommendations
        for x in range(min(len(dishesToShow), state['maxRecommendations'])):
            print(" " + dishesToShow[x])

        questionToUser = "\nWould you like to learn more about one of these dishes, see more dishes, or change your preferences?"
        userDecision = super().question_user(questionToUser, POST_SHOW_DISHES_PROMPT) # questions user with method from parent Agent class and returns validated user answer

        # returned to AgentState
        return {"userDecision": userDecision}