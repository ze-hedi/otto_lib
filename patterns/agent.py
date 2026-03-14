from fastmcp import Client 
from fastmcp.client.transports import PythonStdioTransport
from typing import Dict, List 
from inference.llm_call import LLMCall
from inference.inference_utils import AnthropicSamplingParams
import os
import logging 
import asyncio 



class Agent :

    def __init__(self) :
        pass  

    def get_system_prompt(self) : 
        return self.llm_call.llm_call.system 

    async def connect_servers_spawned(self) : 
        self.clients = {} 
        self.tools = {} 
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env = os.environ.copy()
        env["PYTHONPATH"] = BASE_DIR 
        for server_file_path in self.server_file_paths : 
            try : 
                full_path = BASE_DIR + server_file_path 
                client = Client(PythonStdioTransport(full_path,env=env))
                await client.__aenter__()
                server_name = client.initialize_result.serverInfo.name
                self.logger.info(f"connected successfuly to server : {server_name}")
                self.logger.info(f"server file path : {full_path}")
                self.clients[server_name] = client

                tools = await client.list_tools() 
                self.logger.info(f"available tools :")
                for tool in tools : 
                    self.logger.info(tool.name)
                    self.tools[tool.name] = (tool,server_name)
            except Exception as e : 
                self.logger.error(f"failed to connect to server on file : {server_name}")
                self.logger.error(e)
            
            self.logger.info("\n\n")
            

    async def connect_servers_http(self) :

        self.clients = {}
        self.tools = {}

        for server_url in self.server_urls : 
            try : 
                client = await Client(server_url).__aenter__()
                self.logger.info(f"connected successfuly to server at url : {server_url}")
                server_name = client.initialize_result.serverInfo.name
                self.logger.info(f"server name : {server_name}")
                self.clients[server_name] = client 
                tools = await client.list_tools() 
                for tool in tools  : 
                    self.tools[tool.name] = (tool,server_name)

            except Exception as e: 
                self.logger.error(f"failed to connect to server : {server_url}")

    async def connect_servers(self) : 
        if self.spawned == True : 
            await self.connect_servers_spawned()
        else : 
            self.connect_servers_http()
    
    def show_tools(self) :
        return self.tools 

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



    @classmethod
    async def create(cls,name:str,logger:logging.Logger,llm_call:LLMCall,server_ids:Dict,spawned:bool=False) : 
        self = cls()
      
        self.name = name 
        self.logger = logger 
        self.llm_call = llm_call 

        self.logger.info(f"agent name : {self.name}")
        
        self.spawned = spawned

        if spawned == True : 
            if "server_file_paths" in server_ids : 
                self.server_file_paths = server_ids['server_file_paths']
            else : 
                raise ValueError("need to provide the key server_file_paths in server_ids because we are in stdio mode")

        else : 
            if "server_urls" in server_ids : 
                self.server_urls = server_ids['server_urls']
            else : 
                raise ValueError("need to provide the key server_urls in server_ids because we are in http mode")
        await self.connect_servers()

        return self 


async def main() : 
    # server_ids = {"server_urls" : ["http://127.0.0.1:8000/mcp"]}

    logger = logging.getLogger(__name__)
    sampling_params = AnthropicSamplingParams()
    claude_call = LLMCall("claude-haiku-4-5-20251001",sampling_params,logger) 
    print("start building the react agent .... ")

    # agent = await Agent.create(logger,claude_call,server_ids,False)

    server_file_paths = { "server_file_paths" : ["/MCP/api_web_search_mcp/server.py"]}
    agent_2 = await Agent.create(logger,claude_call,server_file_paths, True)

if __name__ == "__main__" : 
    asyncio.run(main())