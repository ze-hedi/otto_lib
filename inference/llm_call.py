import logging
from typing import Dict, List
from inference.inference_utils import SamplingParams, AnthropicSamplingParams
from inference.gpt_call import GPTCall
from inference.claude_call import ClaudeCall 



class LLMCall  : 
    def __init__(self,model:str,sampling_params:SamplingParams, logger:logging.Logger, stream:bool=True, name:str="") : 
        
        self.llm_params = {
            "model" : model , 
            "sampling_params" : sampling_params , 
            "logger" : logger , 
            "stream" : stream
        }
        if name != "" : 
            self.llm_params["name"] = name 


        if model.startswith("gpt") : 
            self.llm_call = GPTCall(**self.llm_params)

        elif model.startswith("claude") : 
            self.name = name
            self.llm_call = ClaudeCall(model,sampling_params,logger)

    def set_system_prompt(self,system_prompt:str) : 
        self.llm_call.set_system_prompt(system_prompt)

    def __call__(self,messages:List[Dict]) : 
        return self.llm_call(messages) 





if __name__=="__main__" : 
    logger = logging.getLogger(__name__)
    sampling_params = SamplingParams()
    gpt_call = LLMCall("gpt-5.1",sampling_params,logger) 

    messages = [{"role" : "system","content":"you are a helpful assistant"},
                {"role" : "user", "content":"is it possible to dedicate 1 year of life to deep work to build enough passive income resources. know that i'm a c++ scientific computing expert and ai agent builder"}]

    response = gpt_call(messages) 
    ai_response = ""
    for chunk in response : 
        if chunk.choices[0].delta.content : 
            print(chunk.choices[0].delta.content, end="", flush=True)
            ai_response =chunk.choices[0].delta.content 

