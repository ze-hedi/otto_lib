from fastmcp import FastMCP
from pydantic import BaseModel, Field 
from typing import Annotated, Literal, List,Dict
from MCP.api_web_search_mcp.tavily_search_tool import TavilySearch
import asyncio 



tavily_search = TavilySearch()

server = FastMCP("api-web-search-mcp-server")

class TavilySearchInput(BaseModel) : 
    query: Annotated[str, Field(
        description="Search the web with a short query and get back a list of ranked results with titles, URLs, and text snippets."
    )]
    search_depth: Annotated[Literal[ 'advanced', "basic", "fast", "ultra-fast"],Field(
        description="Controls latency vs relevance tradeoff. 'advanced' : highest relevance, 'basic' : balanced, 'fast' : lower latency, 'ultra-fast' : minimal latency",
        default="basic"
    )]
    chunks_per_source: Annotated[int,Field(
        description="Max number of content chunks (500 chars each) per source. Only available when search_depth is 'advanced'", 
        ge=1, 
        le=3, 
        default=3
    ) ]
    max_results: Annotated[int,Field(
        description="Maximum number of search results to return", 
        ge=1, 
        le=4,
        default=1 
    )]
    topic:Annotated[Literal["general", "news", "finance"],Field(
        description="Search category: 'news' for real-time updates, 'general' for broader searches, 'finance' for financial information",
        default="general"
    )]




@server.tool() 
async def search(search_params:TavilySearchInput)  : 
    """
        Use tavily search apui to do web search 
    """
    tavily_input = search_params.model_dump()
    tavily_result = tavily_search(**tavily_input)

    web_search_result = ""
    for i,result in enumerate(tavily_result["results"]) :
        web_search_result += "title : {title} \n".format(title=result["title"]) + "URL : {url} \n".format(url=result["title"]) + "content : \n {content} \n\n".format(content=result["content"])

    return web_search_result


async def show_tools() : 
    tools = await server.list_tools()
    for tool in tools : 
        tools_dict = tool.parameters 
        print(type(tool.parameters))
        print(tools_dict.keys())
        print(f"tool \n {tools_dict['properties']['search_params']['properties']}")
        

if __name__ == "__main__":
    # Print generated schemas (what LLM sees)
    # server.run(transport="http", host="127.0.0.1", port=8000)
    server.run(transport="stdio")




