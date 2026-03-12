from typing import Dict,List
from memory.prompts.scratchpad_prompts import summarize_prompt
import logging 

#this class will be used as the object to handle the step of reasoning for an agent or any short term memory 
# it has the following injection mode (how the memory or resoning steps are injected into the prompt)
#   classic : concatenate all steps and injected into the prompt 
#   sliding_window : only concatenate the n last messages
#   summurize : summurize conversation and then inject it 
class ScratchPad : 
    def __init__(self,logger:logging.Logger, injection_mode:str="classic",injection_config:Dict=None) : 
        self.steps = []
        self.loggger = logger 
        self.logger.info("setting scratch pat object")
        self.injection_mode = injection_mode

        settings = ""
        if self.injection_mode == "sliding_window" :
            if not 'window_size' in injection_config : 
                self.logger.warning("WARNING : forgot to give window_size value, by default it will be set to 5")
                self.window_size = 5  
            else : 
                self.window_size = injection_config['window_size']
                settings = "Settings : \n"+f"-window sisze = {self.window_size}"
        elif self.injection_mode == "summurize" :
            if "model" in injection_config : 
                self.model = injection_config["model"]
                settings = "Settings : \n" + f"model : {self.model}"
            else : 
                self.model = "claude-haiku-4-5-20251001"
                self.logger.warning(f"WARNING : forgot to provide model for summary pipeline. By default we will use {self.model}")
                settings = "Settings : \n" + f"model : {self.model}\n"

            
            if "summarize_prompt" in injection_config : 
                self.summarize_prompt = injection_config["summarize_prompt"]
                settings += f"- summarize_prompt : \n{self.summarize_prompt}\n"
            else : 
                self.summarize_prompt = summarize_prompt
                self.logger.warning(f"WARNING : forgot to set summarize prompt, by default summarize_prompt : {self.summarize_prompt}")

        elif self.injection_mode == "classic" : 
            pass 
        else :
            self.logger.warning(f"WARNING : {self.injection_mode} is invalid injection mode. By default 'classic' mode will be set") 
            self.injection_mode = "classic" 

        self.logger.info(f"injection mode : {self.injection_mode}")
    


        self.context = ""

    def add_step(self,step:Dict) :  
        self.steps.append(step) 

        
