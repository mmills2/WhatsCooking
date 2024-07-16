from .agent import Agent
from agent_state import AgentState
from structured_outputs import Queries
from urllib.parse import urlparse
from tavily import TavilyClient
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import os

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

tavily = TavilyClient(api_key = os.environ["TAVILY_API_KEY"])

DISH_SEARCH_PROMPT = """You are a researcher with the task of finding food recipes. You may be given preferences \
about the types of food recipes to find. Generate a list of search queries to find relevant food recipes. Only generate \
{} query(ies)."""

class DishSearchAgent(Agent):
    def __init__(self):
        pass

    def run(self, state: AgentState):
        generatedQueries = model.with_structured_output(Queries).invoke([
            SystemMessage(content = DISH_SEARCH_PROMPT.format(state['numDishSearchQueries'])),
            HumanMessage(content = f"My food dish preferences are: {state['preferences']}")
        ])
        dishSearchResults = []
        domainsVisited = state['domainsVisited'] or []
        for generatedQuery in generatedQueries.queriesList:
            searchResults = tavily.search(query = generatedQuery, max_results = state['maxDishSearchResults'], exclude_domains = state['domainsVisited'])
            for searchResult in searchResults['results']:
                domainsVisited.append(urlparse(searchResult['url']).netloc)
                dishSearchResults.append(searchResult['content'])
        return {"dishSearchResults": dishSearchResults, "domainsVisited": domainsVisited}