import time
import json
import re
from app.api.ask import AskRequest, AskResponse, CitationItem
from app.api.search import SearchRequest
from app.retrieval.search import perform_search
from app.core.logging import logger
from app.llm.client import generate_answer
from app.llm.prompts import SYSTEM_PROMPT, REPAIR_PROMPT, generate_user_prompt

MAX_CHUNK_CHARS = 1500
MAX_TOTAL_CONTEXT_CHARS = 10000

def perform_ask(request: AskRequest) -> AskResponse:
    start_time = time.time()
    
    # 1. Retrieve the context
    search_req = SearchRequest(
        question=request.question,
        k=request.k_chunks,
        filters=request.filters
    )
    search_res = perform_search(search_req)
    raw_chunks = search_res.results
    
    # 2. Build the context blocks within token limits
    context_blocks = []
    total_chars = 0
    
    for i, c in enumerate(raw_chunks):
        snippet = c.snippet[:MAX_CHUNK_CHARS]
        # Approximate size check avoiding exact tokenization overhead
        if total_chars + len(snippet) > MAX_TOTAL_CONTEXT_CHARS:
            logger.warning(f"Context max size reached. Dropping remaining {(len(raw_chunks) - i)} lower-ranked chunks.")
            break
            
        block = {
            "source_id": f"S{i+1}",
            "chunk_id": c.chunk_id,
            "file_name": c.file_name,
            "heading": c.heading,
            "section_path": c.section_path,
            "snippet": snippet
        }
        context_blocks.append(block)
        total_chars += len(snippet)
        
    user_prompt = generate_user_prompt(request.question, context_blocks)
    
    if request.dry_run:
        return AskResponse(
            used_chunks_count=len(context_blocks),
            latency_ms=int((time.time() - start_time) * 1000),
            debug_info={
                "prompt_length_chars": len(user_prompt),
                "context_blocks_passed": len(context_blocks),
                "system_prompt": SYSTEM_PROMPT,
                "user_prompt": user_prompt
            }
        )
        
    if not context_blocks:
        return AskResponse(
            answer="Not found in provided sources.",
            used_chunks_count=0,
            latency_ms=int((time.time() - start_time) * 1000)
        )
        
    # 3. Call LLM
    llm_res = generate_answer(SYSTEM_PROMPT, user_prompt)
    if not llm_res.get("success"):
        return AskResponse(
            answer="Not found in provided sources.",
            latency_ms=int((time.time() - start_time) * 1000),
            debug_info={"error": llm_res.get("error")}
        )
        
    # 4. JSON Parse & Repair Logic
    # We attempt strict JSON parsing. If it fails, do ONE repair.
    raw_content = llm_res["content"]
    parsed = None
    
    def try_parse(content: str):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None
            
    parsed = try_parse(raw_content)
    
    if not parsed:
        logger.warning("LLM first output was invalid JSON. Executing repair prompt.")
        repair_user_prompt = f"Original question context...\n\n{REPAIR_PROMPT}\n\nThe invalid string you returned was:\n{raw_content}"
        repair_res = generate_answer(SYSTEM_PROMPT, repair_user_prompt)
        if repair_res.get("success"):
            parsed = try_parse(repair_res["content"])
            
    if not parsed:
        logger.error("LLM failed strict JSON formatting after repair. Degraded output returned.")
        return AskResponse(
            answer="Not found in provided sources.",
            latency_ms=int((time.time() - start_time) * 1000),
            debug_info={"error": "JSON parse failed on both generation strings"}
        )
        
    answer_text = parsed.get("answer", "")
    citations_list = parsed.get("citations", [])
    
    if not isinstance(citations_list, list):
        citations_list = []
        
    # 5. Citation Integrity (Anti-Laundering)
    valid_source_ids = {b["source_id"] for b in context_blocks}
    safe_citations = []
    
    for c_id in citations_list:
        if c_id in valid_source_ids:
            safe_citations.append(c_id)
            
    # Strip any brackets entirely that are physically in the string but NOT in the safe list
    # e.g., if valid is S1, S2, we want to strip [S99], [S3], etc.
    # regex finds all brackets starting with S and digits inside
    def strip_fake_citations(match):
        raw_token = match.group(1) # S1, S99
        if raw_token not in safe_citations:
            return ""
        return match.group(0) # Keep valid
        
    answer_text = re.sub(r'\[(S\d+)\]', strip_fake_citations, answer_text)
    
    # Strip multiple consecutive spaces if regex left holes
    answer_text = re.sub(r' +', ' ', answer_text).strip()
    
    # Validation constraint
    if not safe_citations and getattr(request, "question", "") and answer_text:
         # Optionally check if answer text indicates it was found. Provide fallback.
         pass
         
    final_citations = []
    for safe_id in safe_citations:
        for block in context_blocks:
            if block["source_id"] == safe_id:
                final_citations.append(CitationItem(
                    source_id=safe_id,
                    chunk_id=block["chunk_id"],
                    file_name=block["file_name"],
                    heading=block["heading"],
                    section_path=block["section_path"],
                    snippet=block["snippet"]
                ))
                break

    # Final Failure Edge Case Control
    if len(final_citations) == 0 and "not found" not in answer_text.lower():
        # Fallback if no citations remained valid but model hallucinated
        answer_text = "Not found in provided sources."
        
    return AskResponse(
        answer=answer_text,
        citations=final_citations,
        used_chunks_count=len(context_blocks),
        latency_ms=int((time.time() - start_time) * 1000)
    )
