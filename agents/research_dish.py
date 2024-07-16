# necessary imports
from .agent import Agent # parent class for agents
from agent_state import AgentState # stores input and output data for agent
from structured_outputs import Queries # schema used for storing generated search queries
from tavily import TavilyClient # search engine tool
from langchain_core.messages import SystemMessage, HumanMessage # used to define message types to AI model
from langchain_openai import ChatOpenAI # OpenAI model
import os # used to import Tavily api key

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

# initializes Tavily search tool
tavily = TavilyClient(api_key = os.environ["TAVILY_API_KEY"])

# system prompt
RESEARCH_DISH_PROMPT = """You are a researcher with the task of researching a specific food dish. You must find a \
description and recipe for the food dish. You may be given some preferences. Generate a list of search queries to find \
this information on the given food dish. If you are given preferences, keep them in mind when gernerating the queries. \
Only generate {} query(ies)."""

# research dish agent
class ResearchDishAgent(Agent): # inherits Agent class
    def __init__(self): # no data to initialize on initialization 
        pass

    # generates search queries to research specific food dish chosen by user and returns the results - runs when node is called
    def run(self, state: AgentState):

        # invokes AI and returns generated queries in Queries schema
        generatedQueries = model.with_structured_output(Queries).invoke([
            SystemMessage(content = RESEARCH_DISH_PROMPT.format(state['numDishResearchQueries'])), # inserts numDishResearchQueries into empty curly braces in RESEARCH_DISH_PROMPT
            HumanMessage(content = f"Food dish: {state['userDecision'].foodDish}\nPreferences: {state['preferences']}")
        ])

        # lists of search results that will be returned
        dishResearchResults = []

        # for each search query will return maxDishResearchResults number of results
        for generatedQuery in generatedQueries.queriesList:
            searchResults = tavily.search(query = generatedQuery, max_results = state['maxDishResearchResults']) # calls Tavily search engine with query
            
            # for each search result adds the content of the result to dishResearchResults
            for searchResult in searchResults['results']:
                dishResearchResults.append(searchResult['content'])
        
        # returned to AgentState
        return {"dishResearchResults": dishResearchResults}
