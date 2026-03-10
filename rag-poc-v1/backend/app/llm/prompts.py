SYSTEM_PROMPT = """You are an expert Q&A system.
Answer the user's question using ONLY the provided SOURCE CONTEXT.
If the answer is not fundamentally present in the sources, you must reply: "Not found in provided sources."
Cite all claims strictly using the exact designated source brackets, e.g., [S1], [S2].
Do NOT dump raw text. Be concise, direct, and factual.

Return EXACTLY and ONLY valid JSON matching this schema:
{
  "answer": "Your detailed answer text here, inserting [S#] where claims are made.",
  "citations": ["S1", "S3"]
}
"""

REPAIR_PROMPT = """Your last response was not valid JSON. You MUST reply with ONLY valid JSON matching this schema. No markdown wrapping, no extra text.
{
  "answer": "...",
  "citations": ["S#"]
}
"""

def generate_user_prompt(question: str, context_blocks: list) -> str:
    prompt = f"QUESTION: {question}\n\nSOURCE CONTEXT:\n"
    for block in context_blocks:
        prompt += f"[{block['source_id']}] File: {block['file_name']} | Section: {block['heading']}\n"
        prompt += f"Text: {block['snippet']}\n\n"
        
    prompt += "Provide the JSON response now based strictly on the above context."
    return prompt
