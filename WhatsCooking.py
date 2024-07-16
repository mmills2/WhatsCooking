# necessary imports
import configparser
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from agent_state import AgentState
from agents import *

# used to save states of graph to allow returning to previous states and modifying states
memory = SqliteSaver.from_conn_string(":memory:")

# greeter agent
greeter_agent = GreeterAgent()

# dish searcher agent
dish_search_agent = DishSearchAgent()

# dish list former agent
list_former_agent = ListFormerAgent()

# dishes to show is greater than zero check
def check_dishes_to_show(state: AgentState):
    return len(state['dishesToShow']) > 0

# show dishes node
show_dishes_agent = ShowDishesAgent()

# checks if user wants to learn more about a dish, see more dishes, or change their preferences
def check_post_show_dishes_decision(state: AgentState):
    return state['userDecision'].decision

# research dish agent
research_dish_agent = ResearchDishAgent()

# adjust dish lists node
more_dishes_agent = MoreDishesAgent()

# change preferences agent
change_preferences_agent = ChangePreferencesAgent()

# show dish agent
show_dish_agent = ShowDishAgent()

# post show dish agent
list_return_agent = ListReturnAgent()

# checks if user wants to return to dishes after view a specific dish
def check_post_show_dish_decision(state: AgentState):
    return state['userDecision'].decision

# builds workflow of graph from added nodes and edges
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
builder.add_conditional_edges("list_return", check_post_show_dish_decision, {"yes": "show_dishes", "no": END})
builder.add_conditional_edges("more_dishes", check_dishes_to_show, {True: "show_dishes", False: "dish_search"})

# sets start of graph
builder.set_entry_point("greeter")

# compiles graph so application can be run
graph = builder.compile(checkpointer = memory)

config = configparser.ConfigParser()
config.read('settings.ini')

graphInput = {
    "maxDishSearchResults": config['MAXES'].getint('dishSearchResults'),
    "maxRecommendations": config['MAXES'].getint('dishRecommendations'),
    "maxDishResearchResults": config['MAXES'].getint('dishResearchResults')
}

graphConfig = {
    "recursion_limit": config['MAXES'].getint('recursion_limit'),
    "configurable": {"thread_id": "1"}
}

# runs the application and prints out the AgentState after each node runs
for event in graph.stream(graphInput, graphConfig):
    # print(event)
    pass