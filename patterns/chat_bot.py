import logging
from typing import Dict, List
from inference.llm_call import LLMCall



class ChatBot : 
    def __init__(self,llm_call:LLMCall, logger:logging.Logger,system_prompt:str) : 
        self.llm_call = llm_call 
        self.logger = logger 
        self.messages = [{"role":"system", "content":""},{"role":"user","conteht":""}]  
        # self.history = [] #for testing purposes to go fast we will use history_str that stock all the history directly in a string
        self.history_str = "<conversation_history>"

    def __call__(self,system_prompt:str,user_query:str) : 

        self.messages[0]["content"] = system_prompt
        self.messages[1]["content"] = user_query 
        response = self.llm_call(self.messages)
        return response

    def update_history(self,user_query:str, ai_response:str ) : 
        
        if self.history_str.endswith("</conversation_history>"):
            self.history_str = self.history_str[:-len("</conversation_history>")]
        self.history_str += f"""
<user>{user_query}</user> 
<assistant>{ai_response}</assistant>
"</conversation_history>"""
        print('\n\n')
        print("################################################") 
        print(self.history_str) 
        print("################################################") 
