# RAG PoC v1 - Demo Questions

The following JSON block is parsed by the automated retrieval test harness. Provide keywords to strictly evaluate vector search recall accuracy.

```json
[
  {
    "id": "Q1",
    "question": "What is Confidential Information?",
    "keywords_any": ["Confidential Information", "non-public", "proprietary"],
    "keywords_all": [],
    "heading_hint": "TERMS",
    "k": 6,
    "filters": {"doc_type": "docx"}
  },
  {
    "id": "Q2",
    "question": "Who can the Receiver share information with?",
    "keywords_any": ["Permitted Receivers", "employees", "affiliates"],
    "keywords_all": [],
    "heading_hint": "TERMS",
    "k": 6
  },
  {
    "id": "Q3",
    "question": "For what purpose can the confidential info be used?",
    "keywords_any": ["Purpose"],
    "keywords_all": ["Permitted", "Receivers"],
    "heading_hint": "TERMS",
    "k": 6
  },
  {
    "id": "Q4",
    "question": "How long do the confidentiality obligations last?",
    "keywords_any": ["3 years", "three years", "survival"],
    "keywords_all": [],
    "heading_hint": "SURVIVAL",
    "k": 6
  },
  {
    "id": "Q5",
    "question": "Are there limits on liability?",
    "keywords_any": ["liability", "indirect", "consequential"],
    "keywords_all": [],
    "heading_hint": "LIABILITY",
    "k": 6
  }
]
```
