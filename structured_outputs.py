# necessary imports
from typing import List, Optional # used for variable type validation
from langchain_core.pydantic_v1 import BaseModel # used for variable type validation

# structured output schemas for AI models to allow for consistent data output
class UserDecision(BaseModel): # store user's decision after questioning the user
    decision: str
    preferences: Optional[str]
    foodDish: Optional[str]
    clarifyingRespone: Optional[str]

class Queries(BaseModel): # stores list of queries
    queriesList: List[str]

class Dishes(BaseModel): # stores list of dishes
    dishesList: List[str]