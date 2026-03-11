from vllm import LLM, SamplingParams 


llm = LLM(
    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    gpu_memory_utilization=0.5,  # Lower memory usage
    max_model_len=1024,           # Reduce context
    max_num_seqs=8,               # Smaller batch
    trust_remote_code=True,
)
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=256,
    presence_penalty=0.0,
    frequency_penalty=0.0,
)