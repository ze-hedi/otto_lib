import json
import logging 
import asyncio 
import re 
from typing import Dict, List 
from inference.inference_utils import SamplingParams, AnthropicSamplingParams
from inference.llm_call import LLMCall
from patterns.agent import Agent 
from patterns.prompts.plan_and_execute_prompts import planner_prompt, tool_call_prompt
from memory.scratchpad import ScratchPad
from memory.plan_and_execute_scratchpad import PlanAndExecuteScratchPad


class Planner :
    def __init__(self,llm_call:LLMCall,logger:logging.Logger, system_prompt:str=None) : 
        self.llm_call = llm_call
        self.logger = logger 
        if system_prompt is not None : 
            self.system_prompt = system_prompt
        else : 
            self.system_prompt = planner_prompt 
    def set_tools_on_system_prompt(self,tools:str) : 
        self.system_prompt = self.system_prompt.format(TOOLS=tools)
        self.logger.info("############## PLANNER SYSTEM PROMPT ##############")
        self.logger.info(self.system_prompt)
        self.logger.info("###################################################")
        self.llm_call.set_system_prompt(self.system_prompt)

    def parse_response(self,llm_response) : 
        result = {} 
        think_match = re.search(r"<think>(.*?)</think>", llm_response, re.DOTALL)
        if not think_match:
            self.logger.error("ERROR : can't find the <think></think> block in the generated response")
            return False 

        result["think"] = think_match.group(1).strip()

        plan_match = re.search(r"<plan>(.*?)</plan>", llm_response, re.DOTALL)
        
        if plan_match : 
            plan = plan_match.group(1).strip()
            remainder = re.sub(r"<step>.*?</step>", "", plan, flags=re.DOTALL)
            if remainder.strip() : 
                self.logger.error("ERROR : Bad plan output format")

            result["plan"] = re.findall(r"<step>(.*?)</step>", plan, flags=re.DOTALL)
            return result 
            
        else : 
            self.logger.error("ERROR: Bad plan output format")
            return False 




    def __call__(self,messages:Dict) : 
        planner_response = self.llm_call(messages)
        return planner_response

class ToolExecutor : 
    def __init__(self,llm_call:LLMCall, logger:logging.Logger, system_prompt:str=None) : 
        self.llm_call = llm_call 
        self.logger = logger 

        if system_prompt is not None : 
            self.system_prompt = system_prompt 
        else : 
            self.system_prompt = tool_call_prompt


    def set_tools_on_system_prompt(self,tools:str) : 
        self.system_prompt = tool_call_prompt.format(TOOLS=tools)
        self.logger.info("############## PLANNER SYSTEM PROMPT ##############")
        self.logger.info(self.system_prompt)
        self.logger.info("###################################################")
        self.llm_call.set_system_prompt(self.system_prompt)

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
                print("\n\n\n")
            else:
                self.logger.error("ERROR : can't find <action></action> nor <final></final> in the llm response")
                self.logger.error("############# PRINTING THE TOOL EXECUTOR RESPONSE #############" ) 
                self.logger.error(llm_response)
                self.logger.error("####################################################################")
                
                return False 
        return result 

    def __call__(self, context : str) : 
        
        messages = [{
            "role" : "user" , 
            "content" : context
        }]

        tool_call = self.llm_call(messages)
        parsed_response = self.parse_response(tool_call)
        max_retries=3
        retry=1
        while isinstance(parsed_response,bool) and retry <=  max_retries : 
            self.logger.warning(f"WARNING : retrying tool executor call for {retry} time")
            self.logger.warning("################### PARSED RESPONSE ###################")
            self.logger.warning(tool_call)
            self.logger.warning("#######################################################")
            self.logger.warning("\n")
            tool_call = self.llm_call(messages)
            parsed_response = self.parse_response(tool_call)
            retry += 1 
        
        # print("toll call response : ") 
        # print(json.dumps(parsed_response,indent=4))

        
        return parsed_response
        # print("tool execution response ") 
        # print(tool_execution_response)



        





class PlanAndExecuteAgent(Agent) : 
    
    def __init__(self) : 
        pass 

    @classmethod 
    async def create(cls,logger:logging.Logger,planner_llm_call:LLMCall,tool_executor_llm_call:LLMCall,server_ids:Dict, spawned:bool=False, 
                    agent_name:str="plan_and_execute_agent", planner_system_prompt:str=None) : 

        logger.info("creating the plan and execute agent .....")
        logger.info(f"name : {agent_name}")
        self = await super().create(agent_name,logger,planner_llm_call,server_ids,spawned)
        
        self.planner = Planner(planner_llm_call,logger,planner_system_prompt)
        self.tool_executor = ToolExecutor(tool_executor_llm_call,logger) 

        tools_str = ""
        for tool_name in self.tools.keys() :
            tools_str += f"name :  {tool_name} \n" + f"description : \n {self.tools[tool_name][0].description} \n" + f"input scheme : \n {json.dumps(self.tools[tool_name][0].inputSchema, indent=2)}"

        self.planner.set_tools_on_system_prompt(tools_str)
        self.tool_executor.set_tools_on_system_prompt(tools_str)

        self.scratchpad = PlanAndExecuteScratchPad(logger=self.logger)
        
        return self

    
    def build_plan(self,parsed_response) : 
        result = ""
        for i in range(len(parsed_response['plan'])) :
            step_num = i + 1 
            result += f"{step_num}- {parsed_response['plan'][i]}\n"
        return result 

    async def __call__(self,user_query) : 

        messages = [{
            "role" : "user", 
            "content" : user_query
        }]

        plan_response = self.planner(messages)
        parsed_response = self.planner.parse_response(plan_response)
        
        num_retries = 3
        retry = 0
        while isinstance(parsed_response,bool) and retry<=3 : 
            plan_response = self.planner(messages)
            parsed_response = self.planner.parse_response(plan_response)
            
        self.scratchpad.add("plan",plan_response)
        if isinstance(parsed_response,bool) : 
            print("failed to parse planner response ")
        else : 
            print("################## THINK #######################")
            print(parsed_response["think"])
            print("################################################")
            print("################## PLAN #######################")

            
            plan_str = self.build_plan(parsed_response)
            for i in range(len(parsed_response["plan"])) : 

                print(f"iteration num : {i}")
                
                self.scratchpad.add("step to execute",parsed_response["plan"][i])
                print("printing the scratchpad content so far")
                context = self.scratchpad.build() 

                tool_2_call = self.tool_executor(context)

                if 'action' in tool_2_call : 

                    print("print tool to call") 
                    print(tool_2_call['action'])
                    tool_execution_response = await self.execute_tool(self.tools[tool_2_call['action']['name']],tool_2_call["action"])
                    

                    self.scratchpad.add("exectuted step",f"{parsed_response['plan'][i]}",True) 
                    self.scratchpad.add("tool to call",f"{json.dumps(tool_2_call,indent=2)}")
                    self.scratchpad.add("tool response",f"{tool_execution_response}")

                
                elif 'final' in tool_2_call : 
                    self.scratchpad.add("exectuted step",f"{parsed_response['plan'][i]}",True) 
                    self.scratchpad("response",f"{tool_2_call['final']}")
                print("\n\n\n")

                    # print("tool call ")
                    # print(tool_execution_response)

                    
                                    # print(f"step{i} : ")
                # print(parsed_response["plan"][i]) 





async def main() : 
    server_file_paths = { "server_file_paths" : ["/MCP/api_web_search_mcp/server.py"]}

    log_file_path = "./log_plan_and_execute_agent.txt" 
    logger = logging.getLogger(log_file_path) 
    logger.setLevel(logging.DEBUG) 
    handler = logging.FileHandler(log_file_path)
    logger.addHandler(handler)

    sampling_params = AnthropicSamplingParams()
    claude_call = LLMCall("claude-haiku-4-5-20251001",sampling_params,logger) 

    tool_executor_claude_call = LLMCall("claude-haiku-4-5-20251001",sampling_params,logger) 

    plan_and_execute_agent = await PlanAndExecuteAgent.create(logger,claude_call,tool_executor_claude_call,server_file_paths,True) 

    usery_query = "we are in the beginning of march 2026, there's a war between usa and Israel vs Iran. It has an impact on the oil prices. Your goal is to estimate how the gaz and oil prices will evolve for the next 3 months"

    await plan_and_execute_agent(usery_query) 

if __name__ == "__main__" :
    asyncio.run(main())  