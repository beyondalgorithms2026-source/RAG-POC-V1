# RAG PoC v1 - Demo Questions

The following JSON block is parsed by the automated retrieval test harness. Provide keywords to strictly evaluate vector search recall accuracy.

```json
[
  {
    "id": "Q01",
    "question": "What is the maximum length of the agreement term (in months)?",
    "keywords_any": ["thirty (30) months", "30 months"],
    "keywords_all": [],
    "heading_hint": "2.1",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q02",
    "question": "What is the agreement’s Effective Date called and when does the Term commence?",
    "keywords_any": ["Effective Date", "Term shall commence"],
    "keywords_all": [],
    "heading_hint": "2.1",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q03",
    "question": "What interest rate applies to overdue payment amounts?",
    "keywords_any": ["6% per year", "interest"],
    "keywords_all": [],
    "heading_hint": "5.3",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q04",
    "question": "What license is granted to use the other party’s Marks and Content (key terms like worldwide/non-exclusive)?",
    "keywords_any": ["worldwide", "non-exclusive", "limited, non-transferable"],
    "keywords_all": [],
    "heading_hint": "6.1",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q05",
    "question": "Who owns user data generated within the network (user data ownership clause)?",
    "keywords_any": ["About User Data", "shall own"],
    "keywords_all": [],
    "heading_hint": "9.2",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q06",
    "question": "What uptime percentage is required for a hosted service during the Term?",
    "keywords_any": ["99.0%", "ninety nine percent"],
    "keywords_all": [],
    "heading_hint": "13.4",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q07",
    "question": "Which section covers indemnification and includes 'indemnify' language?",
    "keywords_any": ["INDEMNIFICATION", "indemnify", "hold harmless"],
    "keywords_all": [],
    "heading_hint": "11.",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q08",
    "question": "Which states are specified for governing law and litigation venue?",
    "keywords_any": ["Illinois", "New York", "governed by the laws"],
    "keywords_all": [],
    "heading_hint": "15.4",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q09",
    "question": "What does the assignment clause say about needing written consent and assignment to an affiliate/successor?",
    "keywords_any": ["assign", "written consent", "affiliate", "successor"],
    "keywords_all": [],
    "heading_hint": "15.6",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q10",
    "question": "Who hosts the Insurance Center and what wrapper is it contained in?",
    "keywords_any": ["hosted solely by ebix", "About Wrapper"],
    "keywords_all": [],
    "heading_hint": "3.2",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q11",
    "question": "What is the Effective Date of the co-branding agreement?",
    "keywords_any": ["May 22, 2000", "Effective Date"],
    "keywords_all": [],
    "heading_hint": "CO-BRANDING",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q12",
    "question": "Which party stores and serves the Gateway Page and where are the servers located?",
    "keywords_any": ["store and maintain the Gateway Page", "server(s) located"],
    "keywords_all": [],
    "heading_hint": "1.2",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q13",
    "question": "Who has sole responsibility for providing and maintaining the Diet Center beneath the Gateway Page?",
    "keywords_any": ["sole responsibility", "eDiets"],
    "keywords_all": [],
    "heading_hint": "1.3",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q14",
    "question": "What clause restricts public statements or press releases about the existence/terms of the agreement?",
    "keywords_any": ["public statement", "press release", "prior written consent"],
    "keywords_all": [],
    "heading_hint": "4.",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q15",
    "question": "What does the privacy clause require regarding consumer data collected from Women.com users?",
    "keywords_any": ["Women.com Data", "privacy", "security policies"],
    "keywords_all": [],
    "heading_hint": "8.4",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q16",
    "question": "Which sections survive termination according to the Survival clause?",
    "keywords_any": ["will survive", "Sections 4, 8, 10, 11, 12, 13, 14 and"],
    "keywords_all": [],
    "heading_hint": "10.4",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q17",
    "question": "What cure period is given for a material breach before termination is allowed?",
    "keywords_any": ["thirty (30) days", "material breach"],
    "keywords_all": [],
    "heading_hint": "10.2",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q18",
    "question": "In confidentiality obligations, to whom may confidential information be disclosed (need-to-know restriction)?",
    "keywords_any": ["employees, agents and contractors", "need to know"],
    "keywords_all": [],
    "heading_hint": "11.4",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q19",
    "question": "What is included in the definition of a filled application form (what action completes it)?",
    "keywords_any": ["FILLED APPLICATION FORM", "Submit"],
    "keywords_all": [],
    "heading_hint": "FILLED APPLICATION FORM",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q20",
    "question": "What website URL is explicitly defined as the EBIX SITE?",
    "keywords_any": ["HTTP://WWW.EBIX.COM", "EBIX SITE"],
    "keywords_all": [],
    "heading_hint": "EBIX SITE",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q21",
    "question": "What are About Guide Site Sub-Pages (definition asks for what pages are included/excluded)?",
    "keywords_any": ["About Guide Site Sub-Pages", "Web pages"],
    "keywords_all": [],
    "heading_hint": "About Guide Site Sub-Pages",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q22",
    "question": "What is the maximum scheduled downtime allowed per month for maintenance (in hours)?",
    "keywords_any": ["one (1) hour", "month period"],
    "keywords_all": [],
    "heading_hint": "13.4",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q23",
    "question": "After how many business days of non-payment can termination be triggered (per the termination section)?",
    "keywords_any": ["twenty (20)", "business days"],
    "keywords_all": [],
    "heading_hint": "13.2",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q24",
    "question": "What does the assignment clause say about consent not being unreasonably withheld or delayed?",
    "keywords_any": ["consent shall not be unreasonably withheld", "assign"],
    "keywords_all": [],
    "heading_hint": "15.6",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q25",
    "question": "Where is a 'LIMITATION OF LIABILITY' section found and what does it generally address?",
    "keywords_any": ["LIMITATION OF LI", "LIMITATION OF LIABILITY", "Except as provided"],
    "keywords_all": [],
    "heading_hint": "LIMITATION",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q26",
    "question": "Where is a 'DISCLAIMER OF WARRANTIES' section found (look for 'DISCLAIMER OF WA')?",
    "keywords_any": ["DISCLAIMER OF WA", "warranties"],
    "keywords_all": [],
    "heading_hint": "DISCLAIMER",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q27",
    "question": "What does the Ownership section say about eDiets Content ownership (retains rights/copyright)?",
    "keywords_any": ["retain all rights", "eDiets Content", "copyright"],
    "keywords_all": [],
    "heading_hint": "8.1",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q28",
    "question": "What restriction exists on promoting or distributing advertising for a 'Women.com Competitive Company' near the gateway page?",
    "keywords_any": ["Women.com Competitive Company", "will not buy, sell, display"],
    "keywords_all": [],
    "heading_hint": "5.2",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q29",
    "question": "How are media metrics allocated for the Gateway Page (pageviews/impressions allocation)?",
    "keywords_any": ["media metrics", "allocated to Women.com"],
    "keywords_all": [],
    "heading_hint": "3.2",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q30",
    "question": "What is the 'Limited Warranty' article called (look for 'ARTICLE VII' and 'Limited Warranty')?",
    "keywords_any": ["ARTICLE VII", "Limited Warranty"],
    "keywords_all": [],
    "heading_hint": "ARTICLE VII",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q31",
    "question": "TARGETED DEBUG: In oneNDA.docx, who can the Receiver share confidential information with?",
    "keywords_any": ["Permitted Receivers", "share the Confidential Information"],
    "keywords_all": [],
    "heading_hint": "PARTIES AND EXECUTION",
    "k": 6,
    "filters": {"doc_type": "docx"},
    "targeted_debug": true
  },
  {
    "id": "Q32",
    "question": "TARGETED DEBUG: In oneNDA.docx, how long do obligations last?",
    "keywords_any": ["How long do my obligations last", "duty to protect"],
    "keywords_all": [],
    "heading_hint": "PARTIES AND EXECUTION",
    "k": 6,
    "filters": {"doc_type": "docx"},
    "targeted_debug": true
  },
  {
    "id": "Q33",
    "question": "TARGETED DEBUG: In oneNDA.docx, where is the definition of Confidential Information presented?",
    "keywords_any": ["What is Confidential Information", "Confidential Information"],
    "keywords_all": [],
    "heading_hint": "TERMS",
    "k": 6,
    "filters": {"doc_type": "docx"},
    "targeted_debug": true
  },
  {
    "id": "Q34",
    "question": "TARGETED DEBUG: In cuad_013.pdf, what section heading is '14. LIMITATION OF LIABILITY'?",
    "keywords_any": ["14. LIMITATION OF LIABILITY", "LIMITATION OF LIABILITY"],
    "keywords_all": [],
    "heading_hint": "14.",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": true
  },
  {
    "id": "Q35",
    "question": "TARGETED DEBUG: In cuad_014.pdf, which section states confidentiality info is disclosed only to employees/agents/contractors with a need to know?",
    "keywords_any": ["employees, agents and contractors", "need to know"],
    "keywords_all": [],
    "heading_hint": "11.4",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": true
  },
  {
    "id": "Q36",
    "question": "TARGETED DEBUG: In cuad_013.pdf, what does 'FILLED APPLICATION FORM' definition say about clicking Submit?",
    "keywords_any": ["FILLED APPLICATION FORM", "Submit"],
    "keywords_all": [],
    "heading_hint": "FILLED APPLICATION FORM",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": true
  },
  {
    "id": "Q37",
    "question": "What is the term 'Confidential Information' used to describe in a confidentiality section (look for explicit definition)?",
    "keywords_any": ["\"Confidential Information\" means", "Confidential Information means"],
    "keywords_all": [],
    "heading_hint": "CONFIDENTIALITY",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q38",
    "question": "What does a termination clause say about terminating for breach if not cured within a stated number of days?",
    "keywords_any": ["terminate", "not cured within thirty (30) days"],
    "keywords_all": [],
    "heading_hint": "Termination",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q39",
    "question": "What does an indemnity clause typically require (look for 'indemnify' + 'attorneys' fees')?",
    "keywords_any": ["indemnify", "attorneys' fees", "hold harmless"],
    "keywords_all": [],
    "heading_hint": "INDEMN",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  },
  {
    "id": "Q40",
    "question": "What does a confidentiality clause say about disclosure to third parties (look for 'will not disclose to any third party')?",
    "keywords_any": ["will not disclose", "third party"],
    "keywords_all": [],
    "heading_hint": "Confidential",
    "k": 6,
    "filters": {"doc_type": "pdf"},
    "targeted_debug": false
  }
]
```
