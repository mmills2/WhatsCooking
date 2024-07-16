from .agent import Agent
from agent_state import AgentState

GREETER_PROMPT = """You are a professional recipe recommender inquiring about what kind of recipe the user \
would like to cook. Make sure to greet the user. You must ask what kind of food they are in the mood for. Tell \
the user if they do not know what they are in the mood for that is ok. Ask if the user has any other preferences \
and give some examples of types of preferences. Don't say anything after asking for preferences. If the user gives \
preferences, make sure they are food related. If the preferences are food related or they have no preferences, respond \
with the following output:

{'decision': "valid",
'preferences': <user preferences>}

If the preferences are not food related, tell the person sorry and kindly say you can only accept food related preferences. \
Respond with the following output:

{'decision': "insufficientResponse",
'clarifyingRespone': <message to user>}
"""

class GreeterAgent(Agent):
    def __init_(self):
        pass

    def run(self, state: AgentState):
        userDecision = Agent.question_user(self, "Hello! What kind of food are you in the mood for today? If you're not sure, that's totally okay. Do you have any preferences such as cuisine type (Italian, Mexican, Asian), dietary restrictions (vegetarian, gluten-free), or specific ingredients you'd like to include?", GREETER_PROMPT)
        return {"userDecision": userDecision, "preferences": userDecision.preferences}
