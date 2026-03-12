import json
import logging 
import asyncio 
import re 
from fastmcp import Client 
from fastmcp.client.transports import PythonStdioTransport
from typing import Dict, List 
from inference.inference_utils import SamplingParams, AnthropicSamplingParams
from inference.llm_call import LLMCall
from patterns.agent import Agent 
from patterns.prompts.react_prompts import react_prompt
from memory.scratchpad import ScratchPad

class ReactAgent(Agent) : 
    
    def __init__(self) : 
        pass 

    def set_system_prompt(self,role:str, tools:str) :
        self.system_prompt = react_prompt.format(role=role,tools=tools) 
        self.llm_call.set_system_prompt(self.system_prompt)
           
    @classmethod 
    async def create(cls,logger:logging.Logger,llm_call:LLMCall,server_ids:Dict,spawned:bool=False,agent_name:str="react_agent",max_iterations:int=10)  : 
        logger.info("creating the react agent ......")
        self = await super().create(agent_name,logger,llm_call,server_ids,spawned)
        self.max_iterations = max_iterations
        self.scratchpad = ScratchPad(logger=self.logger)
        return self 

    def parse_response(self,llm_response:str) :  
        result = {}
        think_match = re.search(r"<think>(.*?)</think>", llm_response, re.DOTALL)
        if not think_match:
            self.logger.error("ERROR : can't find the <think></think> block in the generated response")
            return False 
    
        result["think"] = think_match.group(1).strip()

        action_match = re.search(r"<action>(.*?)</action>", llm_response, re.DOTALL)
        if action_match:
            action_content = action_match.group(1).strip()
            name_match = re.search(r"<name>(.*?)</name>", action_content, re.DOTALL)
            if name_match:
                result["action"] = {"name" :name_match.group(1).strip() }
            else : 
                self.logger.error("ERROR : failed to find <name></name>")
                return False 

            input_match = re.search(r"<input>(.*?)</input>", action_content, re.DOTALL)
            if input_match:
                raw_input = input_match.group(1).strip()
                try:
                    parsed = json.loads(raw_input)
                    result["action"]["arguments"] = parsed
                except json.JSONDecodeError as e:
                    self.logger.error("ERROR : <input></input> does'nt contain a json object")
                    return False 
            else : 
                self.logger.error("ERROR : failed to find <input></input> block")
                return False 

        else:
            final_match = re.search(r"<final>(.*?)</final>", llm_response, re.DOTALL)
            if final_match:
                result["final"] = final_match.group(1).strip()
            else:
                self.logger.error("ERROR : can't find <action></action> nor <final></final> in the llm response")
                return False 

        return result

    async def execute_tool(self,tool_tuple,action_dict) :

        response = ""
        self.logger.info(f"executing {action_dict['name']} on server : {tool_tuple[1]}")
        list_available_clients = list(self.clients.keys())
        try : 
            tool_execution_result = await self.clients[tool_tuple[1]].call_tool(**action_dict)
            for block in tool_execution_result.content : 
                if block.type == "text" : 
                    response += block.text
            return response  

        except Exception as e : 
            self.logger.error("ERROR : failed at executing the tool !!!")
            self.logger.error(f"ERROR : {e}")
            return False 


    async def __call__(self,user_query:str) :
        
        tools_str = ""
        for tool_name in self.tools.keys() :
            tools_str += f"name :  {tool_name} \n" + f"description : \n {self.tools[tool_name][0].description} \n" + f"input scheme : \n {json.dumps(self.tools[tool_name][0].inputSchema, indent=2)}"
    
        agent_role = "You are a professional research and content writer. Your job is to produce well-crafted, substantive written content on a given topic by conducting thorough web research using a structured reasoning loop, then synthesizing your findings into polished prose."

        self.set_system_prompt(role=agent_role,tools=tools_str)

        self.logger.info("########### System prompt #############") 
        self.logger.info(self.get_system_prompt())
        self.logger.info("#################### \n")

        self.context = user_query

        num_iteration = 0 
        finished = False 

        while num_iteration < self.max_iterations and not finished : 

            self.logger.info(f'iteration num {num_iteration}')
            self.messages = [{
                "role" : "user", 
                'content' : self.context
            }]

            ai_response = self.llm_call(self.messages)

            self.logger.info("\n\n")
            self.logger.info("ai response ")
            self.logger.info(ai_response)


            parsed_response = self.parse_response(ai_response)
            
            if isinstance(parsed_response,bool) : 
                print("ai response parsing has failed ")
                num_iteration += 1 

            else :  
                if 'final' in parsed_response : 
                    finished = True  
                else : 
                    server_name = self.tools[parsed_response['action']['name']][1]
                    print(f"***** printing server name : {server_name}")
                
                    print("prinitng action dict ")
                    print(parsed_response["action"])
                    tool_execution_response = await self.execute_tool(self.tools[parsed_response['action']['name']],parsed_response["action"])
                    if isinstance(tool_execution_response,bool) : 
                        pass 
                    else : 
                        self.context += f"######## Tool use ########## \n name : {parsed_response['action']['name']} " + "\n" +  json.dumps(parsed_response['action'],indent=2)
                        self.context += f"####### Tool result ######## \n {tool_execution_response}"
        
                    num_iteration += 1 
                    self.logger.info("\n\n")


async def  main() : 
    server_file_paths = { "server_file_paths" : ["/MCP/api_web_search_mcp/server.py"]}

    log_file_path = "./log_react_agent.txt" 
    logger = logging.getLogger(log_file_path) 
    logger.setLevel(logging.DEBUG) 
    handler = logging.FileHandler(log_file_path)
    logger.addHandler(handler)

    sampling_params = AnthropicSamplingParams()
    claude_call = LLMCall("claude-haiku-4-5-20251001",sampling_params,logger) 
    print("start building the react agent .... ")

    react_agent = await ReactAgent.create(logger,claude_call,server_file_paths,True)
    await react_agent("how will eur/usd price evolve")

    # print(f"printing tools dict : {tools_dict}")
if __name__ == "__main__" : 
    asyncio.run(main())

    