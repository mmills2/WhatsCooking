from .agent import Agent
from agent_state import AgentState

POST_LIST_DISPLAY_PROMPT = """You are a manager deciding what action to take based on a user message. The user will say \
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

class ShowDishesAgent(Agent):
    def __init__(self):
        pass

    def run(self, state: AgentState):
        dishesToShow = state['dishesToShow']
        print("\nHere are some dishes:")
        for x in range(min(len(dishesToShow), state['maxRecommendations'])):
            print(" " + dishesToShow[x])

        userDecision = super().question_user("\nWould you like to learn more about one of these dishes, see more dishes, or change your preferences?", POST_LIST_DISPLAY_PROMPT)

        return {"userDecision": userDecision}