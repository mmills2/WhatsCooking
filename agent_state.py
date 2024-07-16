from typing import TypedDict, List
from structured_outputs import UserDecision

# stores inputs and outputs for nodes
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