from typing import TypedDict, List
from structured_outputs import UserDecision

# stores inputs and outputs for nodes
class AgentState(TypedDict):
    userDecision: UserDecision
    preferences: str
    dishSearchResults: List[str]
    maxDishSearchResults: int
    dishesFromSearch: List[str]
    dishesSeen: List[str]
    dishesToShow: List[str]
    domainsVisited: List[str]
    maxRecommendations: int
    dishResearchResults: List[str]
    maxDishResearchResults: int