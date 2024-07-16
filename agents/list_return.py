# necessary imports
from .agent import Agent # parent class for agents
from agent_state import AgentState # stores input and output data for agent

# system prompt
# output style defined in prompt defines what fields in UserDecision to fill
LIST_RETURN_PROMPT = """You are a manager deciding what action to take based on a user message. Ask the user if they \
would like to return to the list of dishes. Only accept definitive answers (no maybes or not sure or etc). If they give \
an insufficient answer, kindly ask them to please choose yes or no and repeat the question. Reply with one of the following \
outputs based on the user's answer:

{'decision': "yes"}

{'decision': "no"}

{'decision': "insufficientResponse",
'clarifyingRespone': <message to user>}
"""

# list return agent
class ListReturnAgent(Agent): # inherits Agent class
    def __init__(self): # no data to initialize on initialization
        pass

    # questions the user if they want to return to the list of dishes previously shown
    def run(self, state: AgentState):

        questionToUser = "\nWould you like to return to the list of dishes?"
        userDecision = super().question_user(questionToUser, LIST_RETURN_PROMPT) # questions user with method from parent Agent class and returns validated user answer

        # returned to AgentState
        return {"userDecision": userDecision}

# next node: based on user answer either show_dishes or END node