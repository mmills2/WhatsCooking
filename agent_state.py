# necessary imports
from typing import TypedDict, List # used for variable type validation
from structured_outputs import UserDecision # used as value in AgentState

# state schema for StateGraph that stores input and output data for nodes
class AgentState(TypedDict):
    userDecision: UserDecision
    preferences: str
    numDishSearchQueries: int
    dishSearchResults: List[str]
    maxDishSearchResults: int
    dishesFromSearch: List[str]
    dishesSeen: List[str]
    dishesToShow: List[str]
    domainsVisited: List[str]
    maxRecommendations: int
    numDishResearchQueries: int
    dishResearchResults: List[str]
    maxDishResearchResults: int