import anthropic 
import logging
from inference.inference_utils import AnthropicSamplingParams 
from typing import List, Dict
from dotenv import load_dotenv
import os


class ClaudeCall : 
    def __init__(self, model:str, sampling_params : AnthropicSamplingParams,logger:logging.Logger,name:str="claude_call") : 
        
        self.model = model 
        self.logger = logger
        self.name = name

        sampling_params_dict = sampling_params.model_dump() 
        
        self.system = sampling_params_dict.pop("system_prompt")

        self.max_tokens = sampling_params_dict.pop("max_tokens")
        
        load_dotenv()
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.logger.info("anthropic client created correctly")
        self.logger.info(f"client name : {self.name}")
        self.logger.info("\n\n")
        

    def set_system_prompt(self,system_prompt:str) : 
        self.system = system_prompt

    def __call__(self,messages:List[Dict]) : 

        self.logger.info(f"start {self.name} call")
        self.logger.info("parameters : ") 
        self.logger.info(f"model : {self.model}")
        self.logger.info("##########################################")
        self.logger.info(f"max tokens : {self.max_tokens}")
        # self.logger.info("##########################################")
        # self.logger.info("system prompt : ")
        # self.logger.info(self.system)
        self.logger.info("##########################################")
        print("claude call !!!!")

        

        response = self.client.messages.create(
            model=self.model, 
            max_tokens=self.max_tokens, 
            system=self.system, 
            messages=messages
        )

        return response.content[0].text


if __name__ == "__main__" : 
    anthropic_sampling_params = AnthropicSamplingParams(system_prompt="you are a helpful assistant")
    logger = logging.getLogger(__name__)
    model = "claude-sonnet-4-6"

    claude_call = ClaudeCall(model,anthropic_sampling_params,logger)

    messages = [{"role":"user","content" : "how to make money faster as an agentic ai angineer"}]

    response = claude_call(messages)
    print("response") 
    print(response)


