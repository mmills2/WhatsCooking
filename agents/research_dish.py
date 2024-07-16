from .agent import Agent
from agent_state import AgentState
from structured_outputs import Queries
from tavily import TavilyClient
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import os

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

tavily = TavilyClient(api_key = os.environ["TAVILY_API_KEY"])

RESEARCH_DISH_PROMPT = """You are a researcher with the task of researching a specific food dish. You must find a \
description and recipe for the food dish. You may be given some preferences. Generate a list of search queries to find \
this information on the given food dish. If you are given preferences, keep them in mind when gernerating the queries. \
Only generate {} query(ies)."""

class ResearchDishAgent(Agent):
    def __init__(self):
        pass

    def run(state: AgentState):
        generatedQueries = model.with_structured_output(Queries).invoke([
            SystemMessage(content = RESEARCH_DISH_PROMPT.format(state['numDishResearchQueries'])),
            HumanMessage(content = f"Food dish: {state['userDecision'].foodDish}\nPreferences: {state['preferences']}")
        ])
        dishResearchResults = []
        for generatedQuery in generatedQueries.queriesList:
            searchResults = tavily.search(query = generatedQuery, max_results = state['maxDishResearchResults'])
            for searchResult in searchResults['results']:
                dishResearchResults.append(searchResult['content'])
        return {"dishResearchResults": dishResearchResults}
