import re
from typing import List, Dict

MIN_WORDS = 150
TARGET_WORDS = 500
OVERLAP_WORDS = 50
STOPWORDS = {"TERMS", "VARIABLES", "SIGNATURE", "RECITALS"}

def estimate_tokens(text: str) -> int:
    return int(len(text.split()) * 1.3)

def is_heading(line: str) -> bool:
    line = line.strip()
    if not line:
        return False
        
    # Heuristic 1: Article/ARTICLE with roman numerals or numbers
    if re.match(r'^\s*(ARTICLE|Article)\s+[IVXLC0-9]+\b', line):
        return True
        
    # Heuristic 2: Numbered sections like 1.1 or 2.1.3 followed by text
    if re.match(r'^\s*\d+(\.\d+)*\s+[A-Z][A-Za-z].{0,80}$', line):
        return True
        
    # Heuristic 3: Mostly uppercase
    alphas = [c for c in line if c.isalpha()]
    if alphas:
        upper_ratio = sum(1 for c in alphas if c.isupper()) / len(alphas)
        if upper_ratio >= 0.8:
            words = line.split()
            # Must be multi-word or long enough and not a stopword
            if len(words) >= 2 or (len(line) >= 12 and line.upper() not in STOPWORDS):
                return True
                
    return False

def split_text(text: str) -> List[Dict]:
    lines = text.split('\n')
    
    # 1. First Pass: Group physical text into raw sections under headings
    raw_sections = []
    current_heading = "Document Start"
    current_section_lines = []
    
    for line in lines:
        if is_heading(line):
            if current_section_lines:
                raw_sections.append((current_heading, '\n'.join(current_section_lines).strip()))
            current_heading = line.strip()
            current_section_lines = []
        else:
            current_section_lines.append(line)
            
    if current_section_lines:
        raw_sections.append((current_heading, '\n'.join(current_section_lines).strip()))
        
    # 2. Second Pass: Split massive sections > 900 words into paragraphs
    sub_sections = []
    for heading, section_text in raw_sections:
        if not section_text:
            continue
            
        words_count = len(section_text.split())
        if words_count > 900:
            paragraphs = section_text.split('\n\n')
            current_chunk_paragraphs = []
            current_chunk_words = 0
            
            for p in paragraphs:
                p_text = p.strip()
                if not p_text: continue
                p_words = len(p_text.split())
                
                if current_chunk_words + p_words > TARGET_WORDS and current_chunk_paragraphs:
                    chunk_str = '\n\n'.join(current_chunk_paragraphs).strip()
                    sub_sections.append((heading, chunk_str))
                    
                    # Create overlap
                    overlap_paras = []
                    overlap_w_count = 0
                    for prev_p in reversed(current_chunk_paragraphs):
                        prev_p_words = len(prev_p.split())
                        if overlap_w_count + prev_p_words > OVERLAP_WORDS and overlap_paras:
                            break
                        overlap_paras.insert(0, prev_p)
                        overlap_w_count += prev_p_words
                        
                    current_chunk_paragraphs = overlap_paras + [p_text]
                    current_chunk_words = overlap_w_count + p_words
                else:
                    current_chunk_paragraphs.append(p_text)
                    current_chunk_words += p_words
                    
            if current_chunk_paragraphs:
                chunk_str = '\n\n'.join(current_chunk_paragraphs).strip()
                if chunk_str:
                    sub_sections.append((heading, chunk_str))
        else:
            sub_sections.append((heading, section_text))
            
    # 3. Third Pass: Packing logic for small chunks
    final_chunks = []
    buffer_text = []
    buffer_words = 0
    buffer_first_heading = ""
    had_multiple_headings = False
    
    for heading, text_body in sub_sections:
        body_words = len(text_body.split())
        
        # Start new buffer
        if not buffer_text:
            buffer_first_heading = heading
            had_multiple_headings = False
            
        # If continuing a buffer across different headings, add separator
        if buffer_text and heading != buffer_first_heading:
            buffer_text.append(f"\n\n--- {heading} ---")
            had_multiple_headings = True
            
        buffer_text.append(text_body)
        buffer_words += body_words
        
        # Emit buffer if it crosses MIN_WORDS
        if buffer_words >= MIN_WORDS:
            chunk_str = '\n\n'.join(buffer_text).strip()
            section_path = f"Packed: {buffer_first_heading}" if had_multiple_headings else buffer_first_heading
            
            final_chunks.append({
                "heading": buffer_first_heading,
                "section_path": section_path,
                "chunk_text": chunk_str,
                "token_count": estimate_tokens(chunk_str)
            })
            # Reset buffer
            buffer_text = []
            buffer_words = 0
            buffer_first_heading = ""
            had_multiple_headings = False

    # 4. Handle remaining minimal buffer
    if buffer_text:
        chunk_str = '\n\n'.join(buffer_text).strip()
        
        # Merge backwards if final_chunks exist AND buffer is too small
        if final_chunks and buffer_words < MIN_WORDS:
            if buffer_first_heading != final_chunks[-1]["heading"]:
                 final_chunks[-1]["chunk_text"] += f"\n\n--- {buffer_first_heading} ---\n\n" + chunk_str
            else:
                 final_chunks[-1]["chunk_text"] += "\n\n" + chunk_str
            
            # Recalculate tokens & update section path to denote packing
            final_chunks[-1]["token_count"] = estimate_tokens(final_chunks[-1]["chunk_text"])
            if not final_chunks[-1]["section_path"].startswith("Packed:"):
                 final_chunks[-1]["section_path"] = f"Packed: {final_chunks[-1]['heading']}"
        else:
            # Emit standalone (either no prior chunks, or it's > MIN_WORDS anyway)
            section_path = f"Packed: {buffer_first_heading}" if had_multiple_headings else buffer_first_heading
            final_chunks.append({
                "heading": buffer_first_heading,
                "section_path": section_path,
                "chunk_text": chunk_str,
                "token_count": estimate_tokens(chunk_str)
            })

    return final_chunks
