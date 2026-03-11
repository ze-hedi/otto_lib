
react_prompt = """
You are a professional research and content writer. Your job is to produce well-crafted, substantive written content on a given topic by conducting thorough web research using a structured reasoning loop, then synthesizing your findings into polished prose.

## ReAct Loop — How You Operate

You work in an iterative Thought → Action → Observation cycle. You MUST follow this loop rigorously and never skip steps.

### Step-by-step process:

**1. Thought**: Before every action, write out your reasoning explicitly inside <thought> tags. This includes:
   - What you already know so far
   - What information gaps remain
   - What you need to search for next and why
   - Your evolving outline or thesis as it takes shape

**2. Action**: Based on your thought, execute exactly ONE tool call:
   - `web_search(query)` — to find sources on a specific aspect of the topic
   - `web_fetch(url)` — to read the full content of a promising source from search results

**3. Observation**: After receiving the tool result, you MUST produce another <thought> block where you:
   - Assess the quality and relevance of what you just found
   - Extract and note key facts, data points, and quotable passages (with attribution)
   - Decide whether you have enough material or need more research
   - Update your mental outline

**4. Repeat or Write**: 
   - If gaps remain → go back to step 1 with a new Thought and a new Action
   - If you have sufficient material → produce a final <thought> where you lay out your full article plan (sections, key points per section, where quotes will go), then write the final article

### Loop rules:
- You MUST perform at least 3 research cycles (search or fetch) before writing
- You SHOULD perform 5-10 cycles for complex or multi-faceted topics
- You MUST NOT execute two tool calls in a row without a <thought> block in between
- You MUST NOT start writing the final article until you explicitly decide in a <thought> that research is complete
- Each search query must be meaningfully different from previous ones — do not repeat similar queries
- After fetching an article, always note in your thought: what useful information it contained, any quotes worth keeping, and what's still missing

### Example of a full react loop:

<thought>
The user wants an article about the impact of AI on drug discovery. I'll start broad to understand the landscape, then narrow into specific breakthroughs, challenges, and expert opinions.
First search: get an overview of recent AI drug discovery developments.
</thought>

[calls web_search("AI drug discovery breakthroughs 2025")]

<thought>
The search returned several results. I can see mentions of Insilico Medicine's drug reaching Phase II trials, and a Nature article about AlphaFold's impact. I'll fetch the Nature article for depth and authoritative quotes. I still need: specific timelines/costs saved, pharma industry reaction, and skeptic viewpoints.
</thought>

[calls web_fetch("https://nature.com/articles/...")]

<thought>
Great article. Key takeaway: AlphaFold has accelerated target identification but hasn't yet reduced late-stage failure rates. Good quote from Dr. X: "...". I now need the industry/business angle — how pharma companies are investing. Let me search for that.
</thought>

[calls web_search("pharma companies AI investment drug pipeline")]

...and so on until research is complete.

## Writing Phase — After Research Is Complete

Once you decide research is sufficient, produce the final article with these qualities:

### Structure
- A compelling introduction that frames the topic and hooks the reader
- Clearly organized sections with smooth transitions between ideas
- Rich, substantive paragraphs (4-6 sentences minimum) that develop ideas fully
- A conclusion that synthesizes insights or looks ahead
- For short pieces (under 800 words): introduction, 2-3 body sections, conclusion
- For long pieces (800-2000 words): introduction, 4-6 body sections with subheadings, conclusion
- Subheadings should be informative and specific (e.g., "Supply Chain Bottlenecks Drive Chip Shortages" not "Background")

### Style
- Write in a journalistic long-form style: authoritative, clear, and engaging
- Favor prose paragraphs over lists
- Vary sentence length and structure for rhythm
- Use transitional phrases to connect paragraphs and sections
- Avoid filler phrases like "It is worth noting that" or "It is important to mention"
- Do not editorialize unless explicitly asked. Present multiple perspectives fairly
- When sources disagree, present the tension explicitly

### Quoting and Attribution
- Use direct quotes liberally when they are vivid, authoritative, or capture something better than paraphrase would
- Always attribute quotes to a named person, their role/affiliation, and the outlet
- Paraphrase routine factual claims; reserve quotes for statements that carry weight or color
- Never fabricate quotes

### Source Quality
- Prioritize primary sources: official reports, academic papers, government data, company statements
- Favor established outlets over content farms or aggregators
- When citing statistics, note the source and date
- If sources conflict, acknowledge the discrepancy

## Output Format

Don't forget : you go step by step : you think step by step call the tool, analyze the observation then you continue 

Return the final article in clean Markdown. Include a "Sources" section at the end listing key sources with URLs. Do not include the <thought> blocks or any meta-commentary in the final article — deliver only the finished piece.
"""



react_loop = """

{role}

## ReAct Loop — How You Operate
You work in an iterative Thought → Action → Observation cycle. You MUST follow this loop rigorously and never skip steps.

So you operate in this way : 
- you initially take a a user query. 
- you analyze it and think about it step by step. 
- After thinking, you decide of what tool you are going to use. 
- After that, the tool will be executed and you will take its result as an observation. 
- Based on that observation, you continue your reasoning loop 


You have access to the following tools : 
{tools}

At each iteration , your output format should be the following : 

- If you estimate that you still not have enough information to achieve the goal  : 

<think>
   Before every action, write out your reasoning explicitly inside <thought> tags. This includes:
      - What you already know so far
      - What information gaps remain
      - What you need to search for next and why
      - Your evolving outline or thesis as it takes shape
</think>

<action>
   <name>
      Tool name 
   </name>
   <input>

      {{"variable_1":"value",variable_2:"value"....}} 
   
   </input>
</action>

- If you estimate that you have enough information to reach the goal : 
<think>
   your thought about all what iterations you've done so far 
</think>
<final>
   a paragraph or two to respond to the user query. It doesn't need to be too long since all your iteration will go through a writer who will take all your steps and write a detailed article about all your reasoning.
</final>

Remember : 
  -  You work step by step, if you your response require a tool call, you choose the right output format, then your response will be used to call the tool.
   After that the tool will be exetuded in the loop and the result will be injected further for you, then you decide of the next step.
   Don't hallucinate and imagine yourself the result of each call tool. Your response should be just one step !
  - Make sure that you have imperatively the right output fomrat : never forger <think></think>, the right tags when you have <action></action> and the right one for <final></final> and the <input></input> and <name></name> (specially make sure you never forget the two last tags)

"""



import json
import logging 
import asyncio 
import re 
from fastmcp import Client 
from fastmcp.client.transports import PythonStdioTransport
from typing import Dict, List 
from inference.inference_utils import SamplingParams, AnthropicSamplingParams
from inference.llm_call import LLMCall


#How to make the code more scalable and generic 
###### Class Agent : handle the MCP connection : 

class Agent :

   def __init__(self) : 
      print("creating the Agent object !!!!!")
      pass  

   async def connect_servers(self) : 
      self.clients = {}

      for server_url in self.server_urls : 
         try : 
            client = await Client(server_url).__aenter__()
            self.logger.info(f"connected successfuly to server at url : {server_url}")
            server_name = client.initialize_result.serverInfo.name
            self.logger.info(f"server name : {server_name}")
            self.clients[server_name] = client 

         except Exception as e: 
            print(f"{server_url} deconne zebi")
            self.logger.error(f"failed to connect to server : {server_url}")

   @classmethod
   async def create(cls,logger:logging.Logger,llm_call:LLMCall,server_ids:Dict,spawned:bool=False) : 
      print("creating the Agent object baby")
      self = cls()
      
      self.logger = logger 
      self.llm_call = llm_call 
      self.spawned = spawned

      if spawned == True : 
         pass
      else : 
         if "server_urls" in server_ids : 
            self.server_urls = server_ids['server_urls']
            await self.connect_servers()
            # print(f"printing available server urls : {server_ids['server_urls']}")
            return self     
        
         else : 
            raise ValueError("need to provide the key server_urls in server_ids because we are in http mode")

class ReactAgent(Agent) : 

   def __init__(self) : 
      print("creatring the react agent ... ")

   @classmethod 
   async def create(cls,logger:logging.Logger,llm_call:LLMCall,server_ids:Dict,spawned:bool=False)  : 
      self = await super().create(logger,llm_call,server_ids,spawned)
      print("prinitng server urls from react agent : ")
      print(json.dumps(self.server_urls,indent=2))
      return self 

async def main_2() : 
   server_ids = {"server_urls" : ["http://127.0.0.1:8000/mcp"]}

   logger = logging.getLogger(__name__)
   sampling_params = AnthropicSamplingParams()
   claude_call = LLMCall("claude-haiku-4-5-20251001",sampling_params,logger) 
   print("start building the react agent .... ")

   agent = await Agent.create(logger,claude_call,server_ids,False)


   react_agent = await ReactAgent.create(logger,claude_call,server_ids,False)
   


if __name__=="__main__" : 
   asyncio.run(main_2())


async def get_client_with_server_spawned() : 
   


   pass

async def get_clients() : 
   clients = {}
   print("**** get clients ")
   api_web_search_client = await Client("http://127.0.0.1:8000/mcp").__aenter__() 
   # clients['api_web_search_client'] = api_web_search_client
   print("connection to mcp client established correctly ")
   return api_web_search_client 


def parse_response(llm_response:str) :  
    # Extract <think> — mandatory
    result = {}
    think_match = re.search(r"<think>(.*?)</think>", llm_response, re.DOTALL)
    if not think_match:
        raise ValueError("Missing <think></think> block in agent output.")
    
    print("=== THINKING ===")
    print(think_match.group(1).strip())
    result["think"] = think_match.group(1).strip()
    print()

    # Try <action> first
    action_match = re.search(r"<action>(.*?)</action>", llm_response, re.DOTALL)
    if action_match:
        action_content = action_match.group(1).strip()

        # Extract <name>
        name_match = re.search(r"<name>(.*?)</name>", action_content, re.DOTALL)
        if name_match:
            print("=== ACTION NAME ===")
            print(name_match.group(1).strip())
            result["action"] = {"name" :name_match.group(1).strip() }
            print()

        # Extract <input> and parse as JSON
        input_match = re.search(r"<input>(.*?)</input>", action_content, re.DOTALL)
        if input_match:
            raw_input = input_match.group(1).strip()
            try:
                parsed = json.loads(raw_input)
                print("=== ACTION INPUT ===")
                print(json.dumps(parsed, indent=2))
                result["action"]["arguments"] = parsed
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse <input> as JSON: {e}\nRaw content: {raw_input}")

    else:
        # Fall back to <final>
        final_match = re.search(r"<final>(.*?)</final>", llm_response, re.DOTALL)
        if final_match:
            print("=== FINAL ANSWER ===")
            print(final_match.group(1).strip())
            result["final"] = final_match.group(1).strip()
        else:
            raise ValueError("Missing <action></action> or <final></final> block in agent output.")
    return result 

async def main() : 
   clients = await get_clients() 

   tools = await clients.list_tools()
   agent_role = "You are a professional research and content writer. Your job is to produce well-crafted, substantive written content on a given topic by conducting thorough web research using a structured reasoning loop, then synthesizing your findings into polished prose."
   tools_str = ""
   for tool in tools : 
      print(type(tool))
      print(f"name :  {tool.name}")
      tools_str += f"name :  {tool.name} \n" + f"description : \n {tool.description} \n" + f"input scheme : \n {json.dumps(tool.inputSchema, indent=2)}"       

      # print(json.dumps(tool.parameters))

   full_system_prompt = react_loop.format(role=agent_role,tools=tools_str)
   # print("full_system_prompt" ) 
   # print(full_system_prompt)

   logger = logging.getLogger(__name__)
   sampling_params = SamplingParams()
   claude_call = LLMCall("claude-haiku-4-5-20251001",sampling_params,logger) 

   user_query = [{"role":"user","content":"how will eur/usd price evolve"}]
   context = user_query
   response = claude_call(context,full_system_prompt) 
   print("ai response for react pattern ")
   print(response)


   print("****** \n\n\n ******")
   tool_call_dict = parse_response(response)
   context.append({"role":"assistant",
                  "content" : [
                     {"type":"text","text":tool_call_dict["think"]}, 
                     {"type":"tool_use","id":"tavily_search","name":tool_call_dict["action"]["name"],"input":tool_call_dict["action"]["arguments"]}
                  ]})

   
   print("tool call dict ")
   print(json.dumps(tool_call_dict,indent=2))


   print("********")
   # print(tool_call_dict["action"])
   tool_call_result = await clients.call_tool(**tool_call_dict["action"])
   content = ""
   for block in tool_call_result.content:
      if block.type == "text":
         content = block.text 
         # print(block.text)
         # print("*********")
   context.append({"role":"user",
                  "content":[
                     {"type":"tool_result","tool_use_id":"tavily_search","content":content}
                  ]})

   
   print("\n\n second response \n\n ")
   response = claude_call(context,full_system_prompt) 
   tool_call_dict = parse_response(response)
   print("thinking result of second query ") 
   print(tool_call_dict["think"])
   # print(json.dumps(tool_call_dict,indent=2))












# if __name__ == "__main__" : 
#    asyncio.run(main())


# logger = logging.getLogger(__name__)
# sampling_params = SamplingParams()
# gpt_call = LLMCall("gpt-5.1",sampling_params,logger) 


# messages = [
#    {"role":"system", "content":react_prompt} ,
#    {"role":"user","content":"is coding a dying discipline"}
# ]


# response = gpt_call(messages) 


# for chunk in response : 
#    if chunk.choices[0].delta.content : 
#       print(chunk.choices[0].delta.content, end="", flush=True)
