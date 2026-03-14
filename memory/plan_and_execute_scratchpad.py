from typing import Dict,List
from memory.prompts.scratchpad_prompts import summarize_prompt
from memory.scratchpad import ScratchPad
import logging 


class PlanAndExecuteScratchPad(ScratchPad) : 
    
    def __init__(self,logger:logging.Logger, injection_mode:str="classic",injection_config:Dict=None) : 
        super().__init__(logger,injection_mode, injection_config) 
        self.context = []

    def add(self,type_of_context:str, context_2_add:str, delete_last:bool=False) :
        if delete_last : 
            self.context.pop()
        self.context.append({"type":type_of_context,"context" : context_2_add})

    

    def build(self) :
        result = "" 
        for added_message in self.context :
            result += f"{added_message['type']} : \n{added_message['context']} \n"

        self.logger.info(f"############ CONTEXT ############")
        self.logger.info(result)
        self.logger.info("#################################")
        print(result) 

        return result  
