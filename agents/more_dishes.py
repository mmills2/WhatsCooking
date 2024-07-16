from .agent import Agent
from agent_state import AgentState

class MoreDishesAgent(Agent):
    def __init__(self):
        pass

    def run(self, state: AgentState):
        dishesToShow = state['dishesToShow']
        dishesSeen = state['dishesSeen'] or []
        dishesSeen = dishesSeen + dishesToShow[:min(len(dishesToShow), state['maxRecommendations'])]
        for i in range(min(len(dishesToShow), state['maxRecommendations'])):
            del dishesToShow[0]
        return {"dishesToShow": dishesToShow, "dishesSeen": dishesSeen}