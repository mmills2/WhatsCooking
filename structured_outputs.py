from typing import List, Optional
from langchain_core.pydantic_v1 import BaseModel

# store user's decision after being shown food dishes
class UserDecision(BaseModel):
    decision: str
    preferences: Optional[str]
    foodDish: Optional[str]
    clarifyingRespone: Optional[str]

# stores list of queries and provides structured output for generating queries
class Queries(BaseModel):
    queriesList: List[str]

# stores list of dishes and provides structured output for forming list
class Dishes(BaseModel):
    dishesList: List[str]