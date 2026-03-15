from typing import Dict, Any, Optional
from MCP.api_web_search_mcp.tavily_search_tool import TavilySearch 
from inference.llm_call import LLMCall
from inference.inference_utils import SamplingParams, AnthropicSamplingParams
import logging


# Usage example:
if __name__ == "__main__":

    logger = logging.Logger(__file__)
    sampling_params = AnthropicSamplingParams() 

    claude_call = LLMCall("claude-haiku-4-5-20251001",sampling_params,logger) 



    # Initialize with your API key
    tavily = TavilySearch(claude_call,"rephrase_content")

    
    
    BLOG_DOMAINS = [
    "medium.com",
    "substack.com",
    "wordpress.com",
    "blogspot.com",
    "seekingalpha.com",  # Financial blogs
    "investing.com/analysis",
    "fxstreet.com",
    "dailyfx.com",
    "forexlive.com",
    "actionforex.com"
    ]

    user_query = "eur/usd bullish or bearish in q2 2026"
    # Perform a search
    results = tavily(
        query="eur/usd bullish or bearish in q2 2026",
        search_depth = "advanced", 
        chunks_per_source = "2", 
        max_results=2, 
        topic="general"
    )
    
    # Print results
    print(f"Query: {results['query']}")
    print(f"\nFound {len(results['results'])} results:\n")
    
    cleaned_html = None 
    
    
    for i, result in enumerate(results['results'], 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f" \n  raw content **: \n {result['raw_content']}")
        print("\n\n")
        summary = tavily.summarize_markdown(user_query,result)
        print("******** SUMMARY ***********") 
        print(summary)
        print("\n\n")
        # print(f" full content :   {result['raw_content']} ")
