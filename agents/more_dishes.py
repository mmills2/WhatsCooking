# necessary imports
from .agent import Agent # parent class for agents
from agent_state import AgentState # stores input and output data for agent

# more dishes agent
class MoreDishesAgent(Agent): # inherits Agent class
    def __init__(self): # no data to initialize on initialization 
        pass

    # removes just shown dishes from dishesToShow and adds them to dishesSeen - runs when node is called
    def run(self, state: AgentState):

        # lists of dishes that will be returned
        dishesToShow = state['dishesToShow']
        dishesSeen = state['dishesSeen'] or []

        # adds dishes from index 0 to either maxRecommendations or however many is left in the list if their are less than maxRecommendations to dishesSeen - all the dishes that were just shown in show_dishes
        dishesSeen = dishesSeen + dishesToShow[:min(len(dishesToShow), state['maxRecommendations'])]

        # removes just shown dishes from dishesToShow
        for i in range(min(len(dishesToShow), state['maxRecommendations'])):
            del dishesToShow[0]
        
        # returned to AgentState
        return {"dishesToShow": dishesToShow, "dishesSeen": dishesSeen}

# next node: if dishesToShow is empty then dish_search, otherwise show_dishes