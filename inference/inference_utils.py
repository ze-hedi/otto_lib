from typing import Dict, Optional, List
from pydantic import BaseModel 

class SamplingParams(BaseModel) : 
    pass 

class AnthropicSamplingParams(SamplingParams) : 
    max_tokens :int = 1024

    system_prompt:str = None

class OpenAISamplingParams(SamplingParams) : 
    
    # Range: 0-2. Controls randomness.
    # Higher = more random/creative. Lower = more focused/deterministic.
    temperature :float= 1.0

    # Range: 0-1. Nucleus sampling. 
    # Considers tokens with top_p probability mass.
    # Alternative to temperature. Don't use both.
    top_p: float=1.0

    # Maximum tokens to generate in completion.
    # Default: inf (model's context length limit)
    # max_tokens: int=None

    # Number of completions to generate for each prompt.
    n : int=1

    # Range: -2.0 to 2.0. Penalizes tokens based on whether they appear.
    # Positive = encourage new topics. Negative = stay on topic.
    presence_penalty : float =0.0


    # Range: -2.0 to 2.0. Penalizes tokens based on frequency.
    # Positive = reduce repetition. Negative = allow repetition.
    frequency_penalty : float =0.0

    # Dict mapping token IDs to bias values (-100 to 100).
    # Modify likelihood of specified tokens appearing.
    logit_bias : int =None


    # Integer. For deterministic sampling (beta feature).
    # Same seed + params = similar outputs.
    seed : int =None


    # String or list of strings. Stop sequences.
    # Generation stops when these appear.
    stop : List =None
