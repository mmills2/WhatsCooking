from structured_outputs import UserDecision

class Agent:
    def __init__(self, state):
        self.state = state
    
    def question_user(questionToUser: str, systemPrompt: str) -> UserDecision:
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