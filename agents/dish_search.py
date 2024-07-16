# necessary imports
from .agent import Agent # parent class for agents
from agent_state import AgentState # stores input and output data for agent
from structured_outputs import Queries # schema used for storing generated search queries
from urllib.parse import urlparse # used for retrieving domains from urls
from tavily import TavilyClient # search engine tool
from langchain_core.messages import SystemMessage, HumanMessage # used to define message types to AI model
from langchain_openai import ChatOpenAI # OpenAI model
import os # used to import Tavily api key

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

# initializes Tavily search tool
tavily = TavilyClient(api_key = os.environ["TAVILY_API_KEY"])

# system prompt
DISH_SEARCH_PROMPT = """You are a researcher with the task of finding food recipes. You may be given preferences \
about the types of food recipes to find. Generate a list of search queries to find relevant food recipes. Only generate \
{} query(ies)."""

# dish search agent
class DishSearchAgent(Agent):# inherits Agent class
    def __init__(self): # no data to initialize on initialization 
        pass

    # generates search queries to find food dishes based on the user's preferences and returns the results - runs when node is called
    def run(self, state: AgentState):
        
        # invokes AI and returns response in Queries schema
        generatedQueries = model.with_structured_output(Queries).invoke([
            SystemMessage(content = DISH_SEARCH_PROMPT.format(state['numDishSearchQueries'])),
            HumanMessage(content = f"My food dish preferences are: {state['preferences']}")
        ])

        # lists of search results and domains visited that will be returned
        dishSearchResults = []
        domainsVisited = state['domainsVisited'] or []

        # for each search query will return maxDishSearchResults number of results and excludes previously visited domains to allow for new results when searching multiple times in a row
        for generatedQuery in generatedQueries.queriesList:
            searchResults = tavily.search(query = generatedQuery, max_results = state['maxDishSearchResults'], exclude_domains = state['domainsVisited']) # calls Tavily search engine with query
            
            # for each search result adds the domain of the result to domainsVisited and adds the content of the result to dishSearchResults
            for searchResult in searchResults['results']:
                domainsVisited.append(urlparse(searchResult['url']).netloc)
                dishSearchResults.append(searchResult['content'])

        # returned to AgentState
        return {"dishSearchResults": dishSearchResults, "domainsVisited": domainsVisited}