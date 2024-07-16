from .agent import Agent
from agent_state import AgentState

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

class ChangePreferencesAgent(Agent):
    def __init__(self):
        pass

    def run(self, state: AgentState):

        userDecision = super().question_user("\nWhat are your new food preferences?", CHANGE_PREFERENCES_PROMPT)

        dishesSeen = []
        domainsVisited = []
        return {"preferences": userDecision.preferences, "dishesSeen": dishesSeen, "domainsVisited": domainsVisited}