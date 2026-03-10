import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any

from app.db.repo_search import search_chunks, search_chunks_keyword
from app.embedding.embedder import embed_texts
from app.core.logging import logger
from app.core.config import settings
from app.retrieval.search import merge_hybrid_results

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEMO_FILE = PROJECT_ROOT / "demo_questions.md"
REPORT_FILE = PROJECT_ROOT / "eval_report.json"

def parse_demo_questions() -> List[Dict]:
    if not DEMO_FILE.exists():
        logger.error(f"Demo file not found at {DEMO_FILE}")
        return []
    
    with open(DEMO_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
    if not match:
        logger.error("Could not find JSON block in demo_questions.md")
        return []
        
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON demo questions: {e}")
        return []

def print_debug_table(results: List[Dict]):
    print(f"\n{'Rank':<5} | {'Score':<6} | {'Dist':<6} | {'k_score':<7} | {'c_score':<7} | {'Doc Type':<8} | {'File Name':<15} | {'Heading':<20} | {'Section Path':<25} | {'Snippet (First 80 chars)'}")
    print("-" * 155)
    for i, r in enumerate(results):
        dist = r.get('distance')
        if dist is not None:
            score = max(0.0, 1.0 - dist)
        else:
            score = r.get('keyword_score', r.get('rank_score', 0.0))
            
        c_score = r.get('combined_score', 0.0)
        k_score = r.get('keyword_score', 0.0)
        dist_str = f"{dist:<6.3f}" if dist is not None else "N/A   "
        
        snippet = r['snippet'].replace('\n', ' ')[:80] + "..." if len(r['snippet']) > 80 else r['snippet'].replace('\n', ' ')
        print(f"{i+1:<5} | {score:<6.3f} | {dist_str} | {k_score:<7.3f} | {c_score:<7.3f} | {r.get('doc_type', '')[:8]:<8} | {r['file_name'][:15]:<15} | {r['heading'][:20]:<20} | {r['section_path'][:25]:<25} | {snippet}")
    print("\n")

def evaluate_question(q_data: Dict, default_k: int, global_doc_type: str = None, debug: bool = False, mode: str = "vector") -> Dict:
    question = q_data["question"]
    k = q_data.get("k", default_k)
    filters = q_data.get("filters", {})
    keywords_any = q_data.get("keywords_any", [])
    keywords_all = q_data.get("keywords_all", [])
    heading_hint = q_data.get("heading_hint", "")
    
    # Extract filter args safely, deferring to global if question string doesn't provide it
    doc_type = filters.get("doc_type")
    if not doc_type and global_doc_type and global_doc_type.lower() != "all":
        doc_type = global_doc_type
    
    try:
        if mode == "vector":
            query_vector = embed_texts([question])[0]
            results = search_chunks(
                query_vector=query_vector,
                k=k,
                doc_type=doc_type
            )
        elif mode == "keyword":
            results = search_chunks_keyword(
                query_text=question,
                k=k,
                doc_type=doc_type
            )
            max_rank = max((r["rank_score"] for r in results), default=0.0)
            for r in results:
                r["keyword_score"] = r["rank_score"] / max_rank if max_rank > 0 else 0.0
        elif mode == "hybrid":
            query_vector = embed_texts([question])[0]
            v_res = search_chunks(query_vector=query_vector, k=settings.VECTOR_CANDIDATES, doc_type=doc_type)
            k_res = search_chunks_keyword(query_text=question, k=settings.KEYWORD_CANDIDATES, doc_type=doc_type)
            results = merge_hybrid_results(v_res, k_res, k=k, alpha=settings.HYBRID_ALPHA)
        else:
            results = []
    except Exception as e:
        logger.error(f"Search failed for '{question}': {e}")
        return {"status": "FAIL", "error": str(e)}
        
    if debug:
        print(f"DEBUG TOP-{k} FOR: {question}")
        print_debug_table(results)
        
    # 3. Validation Logic
    passed = False
    best_rank = None
    matched_kw = None
    best_heading = None
    best_file = None
    
    has_all = bool(keywords_all)
    has_any = bool(keywords_any)
    
    for i, res in enumerate(results):
        text_block = (res['heading'] + " " + res['snippet']).lower()
        
        # 3.1 Check ALL constraints (if provided)
        all_passed = False
        if has_all:
            all_passed = all(kw.lower() in text_block for kw in keywords_all)
            
        # 3.2 Check ANY constraints (if provided)
        any_passed = False
        matched_any_kw = None
        if has_any:
            for kw in keywords_any:
                if kw.lower() in text_block:
                    any_passed = True
                    matched_any_kw = kw
                    break
                    
        # 3.3 Pass condition: if (has_any and any_passed) or (has_all and all_passed)
        if (has_any and any_passed) or (has_all and all_passed):
            passed = True
            best_rank = i + 1
            best_heading = res['heading']
            best_file = res['file_name']
            
            if has_all and all_passed:
                matched_kw = "ALL_MATCHED"
            else:
                matched_kw = matched_any_kw
            break
            
    # Collect strongest retrieved header for hints (even if failed, take Rank 1)
    if not best_heading and len(results) > 0:
        best_heading = results[0]['heading']
        best_file = results[0]['file_name']

    return {
        "id": q_data.get("id", "Unknown"),
        "question": question,
        "status": "PASS" if passed else "FAIL",
        "best_match_rank": best_rank,
        "matched_keyword": matched_kw,
        "heading_hint": heading_hint,
        "best_retrieved_heading": best_heading,
        "best_retrieved_file": best_file
    }

def run_eval(args):
    """Main evaluation runner"""
    mode = args.mode or ("hybrid" if settings.HYBRID_ENABLED else "vector")
        
    if args.debug_question:
        q_data = {
            "id": "DEBUG_1",
            "question": args.debug_question,
            "keywords_any": [],
            "keywords_all": [],
            "heading_hint": "",
            "k": args.k
        }
        res = evaluate_question(q_data, args.k, global_doc_type=args.doc_type, debug=True, mode=mode)
        print("DEBUG QUESTION RESULT:")
        print(json.dumps(res, indent=2))
        return

    questions = parse_demo_questions()
    if not questions:
        return
        
    if args.limit:
        questions = questions[:args.limit]
        
    print(f"Evaluating {len(questions)} questions...")
    results_list = []
    
    for q in questions:
        res = evaluate_question(q, args.k, global_doc_type=args.doc_type, debug=args.debug, mode=mode)
        results_list.append(res)
        
    # Aggregate Metrics
    passed_count = sum(1 for r in results_list if r["status"] == "PASS")
    total = len(results_list)
    failed_count = total - passed_count
    
    pass_rate = (passed_count / total * 100.0) if total > 0 else 0.0
    
    summary = {
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "pass_rate_percent": round(pass_rate, 2),
        "k_used": args.k,
        "mode": mode
    }
    
    failures = [r for r in results_list if r["status"] == "FAIL"]
    
    report = {
        "summary": summary,
        "results": results_list,
        "failures": failures
    }
    
    out_file = PROJECT_ROOT / f"eval_report_{mode}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print("\n" + "="*40)
    print(f"M8 RETRIEVAL EVALUATION SUMMARY (Mode: {mode.upper()})")
    print("="*40)
    print(f"Total Questions: {total}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"Report saved to: {out_file}")
    print("="*40 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M8 Retrieval Evaluation Harness")
    parser.add_argument("--k", type=int, default=6, help="Default k retrieved chunks")
    parser.add_argument("--limit", type=int, help="Limit to N questions")
    parser.add_argument("--debug", action="store_true", help="Print debug top-k tables")
    parser.add_argument("--debug-question", type=str, help="Debug single ad-hoc question")
    parser.add_argument("--doc-type", type=str, help="Filter by document type (pdf, docx)")
    parser.add_argument("--mode", type=str, choices=["vector", "keyword", "hybrid"], help="Search mode")
    
    args = parser.parse_args()
    run_eval(args)
