# What's Cooking

Have you ever desired to cook something new but you weren't sure what to cook? What's Cooking finds just the right food dish for you to try out. Powered by AI agents, What's Cooking scours the internet for recipes based on your preferences, or if you have none, suggests some recipes to you.

## Meet the Agents

What's Cooking is built up of nine LangGraph agents working together to give you the perfect recipe.

1. GREETER AGENT: Greets the user and gets their food preferences
2. DISH SEARCH AGENT: Searches the internet for relevant food dishes
3. LIST FORMER AGENT: Constructs a list of food dishes from the search
4. SHOW DISHES AGENT: Shows the list of food dishes with options to learn more about a dish, see more dishes, or change their food preferences
5. RESEARCH DISH AGENT: Searches the internet for information on a food dish
6. SHOW DISH AGENT: Shows a decsription, list of ingredients, and recipe for a food dish
7. LIST RETURN AGENT: Routes the user back to a previously shown list of food dishes
8. SEE MORE DISHES AGENT: Shows more relevant food dishes
9. CHANGE PREFERENCES AGENT: Gets the user's new food preferences if they want to change them

## Example Generation

![screenshot](example_generations/exampleGenerationOne.png)
![screenshot](example_generations/exampleGenerationTwo.png)

## How to Install

### API Keys

An OpenAI API key and Tavily API key are required for this application. Click the links below to sign up:\
[OpenAI API Key](https://platform.openai.com/)\
[Tavily API Key](https://tavily.com/)

### Installing Project

1. First clone the repository
   ```
   git clone https://github.com/mmills2/WhatsCooking.git
   ```
2. Then set your API keys
   - Windows
   ```
   setx OPENAI_API_KEY = <your-openai-api-key>
   setx TAVILY_API_KEY = <your-tavily-api-key>
   ```
   - Linux/Unix
   ```
   export OPENAI_API_KEY = <your-openai-api-key>
   export TAVILY_API_KEY = <your-tavily-api-key>
   ```
   You may have to restart your terminal after setting the API keys for the set to take affect
3. Then install the requirements
   ```
   pip install -r requirements.txt
   ```
4. Lastly run the WhatsCooking.py file
   ```
   python WhatsCooking.py
   ```
