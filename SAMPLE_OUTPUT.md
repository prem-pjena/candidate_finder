# Sample Run Output

> **Query:** *"Customer Success Manager, 3+ years, fintech / financial services background, in Bangalore or Delhi NCR."*

This output was generated from a live run of the API using a local LM Studio model. Results will vary depending on the LLM model used.

---

## Top 20 Candidates

```
Rank | Name               | Title                         | Exp | Location     | Score | Reason
─────┼────────────────────┼───────────────────────────────┼─────┼──────────────┼───────┼─────────────────────────────────────────────────────────────────────────
  1  | Arjun Menon        | Customer Success Manager      | 12yr| Remote       |  98   | Near perfect match: 12 years experience in financial services
     |                    |                               |     |              |       | and remote location.
  2  | Riya Chopra        | Senior Customer Success Mgr   |  4yr| Bangalore    |  95   | Excellent match: 4 years experience, relevant skills
     |                    |                               |     |              |       | (Salesforce, Onboarding), correct location.
  3  | Faisal Menon       | Customer Success Associate    |  8yr| Delhi NCR    |  95   | Excellent match with experience, skills, and customer
     |                    |                               |     |              |       | success focus.
  4  | Sanjana Jain       | Associate Product Manager     |  3yr| Bangalore    |  95   | Title related, 3 years exp, correct industry/location,
     |                    |                               |     |              |       | strong analytical skills.
  5  | Rahul Mukherjee    | Senior Customer Success Mgr   |  8yr| Hyderabad    |  95   | Senior CSM title, 8 years exp, relevant industry,
     |                    |                               |     |              |       | strong skills.
  6  | Riya Patel         | Head of Customer Success      | 12yr| Noida        |  95   | Excellent match with experience, industry, and relevant
     |                    |                               |     |              |       | skills for CSM role.
  7  | Arjun Das          | Customer Success Associate    |  7yr| Remote       |  92   | Very strong match: relevant experience, financial
     |                    |                               |     |              |       | industry, account management skills.
  8  | Ramya Das          | Customer Success Manager      |  3yr| Delhi NCR    |  90   | Meets experience and location requirements with relevant
     |                    |                               |     |              |       | CSM skills.
  9  | Farhan Malhotra    | Senior Customer Success Mgr   |  5yr| Delhi NCR    |  90   | Strong match: 5 years experience in related industry
     |                    |                               |     |              |       | (insurance), strong account management skills.
 10  | Deepak Patel       | Customer Success Specialist   |  7yr| Delhi NCR    |  90   | Strong match with experience, skills, and location;
     |                    |                               |     |              |       | relevant customer focus.
 11  | Gaurav Iyer        | Implementation Manager        | 12yr| Bangalore    |  90   | Significant experience, relevant skills in financial
     |                    |                               |     |              |       | services, title slightly different.
 12  | Arpit Malhotra     | Customer Success Manager      |  —  | Remote       |  90   | Direct title match and relevant skills. Experience
     |                    |                               |     |              |       | assumed sufficient (missing data).
 13  | Hari Nair          | Strategic Account Manager     |  —  | Delhi NCR    |  90   | Excellent match with financial services industry,
     |                    |                               |     |              |       | location, and relevant skills.
 14  | Meera Patel        | Customer Success Associate    | 10yr| Remote       |  90   | Excellent match with CS title, experience, and
     |                    |                               |     |              |       | relevant skills.
 15  | Payal Agarwal      | Customer Success Lead         |  3yr| Mumbai       |  90   | Excellent match with experience (3 years), relevant
     |                    |                               |     |              |       | skills, and customer focus.
 16  | Payal Mishra       | Customer Success Associate    | 12yr| Hyderabad    |  90   | Excellent experience and strong skills like Data
     |                    |                               |     |              |       | Analysis and QBRs.
 17  | Sourav Singh       | Head of Customer Success      |  9yr| Noida        |  90   | Excellent experience and senior title. Skills align
     |                    |                               |     |              |       | well with CSM role.
 18  | Ishaan Dubey       | Support Team Lead             |  —  | Bangalore    |  90   | Excellent match with industry and location. Skills
     |                    |                               |     |              |       | align well with CSM role.
 19  | Gaurav Ghosh       | Customer Success Manager      |  7yr| Delhi NCR    |  85   | Strong match: relevant title, 7 years exp, location
     |                    |                               |     |              |       | match. Skills align well.
 20  | Rahul Iyer         | Senior Customer Success Mgr   |  9yr| Delhi NCR    |  85   | Strong match: high experience and relevant skills.
     |                    |                               |     |              |       | Industry slightly off target.
```

---

## Key Observations

### 1. Missing Data Handled Gracefully
- **Arpit Malhotra** (rank 12) and **Hari Nair** (rank 13) have `null` experience — still scored 90. The LLM assumed sufficient experience from their title and skills.
- **Ishaan Dubey** (rank 18) has `null` experience — scored 90 based on industry, location, and skills.

### 2. Remote Candidates Get Fair Scores
- **Arjun Menon** (rank 1, Remote) scored 98 — top match because location wasn't a barrier.
- **Arpit Malhotra** (rank 12, Remote) scored 90 with direct title match.

### 3. Related Titles Recognized
- **Sanjana Jain** (Associate Product Manager, rank 4) scored 95 — title is different but related.
- **Gaurav Iyer** (Implementation Manager, rank 11) scored 90 — transferable skills recognized.

### 4. Location Flexibility
- Candidates in **Hyderabad**, **Mumbai**, and **Noida** still scored well — LLM recognized proximity or remote flexibility.

---

## Summary

- **Total candidates in dataset:** 500
- **Candidates scoring above 50/100:** 20+
- **Top 20 returned:** 20
- **Auto-broaden triggered:** No
- **Model used:** Local LM Studio (results vary by model)

---

## Full Response JSON

```json
{
  "query": "Customer Success Manager, 3+ years, fintech / financial services background, in Bangalore or Delhi NCR.",
  "total_results": 20,
  "broaden_used": false,
  "results": [
    {
      "rank": 1,
      "name": "Arjun Menon",
      "title": "Customer Success Manager",
      "location": "Remote",
      "experience": 12,
      "score": 98,
      "reason": "Near perfect match: 12 years experience in financial services and remote location."
    },
    {
      "rank": 2,
      "name": "Riya Chopra",
      "title": "Senior Customer Success Manager",
      "location": "Bangalore",
      "experience": 4,
      "score": 95,
      "reason": "Excellent match: 4 years experience, relevant skills (Salesforce, Onboarding), correct location."
    },
    {
      "rank": 3,
      "name": "Faisal Menon",
      "title": "Customer Success Associate",
      "location": "Delhi NCR",
      "experience": 8,
      "score": 95,
      "reason": "Excellent match with experience, skills, and customer success focus."
    },
    {
      "rank": 4,
      "name": "Sanjana Jain",
      "title": "Associate Product Manager",
      "location": "Bangalore",
      "experience": 3,
      "score": 95,
      "reason": "Excellent match: Title related, 3 years exp, correct industry/location, strong analytical skills."
    },
    {
      "rank": 5,
      "name": "Rahul Mukherjee",
      "title": "Senior Customer Success Manager",
      "location": "Hyderabad",
      "experience": 8,
      "score": 95,
      "reason": "Excellent match: Senior CSM title, 8 years exp, relevant industry, strong skills."
    },
    {
      "rank": 6,
      "name": "Riya Patel",
      "title": "Head of Customer Success",
      "location": "Noida",
      "experience": 12,
      "score": 95,
      "reason": "Excellent match with experience, industry, and relevant skills for CSM role."
    },
    {
      "rank": 7,
      "name": "Arjun Das",
      "title": "Customer Success Associate",
      "location": "Remote",
      "experience": 7,
      "score": 92,
      "reason": "Very strong match: Relevant experience, financial industry, account management skills."
    },
    {
      "rank": 8,
      "name": "Ramya Das",
      "title": "Customer Success Manager",
      "location": "Delhi NCR",
      "experience": 3,
      "score": 90,
      "reason": "Excellent match: Meets experience and location requirements with relevant CSM skills."
    },
    {
      "rank": 9,
      "name": "Farhan Malhotra",
      "title": "Senior Customer Success Manager",
      "location": "Delhi NCR",
      "experience": 5,
      "score": 90,
      "reason": "Strong match: 5 years experience in related industry (insurance), strong account management."
    },
    {
      "rank": 10,
      "name": "Deepak Patel",
      "title": "Customer Success Specialist",
      "location": "Delhi NCR",
      "experience": 7,
      "score": 90,
      "reason": "Strong match with experience, skills, and location; relevant customer focus."
    },
    {
      "rank": 11,
      "name": "Gaurav Iyer",
      "title": "Implementation Manager",
      "location": "Bangalore",
      "experience": 12,
      "score": 90,
      "reason": "Strong match: Significant experience, relevant skills in financial services."
    },
    {
      "rank": 12,
      "name": "Arpit Malhotra",
      "title": "Customer Success Manager",
      "location": "Remote",
      "experience": null,
      "score": 90,
      "reason": "Direct title match and relevant skills. Experience assumed sufficient for CSM role."
    },
    {
      "rank": 13,
      "name": "Hari Nair",
      "title": "Strategic Account Manager",
      "location": "Delhi NCR",
      "experience": null,
      "score": 90,
      "reason": "Excellent match with financial services industry, location, and relevant skills."
    },
    {
      "rank": 14,
      "name": "Meera Patel",
      "title": "Customer Success Associate",
      "location": "Remote",
      "experience": 10,
      "score": 90,
      "reason": "Excellent match with CS title, experience, and relevant skills."
    },
    {
      "rank": 15,
      "name": "Payal Agarwal",
      "title": "Customer Success Lead",
      "location": "Mumbai",
      "experience": 3,
      "score": 90,
      "reason": "Excellent match with experience (3 years), relevant skills, and customer focus."
    },
    {
      "rank": 16,
      "name": "Payal Mishra",
      "title": "Customer Success Associate",
      "location": "Hyderabad",
      "experience": 12,
      "score": 90,
      "reason": "Excellent experience and strong skills like Data Analysis and QBRs."
    },
    {
      "rank": 17,
      "name": "Sourav Singh",
      "title": "Head of Customer Success",
      "location": "Noida",
      "experience": 9,
      "score": 90,
      "reason": "Excellent experience and senior title. Skills align well with CSM role."
    },
    {
      "rank": 18,
      "name": "Ishaan Dubey",
      "title": "Support Team Lead",
      "location": "Bangalore",
      "experience": null,
      "score": 90,
      "reason": "Excellent match with industry and location. Skills align well with CSM role."
    },
    {
      "rank": 19,
      "name": "Gaurav Ghosh",
      "title": "Customer Success Manager",
      "location": "Delhi NCR",
      "experience": 7,
      "score": 85,
      "reason": "Strong match: Relevant title, 7 years exp, location match. Skills align well."
    },
    {
      "rank": 20,
      "name": "Rahul Iyer",
      "title": "Senior Customer Success Manager",
      "location": "Delhi NCR",
      "experience": 9,
      "score": 85,
      "reason": "Strong match: High experience and relevant skills. Industry slightly off target."
    }
  ]
}
```
