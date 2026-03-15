from tavily import TavilyClient
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from inference.llm_call import LLMCall
from MCP.api_web_search_mcp.prompts import rephrase_content_prompt, summarize_markdown_prompt
import trafilatura 
import os
import logging 



class TavilySearch:
    """Simple Tavily search client wrapper."""
    
    def __init__(self,llm_call:LLMCall,search_mode:str="default"):
        """
        Initialize Tavily search client.
        
        Args:
            api_key: Your Tavily API key (starts with 'tvly-')
        """
        self.llm_call = llm_call
        self.search_mode = search_mode
        load_dotenv() 
        tavily_search_key = os.getenv("TAVILY_SEARCH")
        self.client = TavilyClient(api_key=tavily_search_key)
    
    def rephrase_content(self,result:Dict) : 
        prompt = f"""Title
{result['title']}

Url : 
{result['url']}

content : 
{result['content']}"""
        prompt = rephrase_content_prompt.format(SEARCH_RESULTS=prompt)
        messages = [{
            "role" : "user", 
            "content" : prompt
        }]

        rephrased_prompt = self.llm_call(messages) 
        return  rephrased_prompt

    def summarize_markdown(self,user_query:str,result:Dict) : 
        prompt = summarize_markdown_prompt.format(QUERY_OR_STEP=user_query, TITLE=result['title'],
                                                  URL=result['url'],CONTENT=result['raw_content'])

        messages = [{
            "role" : "user", 
            "content" : prompt
        }]
        summary = self.llm_call(messages)
        return summary

    def __call__(self, query: str,search_depth:str, chunks_per_source:str, max_results:int, topic:str) -> Dict[str, Any]:
        """
        Execute a search query.
        
        Args:
            query: The search query string
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            Dictionary containing search results with keys:
            - query: The executed query
            - results: List of search results
            - response_time: Time taken for the search
        """

#         BLOG_DOMAINS = [
#     "medium.com",
#     "substack.com",
#     "wordpress.com",
#     "blogspot.com",
#     "seekingalpha.com",  # Financial blogs
#     "investing.com/analysis",
#     "fxstreet.com",
#     "dailyfx.com",
#     "forexlive.com",
#     "actionforex.com"
# ]
        response = self.client.search(
            query=query,
            search_depth=search_depth, 
            max_results=max_results,
            chunks_per_source=chunks_per_source,
            topic=topic, 
            include_raw_content=True
        )
        
        return response





