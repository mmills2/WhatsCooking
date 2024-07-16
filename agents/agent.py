# necessary imports
from structured_outputs import UserDecision # schema used for storing user output data
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage # used to define message types to AI model
from langchain_openai import ChatOpenAI # OpenAI model

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

# agent parent class
class Agent:
    def __init__(self): # no data to initialize on initialization 
        pass
    
    # questions the user until valid answer is given and returns data based on user's answer
    def question_user(self, questionToUser: str, systemPrompt: str) -> UserDecision:
        print(questionToUser)

        # stores history of messages while questioning user
        messages = [
            SystemMessage(content = systemPrompt),
            AIMessage(content = questionToUser)    
        ]
        
        userDecision = UserDecision(decision = "insufficientResponse") # allows while loop to be entered
        while(userDecision.decision == "insufficientResponse"): # loops while user answer is not valid
            
            if(userDecision.clarifyingRespone): # if AI model has a response to user's answer (will not on first pass)
                print(userDecision.clarifyingRespone)
                messages.append(AIMessage(content = userDecision.clarifyingRespone)) # adds AI's response to history of messages
            
            userInput = input(": ")
            messages.append(HumanMessage(content = userInput)) # adds user's answer to history of messages

            userDecision = model.with_structured_output(UserDecision).invoke(messages) # invokes AI with history of messages and returns response in UserDecision schema
        
        return userDecision