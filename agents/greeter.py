# necessary imports
from .agent import Agent # parent class for agents
from agent_state import AgentState # stores input and output data for agent

# system prompt
# output style defined in prompt defines what fields in UserDecision to fill
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

# greeter agent
class GreeterAgent(Agent): # inherits Agent class
    def __init_(self): # no data to initialize on initialization 
        pass

    # greets the user and gets the user's food preferences - runs when node is called
    def run(self, state: AgentState): # AgentState provided by StateGraph
        questionToUser = "Hello! What kind of food are you in the mood for today? If you're not sure, that's totally okay. Do you have any preferences such as cuisine type (Italian, Mexican, Asian), dietary restrictions (vegetarian, gluten-free), or specific ingredients you'd like to include?"
        userDecision = super().question_user(questionToUser, GREETER_PROMPT) # questions user with method from parent Agent class and returns validated user answer
        return {"preferences": userDecision.preferences}
