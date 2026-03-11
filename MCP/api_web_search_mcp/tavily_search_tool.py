from tavily import TavilyClient
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import trafilatura 
import os




class TavilySearch:
    """Simple Tavily search client wrapper."""
    
    def __init__(self):
        """
        Initialize Tavily search client.
        
        Args:
            api_key: Your Tavily API key (starts with 'tvly-')
        """

        load_dotenv() 
        tavily_search_key = os.getenv("TAVILY_SEARCH")
        self.client = TavilyClient(api_key=tavily_search_key)
    


    def extract_with_trafilaura(self, url:str) : 
        try:
            # Method 1: trafilatura (best for articles)
            downloaded = trafilatura.fetch_url(url)
            content = trafilatura.extract(downloaded)
            if content:
                return content
        except:
            pass


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


# Usage example:
if __name__ == "__main__":
    # Initialize with your API key
    tavily = TavilySearch()

    
    
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
    # Perform a search
    results = tavily.search(
        query="eur/usd bullish or bearish",
        max_results=1 , 
        # include_raw_content=True

    )
    
    # Print results
    print(f"Query: {results['query']}")
    print(f"\nFound {len(results['results'])} results:\n")
    
    cleaned_html = None 
    
    
    for i, result in enumerate(results['results'], 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Content **: {result['content']}...\n")
        print(f" full content :   {result['raw_content']} ")



