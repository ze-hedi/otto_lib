
import os
import tiktoken 
import logging
from typing import Dict, List 
from openai import OpenAI
from dotenv import load_dotenv
from inference.inference_utils import SamplingParams



class GPTCall : 
    def __init__(self,model:str,sampling_params : SamplingParams,logger:logging.Logger, stream:bool=True, name:str="gpt_call") : 
        self.name = name
        load_dotenv() 
        self.logger = logger 
        openai_api_key = os.getenv("OPENAI_API_KEY") 
        if openai_api_key : 
            self.gpt_client = OpenAI(api_key=openai_api_key)
        else : 
            raise ValueError("can find OpenAI key ")

        self.call_params = sampling_params.model_dump()
        self.call_params["model"] = model
        self.call_params["stream"] = stream
    
    def __call__(self,messages:List[Dict]) : 
        self.logger.info(f"calling : {self.name}") 
        self.call_params["messages"] = messages 
        response = self.gpt_client.chat.completions.create(**self.call_params) 
        return response 



