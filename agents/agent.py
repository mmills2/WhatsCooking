# loads environment variables
from dotenv import load_dotenv
_ = load_dotenv()

from structured_outputs import UserDecision
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# initializes OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo", temperature = 0)

class Agent:
    def __init__(self):
        pass
    
    def question_user(self, questionToUser: str, systemPrompt: str) -> UserDecision:
        print(questionToUser)

        messages = [
            SystemMessage(content = systemPrompt),
            AIMessage(content = questionToUser)    
        ]
        
        userDecision = UserDecision(decision = "insufficientResponse")
        while(userDecision.decision == "insufficientResponse"):
            if(userDecision.clarifyingRespone):
                print(userDecision.clarifyingRespone)
                messages.append(AIMessage(content = userDecision.clarifyingRespone))
            userInput = input(": ")
            messages.append(HumanMessage(content = userInput))
            userDecision = model.with_structured_output(UserDecision).invoke(messages)
        return userDecision