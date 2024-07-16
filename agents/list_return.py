from .agent import Agent
from agent_state import AgentState

LIST_RETURN_PROMPT = """You are a manager deciding what action to take based on a user message. Ask the user if they \
would like to return to the list of dishes. Only accept definitive answers (no maybes or not sure or etc). If they give \
an insufficient answer, kindly ask them to please choose yes or no and repeat the question. Reply with one of the following \
outputs based on the user's answer:

{'decision': "yes"}

{'decision': "no"}

{'decision': "insufficientResponse",
'clarifyingRespone': <message to user>}
"""

class ListReturnAgent(Agent):
    def __init__(self):
        pass

    def run(self, state: AgentState):

        userDecision = super().question_user("\nWould you like to return to the list of dishes?", LIST_RETURN_PROMPT)

        return {"userDecision": userDecision}