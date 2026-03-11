import anthropic 
import logging
from inference.inference_utils import AnthropicSamplingParams 
from typing import List, Dict
from dotenv import load_dotenv
import os


class ClaudeCall : 
    def __init__(self, model:str, sampling_params : AnthropicSamplingParams,logger:logging.Logger) : 
        self.model = model 
        self.logger = logger

        sampling_params_dict = sampling_params.model_dump() 
        
        self.system = sampling_params_dict.pop("system_prompt")

        self.max_tokens = sampling_params_dict.pop("max_tokens")
        
        load_dotenv()
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(api_key=anthropic_api_key)

    def set_system_prompt(self,system_prompt:str) : 
        self.system = system_prompt

    def __call__(self,messages:List[Dict]) : 

        print("in claude caude call !!!")
        print("printing system prompt first part ")
        print(self.system[:1000])

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


