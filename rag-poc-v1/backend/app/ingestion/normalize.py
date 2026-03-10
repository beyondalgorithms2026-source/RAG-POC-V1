import re

def normalize_text(text: str) -> str:
    if not text:
        return ""

    # remove common page artifacts best-effort
    text = re.sub(r'^[ \t]*Page \d+(?: of \d+)?[ \t]*$', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # de-hyphenate word breaks across newlines
    text = re.sub(r'([a-zA-Z])-\n([a-zA-Z])', r'\1\2', text)
    
    # collapse multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    
    # collapse 3+ newlines to max 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
