import json
import logging 
import asyncio 
import re 
from typing import Dict, List 
from inference.inference_utils import SamplingParams, AnthropicSamplingParams
from inference.llm_call import LLMCall
from patterns.agent import Agent 
from patterns.prompts.plan_and_execute_prompts import planner_prompt
from memory.scratchpad import ScratchPad


class Planner :
    def __init__(self,llm_call:LLMCall,logger:logging.Logger,system_prompt:str=None) : 
        self.llm_call = llm_call
        self.logger = logger 
        if system_prompt is not None : 
            self.system_prompt = system_prompt
        else : 
            self.system_prompt = planner_prompt 
        print("Planner built correctly !!")

    def set_tools_on_system_prompt(self,tools:str) : 
        self.system_prompt = self.system_prompt.format(TOOLS=tools)
        self.logger.info("############## PLANNER SYSTEM PROMPT ##############")
        self.logger.info(self.system_prompt)
        self.logger.info("###################################################")
        self.llm_call.set_system_prompt(self.system_prompt)

    def __call__(self,messages:Dict) : 
        planner_response = self.llm_call(messages)
        return planner_response
    

class PlanAndExecuteAgent(Agent) : 
    
    def __init__(self) : 
        pass 

    @classmethod 
    async def create(cls,logger:logging.Logger,llm_call,server_ids:Dict, spawned:bool=False, 
                    agent_name:str="plan_and_execute_agent", planner_system_prompt:str=None) : 

        logger.info("creating the plan and execute agent .....")
        logger.info(f"name : {agent_name}")
        self = await super().create(agent_name,logger,llm_call,server_ids,spawned)
        
        self.planner = Planner(llm_call,logger,planner_system_prompt)

        tools_str = ""
        for tool_name in self.tools.keys() :
            tools_str += f"name :  {tool_name} \n" + f"description : \n {self.tools[tool_name][0].description} \n" + f"input scheme : \n {json.dumps(self.tools[tool_name][0].inputSchema, indent=2)}"

        self.planner.set_tools_on_system_prompt(tools_str)

        self.scratchpad = ScratchPad(logger=self.logger)
        
        return self

    async def __call__(self,user_query) : 

        messages = [{
            "role" : "user", 
            "content" : user_query
        }]

        plan_response = self.planner(messages)

        print("plan : ")
        print(plan_response) 



async def main() : 
    server_file_paths = { "server_file_paths" : ["/MCP/api_web_search_mcp/server.py"]}

    log_file_path = "./log_plan_and_execute_agent.txt" 
    logger = logging.getLogger(log_file_path) 
    logger.setLevel(logging.DEBUG) 
    handler = logging.FileHandler(log_file_path)
    logger.addHandler(handler)

    sampling_params = AnthropicSamplingParams()
    claude_call = LLMCall("claude-haiku-4-5-20251001",sampling_params,logger) 

    plan_and_execute_agent = await PlanAndExecuteAgent.create(logger,claude_call,server_file_paths,True) 

    usery_query = "we are in the beginning of march 2026, there's a war between usa and Israel vs Iran. It has an impact on the oil prices. Your goal is to estimate how the gaz and oil prices will evolve for the next 3 months"

    await plan_and_execute_agent(usery_query) 

if __name__ == "__main__" :
    asyncio.run(main())  