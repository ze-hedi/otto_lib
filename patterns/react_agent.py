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

class ReactAgent(Agent) : 
    def __init__(self) : 
        print("creating the react agent !!!") 
        self.messages = []

    def set_system_prompt(self,role:str, tools:str) :
        self.system_prompt = react_prompt.format(role=role,tools=tools) 
        self.llm_call.set_system_prompt(self.system_prompt)
        


   
    @classmethod 
    async def create(cls,logger:logging.Logger,llm_call:LLMCall,server_ids:Dict,spawned:bool=False)  : 
        self = await super().create(logger,llm_call,server_ids,spawned)
        print("prinitng server urls from react agent : ")
        if self.spawned == False : 
            print(json.dumps(self.server_urls,indent=2))
        return self 




    def parse_response(self,llm_response:str) :  
        # Extract <think> — mandatory
        result = {}
        think_match = re.search(r"<think>(.*?)</think>", llm_response, re.DOTALL)
        if not think_match:
            raise ValueError("Missing <think></think> block in agent output.")
    
        # print("=== THINKING ===")
        # print(think_match.group(1).strip())
        result["think"] = think_match.group(1).strip()
        # print()

        # Try <action> first
        action_match = re.search(r"<action>(.*?)</action>", llm_response, re.DOTALL)
        if action_match:
            action_content = action_match.group(1).strip()

            # Extract <name>
            name_match = re.search(r"<name>(.*?)</name>", action_content, re.DOTALL)
            if name_match:
                # print("=== ACTION NAME ===")
                # print(name_match.group(1).strip())
                result["action"] = {"name" :name_match.group(1).strip() }
                # print()

            # Extract <input> and parse as JSON
            input_match = re.search(r"<input>(.*?)</input>", action_content, re.DOTALL)
            if input_match:
                raw_input = input_match.group(1).strip()
                try:
                    parsed = json.loads(raw_input)
                    # print("=== ACTION INPUT ===")
                    # print(json.dumps(parsed, indent=2))
                    result["action"]["arguments"] = parsed
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse <input> as JSON: {e}\nRaw content: {raw_input}")

        else:
            # Fall back to <final>
            final_match = re.search(r"<final>(.*?)</final>", llm_response, re.DOTALL)
            if final_match:
                # print("=== FINAL ANSWER ===")
                # print(final_match.group(1).strip())
                result["final"] = final_match.group(1).strip()
            else:
                raise ValueError("Missing <action></action> or <final></final> block in agent output.")
        return result

    async def execute_tool(self,tool_tuple,action_dict) :

        response = ""
        print(f"tool tupe second element : {tool_tuple[1]} ")
        list_available_clients = list(self.clients.keys())
        print(f"list of available client : {list_available_clients}")
        tool_execution_result = await self.clients[tool_tuple[1]].call_tool(**action_dict)
        for block in tool_execution_result.content : 
            if block.type == "text" : 
                response += block.text

        return response  


    async def __call__(self,user_query:str) :
        
        tools_str = ""
        for tool_name in self.tools.keys() :
            tools_str += f"name :  {tool_name} \n" + f"description : \n {self.tools[tool_name][0].description} \n" + f"input scheme : \n {json.dumps(self.tools[tool_name][0].inputSchema, indent=2)}"
    
        agent_role = "You are a professional research and content writer. Your job is to produce well-crafted, substantive written content on a given topic by conducting thorough web research using a structured reasoning loop, then synthesizing your findings into polished prose."

        self.set_system_prompt(role=agent_role,tools=tools_str)

        self.context = user_query

        self.messages = [{
            "role" : "user", 
            'content' : self.context
        }]

        ai_response = self.llm_call(self.messages)

        print("print full ai response ") 
        print(ai_response)

        parsed_response = self.parse_response(ai_response)

        # print("\n\n\n print the parsed response ")
        # print(parsed_response)

        if parsed_response["action"]["name"] in self.tools : 
            print(f"found tool on server : {self.tools[parsed_response['action']['name']][1]}")

        print("\n\n\n")

        # self.messages.append({"role":"assistant",
        #           "content" : [
        #              {"type":"text","text":parsed_response["think"]}, 
        #              {"type":"tool_use","id":"tavily_search","name":parsed_response["action"]["name"],"input":parsed_response["action"]["arguments"]}
        #           ]})
        
        server_name = self.tools[parsed_response['action']['name']][1]
        print(f"***** printing server name : {server_name}")
        tool_execution_response = await self.execute_tool(self.tools[parsed_response['action']['name']],parsed_response["action"])
        # print("printing tool response ") 
        # print(tool_execution_response)


        
        # self.context += " \n\n ######## Thinking ########"
        self.context += f"######## Tool use ########## \n name : {parsed_response['action']['name']} " + "\n" +  json.dumps(parsed_response['action'],indent=2)
        self.context += f"####### Tool result ######## \n {tool_execution_response}"

        self.messages = [{
            "role" : "user", 
            'content' : self.context
        }]

        ai_response = self.llm_call(self.messages)

        print("second ai response ")
        print(ai_response)

        # print("\n\n second response \n\n")
        # print(ai_response)


        # self.messages.append({
        #     "role" : "user", 
        #     "content" : [
        #         {"type" : "tool_result", "tool_use_id" : "tavily_search", "content":tool_execution_response}
        #     ]
        # })

        # print("\n\n\n\n")
        # print("second response") 

        # ai_response = self.llm_call(self.messages)

        # print(ai_response)
        # parsed_response = self.parse_response(ai_response)

        # print("second response parsed") 
        # print(json.dumps(parsed_response,indent=2))


        # print("ai_response")
        # print(json.dumps(parsed_response,indent=2))
 



    # def __call__(self, user_query : str, )
async def  main() : 
    server_file_paths = { "server_file_paths" : ["/MCP/api_web_search_mcp/server.py"]}

    logger = logging.getLogger(__name__)
    sampling_params = AnthropicSamplingParams()
    claude_call = LLMCall("claude-haiku-4-5-20251001",sampling_params,logger) 
    print("start building the react agent .... ")

    react_agent = await ReactAgent.create(logger,claude_call,server_file_paths,True)
    await react_agent("how will eur/usd price evolve")

    # print(f"printing tools dict : {tools_dict}")
if __name__ == "__main__" : 
    asyncio.run(main())

    