# loads environment variables (OPENAI_API_KEY & TAVILY_API_KEY)
from dotenv import load_dotenv
load_dotenv()

# necessary imports
import configparser # used for application configuration settings
from langgraph.graph import StateGraph, END # type of graph being used and end graph execution node
from langgraph.checkpoint.sqlite import SqliteSaver # used for state memory
from agent_state import AgentState # state schema for StateGraph
from agents import * # imports all agents from agents folder

# initializing agents
greeter_agent = GreeterAgent()
dish_search_agent = DishSearchAgent()
list_former_agent = ListFormerAgent()
show_dishes_agent = ShowDishesAgent()
research_dish_agent = ResearchDishAgent()
more_dishes_agent = MoreDishesAgent()
change_preferences_agent = ChangePreferencesAgent()
show_dish_agent = ShowDishAgent()
list_return_agent = ListReturnAgent()

# methods that determine next node for conditional edges
def check_dishes_to_show(state: AgentState): # checks if dishes to show is greater than zero - if not then dish search will be run, otherwise dishes will be shown
    return len(state['dishesToShow']) > 0

def check_post_show_dishes_decision(state: AgentState): # checks if user wants to learn more about a dish, see more dishes, or change their preferences
    return state['userDecision'].decision

def check_list_return_decision(state: AgentState): # checks if user wants to return to dishes after viewing a specific dish
    return state['userDecision'].decision

# initializes StateGraph with AgentState schema
builder = StateGraph(AgentState)

# adds nodes to graph
builder.add_node("greeter", greeter_agent.run)
builder.add_node("dish_search", dish_search_agent.run)
builder.add_node("list_former", list_former_agent.run)
builder.add_node("show_dishes", show_dishes_agent.run)
builder.add_node("research_dish", ResearchDishAgent.run)
builder.add_node("more_dishes", more_dishes_agent.run)
builder.add_node("change_preferences", change_preferences_agent.run)
builder.add_node("show_dish", show_dish_agent.run)
builder.add_node("list_return", list_return_agent.run)

# adds edges between nodes
builder.add_edge("greeter", "dish_search")
builder.add_edge("dish_search", "list_former")
builder.add_edge("research_dish", "show_dish")
builder.add_edge("show_dish", "list_return")
builder.add_edge("change_preferences", "dish_search")

# adds conditional edges
builder.add_conditional_edges("list_former", check_dishes_to_show, {True: "show_dishes", False: "dish_search"})
builder.add_conditional_edges("show_dishes", check_post_show_dishes_decision, {"researchDish": "research_dish", "moreDishes": "more_dishes", "changePreferences": "change_preferences"})
builder.add_conditional_edges("list_return", check_list_return_decision, {"yes": "show_dishes", "no": END})
builder.add_conditional_edges("more_dishes", check_dishes_to_show, {True: "show_dishes", False: "dish_search"})

# sets start of graph
builder.set_entry_point("greeter")

# used to save states of AgentState to allow returning to previous states and modifying states
memory = SqliteSaver.from_conn_string(":memory:")

# compiles StateGraph into CompiledGraph with memory support
graph = builder.compile(checkpointer = memory)

# application settings reader 
config = configparser.ConfigParser()
config.read('settings.ini')

# dictionary of inputs for the AgentState of the CompiledGraph
graphInput = {
    "numDishSearchQueries": config['QUERIES'].getint('numDishSearchQueries'),
    "maxDishSearchResults": config['SEARCH.RESULTS'].getint('maxDishSearchResults'),
    "maxRecommendations": config['DISHES.LIST'].getint('maxRecommendations'),
    "numDishResearchQueries": config['QUERIES'].getint('numDishResearchQueries'),
    "maxDishResearchResults": config['SEARCH.RESULTS'].getint('maxDishResearchResults')
}

# dictionary of configuration settings for running the CompiledGraph
graphConfig = {
    "recursion_limit": config['GRAPH.CONFIG'].getint('recursion_limit'),
    "configurable": {"thread_id": "1"} # AgentSate history will be stored on thread "1"
}

# runs the application with option to perform an action after after each node is run
for event in graph.stream(graphInput, graphConfig): # event is AgentState after last node run
    # print(event) # uncomment to print out AgentState after each node is run
    pass