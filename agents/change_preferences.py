# necessary imports
from .agent import Agent # parent class for agents
from agent_state import AgentState # stores input and output data for agent

# system prompt
# output style defined in prompt defines what fields in UserDecision to fill
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

# change preferences agent
class ChangePreferencesAgent(Agent): # inherits Agent class
    def __init__(self): # no data to initialize on initialization
        pass

    # gets the user's new food preferences and resets dishesSeen and domainsVisited - runs when node is called
    def run(self, state: AgentState):

        questionToUser = "\nWhat are your new food preferences?"
        userDecision = super().question_user(questionToUser, CHANGE_PREFERENCES_PROMPT) # questions user with method from parent Agent class and returns validated user answer

        # resets dishesSeen and domainsVisited to allow for best results with new food preferences
        dishesSeen = []
        domainsVisited = []

        # returned to AgentState
        return {"preferences": userDecision.preferences, "dishesSeen": dishesSeen, "domainsVisited": domainsVisited}

# next node: dish_search