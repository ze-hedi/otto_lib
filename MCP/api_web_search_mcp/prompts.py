

rephrase_content_prompt = """ 
You are a context formatter. Given raw web search results, rewrite them into clean, dense, information-rich paragraphs ready to be injected into an AI agent's context.

Rules:
- Preserve all factual content, numbers, dates, and named entities
- Remove redundancy, ads, navigation text, and boilerplate
- Group related information together
- Output plain prose, no bullet points, no markdown headers
- Keep source attribution inline: (source: <title>, <url>)

Search results:
{SEARCH_RESULTS}

"""

summarize_markdown_prompt = """
You are summarizing a web page to help answer a specific research question.
Focus only on information relevant to the question, ignore the rest. Adjust the length to the informational density of the content:
- Simple or redundant content: 2-3 sentences
- Average content: 4-6 sentences  
- Dense technical or data-rich content: up to 10 sentences

Question/Step: {QUERY_OR_STEP}
Source: {TITLE} — {URL}

Content:
{CONTENT}

Summarize in dense, factual prose. Adjust length to relevance — skip the page entirely with "NOT RELEVANT" if it contains nothing useful.

"""