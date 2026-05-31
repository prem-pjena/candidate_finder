# Sample Run Output

> **Query:** *"Customer Success Manager, 3+ years, fintech / financial services background, in Bangalore or Delhi NCR."*

This file shows the expected output format. Actual scores will vary depending on the LLM model used (local LM Studio models may produce different scores than what's shown here).

---

## Top 20 Candidates

```
Rank | Name               | Title                         | Exp | Location     | Score | Reason
─────┼────────────────────┼───────────────────────────────┼─────┼──────────────┼───────┼──────────────────────────────────────────────────────
  1  | Suresh Nair        | Customer Success Manager      | 4yr | Delhi NCR    |  92   | CSM title matches, financial services industry,
     |                    |                               |     |              |       | 4yr experience meets 3yr minimum, located in Delhi NCR
  2  | Priya Sharma       | Customer Success Manager      | 5yr | Bangalore    |  90   | CSM in fintech, 5yr exp exceeds requirements,
     |                    |                               |     |              |       | Bangalore location, relevant skills in CRM
  3  | Amit Kumar         | Customer Success Manager      | 6yr | Remote       |  85   | CSM with 6yr exp, insurance background,
     |                    |                               |     |              |       | Remote allows working in any location
  4  | Rahul Verma        | Senior Customer Success Mgr   | 8yr | Delhi NCR    |  82   | Senior CSM title, excellent experience,
     |                    |                               |     |              |       | software industry not fintech but transferable
  5  | Deepika Reddy      | Customer Success Lead         | 7yr | Gurgaon      |  78   | CS Lead title, 7yr exp, IT industry,
     |                    |                               |     |              |       | close to Delhi NCR, strong leadership skills
  6  | Ananya Gupta       | Customer Success Associate    | 2yr | Mumbai       |  65   | CS title but Associate level, fintech industry,
     |                    |                               |     |              |       | close to 3yr minimum, Mumbai not target city
  7  | Vikram Patel       | Account Manager               |  —  | Bangalore    |  60   | Account Management overlaps with CSM,
     |                    |                               |     |              |       | Bangalore location, missing experience data
  8  | Maya Joshi         | Technical Support Specialist  | 3yr | Bangalore    |  55   | Customer-facing role, 3yr exp, Bangalore,
     |                    |                               |     |              |       | but title not directly CSM-related
  9  | Neha Singh         | Customer Success Specialist   | 4yr | Delhi NCR    |  75   | CS title, 4yr exp, Delhi NCR location,
     |                    |                               |     |              |       | good communication skills
 10  | Raj Kapoor         | Customer Success Lead         | 7yr | Gurgaon      |  76   | CS Lead, 7yr exp, close to Delhi NCR,
     |                    |                               |     |              |       | strong analytics and planning skills
 11  | Kavita Reddy       | Customer Success Manager      | 3yr | Bangalore    |  88   | Exact title match, 3yr exp meets minimum,
     |                    |                               |     |              |       | financial services industry, Bangalore
 12  | Arun Patel         | Customer Success Manager      | 5yr | Delhi NCR    |  87   | CSM title, 5yr exp, Delhi NCR,
     |                    |                               |     |              |       | experience in client relationship management
 13  | Sneha Gupta        | Senior Customer Success Mgr   | 6yr | Bangalore    |  84   | Senior CSM, 6yr exp, Bangalore,
     |                    |                               |     |              |       | fintech background
 14  | Manish Kumar       | Customer Success Specialist   | 4yr | Delhi NCR    |  72   | CS title, 4yr exp, Delhi NCR,
     |                    |                               |     |              |       | some relevant skills but fintech experience missing
 15  | Pooja Sharma       | Account Manager               | 5yr | Bangalore    |  62   | Account management is CSM-adjacent,
     |                    |                               |     |              |       | 5yr exp, Bangalore, lacks fintech experience
 16  | Rohan Verma        | Customer Success Associate    | 3yr | Bangalore    |  68   | CS Associate, 3yr exp meets minimum,
     |                    |                               |     |              |       | Bangalore location, building CS skills
 17  | Ankit Singh        | Customer Success Manager      | 4yr | Remote       |  80   | CSM title, 4yr exp, Remote is flexible,
     |                    |                               |     |              |       | relevant customer onboarding skills
 18  | Divya Patel        | Customer Success Lead         | 8yr | Bangalore    |  83   | CS Lead, 8yr exp exceeds requirements,
     |                    |                               |     |              |       | Bangalore, strong leadership
 19  | Nikhil Joshi       | Customer Success Manager      | 3yr | Noida        |  70   | CSM title, 3yr exp, Noida near Delhi NCR,
     |                    |                               |     |              |       | industry not fintech
 20  | Ishita Nair        | Customer Success Specialist   | 5yr | Delhi NCR    |  74   | CS title, 5yr exp, Delhi NCR location,
     |                    |                               |     |              |       | good communication skills
```

---

## Summary

- **Total candidates in dataset:** 500
- **Candidates shortlisted by pre-filter:** 87
- **Candidates scoring above 50/100:** 32
- **Top 20 returned:** 20
- **Auto-broaden triggered:** No (32 good candidates found in initial search)

---

## Response JSON (Truncated)

```json
{
  "query": "Customer Success Manager, 3+ years, fintech / financial services background, in Bangalore or Delhi NCR.",
  "total_results": 20,
  "broaden_used": false,
  "results": [
    {
      "rank": 1,
      "name": "Suresh Nair",
      "title": "Customer Success Manager",
      "location": "Delhi NCR",
      "experience": 4,
      "score": 92,
      "reason": "CSM title matches, financial services industry, 4yr experience meets 3yr minimum, located in Delhi NCR"
    },
    {
      "rank": 2,
      "name": "Priya Sharma",
      "title": "Customer Success Manager",
      "location": "Bangalore",
      "experience": 5,
      "score": 90,
      "reason": "CSM in fintech, 5yr exp exceeds requirements, Bangalore location, relevant skills in CRM"
    }
  ]
}
```

> **Note:** This is a representative sample. Actual results will vary based on your specific LLM model and its scoring behavior.
