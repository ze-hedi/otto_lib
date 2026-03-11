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

        print("creating the Agent object !!!!!")
        pass  

    async def connect_servers_spawned(self) : 

        self.clients = {} 
        self.tools = {} 

        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env = os.environ.copy()
        env["PYTHONPATH"] = BASE_DIR 
        for server_file_path in self.server_file_paths : 
            full_path = BASE_DIR + server_file_path 
            print(f"path :  {full_path}")
            client = Client(PythonStdioTransport(full_path,env=env))
            await client.__aenter__()
            server_name = client.initialize_result.serverInfo.name

            print(server_name)
            tools = await client.list_tools() 
            for tool in tools : 
                print(f"name : {tool.name}")

        print("all done correctly")


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
                    print(f"name : {tool.name}")
                print("printing tools : ") 
                print(self.tools)

            except Exception as e: 
                print(f"{server_url} deconne zebi")
                self.logger.error(f"failed to connect to server : {server_url}")

    async def connect_servers(self) : 
        if self.spawned == True : 
            print("spawned case ")
            await self.connect_servers_spawned()
        else : 
            print("http connection case ")
            self.connect_servers_http()
    
    def show_tools(self) :
        print(f"from show tools : {type(self.tools)}")
        return self.tools 


    @classmethod
    async def create(cls,logger:logging.Logger,llm_call:LLMCall,server_ids:Dict,spawned:bool=False) : 
        print("creating the Agent object baby")
        self = cls()
      
        self.logger = logger 
        self.llm_call = llm_call 
        if (self.llm_call is not None) : 
            print("from agent creator llm_call not null !! ")
        else : 
            print("from agent creator llm_call is null !!")
        self.spawned = spawned

        if spawned == True : 
            if "server_file_paths" in server_ids : 
                print("found server file paths ....")
                self.server_file_paths = server_ids['server_file_paths']
                await self.connect_servers()
        else : 
            if "server_urls" in server_ids : 
                self.server_urls = server_ids['server_urls']
                await self.connect_servers()
                # print(f"printing available server urls : {server_ids['server_urls']}")
                return self     
        
            else : 
                raise ValueError("need to provide the key server_urls in server_ids because we are in http mode")


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