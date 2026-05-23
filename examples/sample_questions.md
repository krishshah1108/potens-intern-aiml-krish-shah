# Sample Questions for Manual Testing

Corpus: **10 English policy PDFs** (~10–15 pages each). Ask in **English, Hindi, or Marathi**; answers return in the query language.

Run evaluation:
- `python -m app.evaluation.run_eval` — retrieval/chunking metrics only (fast, no API quota)
- `python -m app.evaluation.run_eval --full` — includes Gemini answers (~13s delay; free tier ~5/min)

---

## English — factual Q&A

| Question | Expected document |
|----------|-----------------|
| What is the maximum retention for client contract records in the data privacy policy? | `data_privacy_policy.pdf` |
| How many paid annual leave days under the leave policy? | `leave_policy.pdf` |
| How many annual leave days does the HR handbook summarize? | `hr_handbook_excerpt.pdf` |
| How many remote days per week in the remote work policy? | `remote_work_policy.pdf` |
| What is the maximum remote allowance in the workplace attendance policy? | `workplace_attendance_policy.pdf` |
| How often must passwords rotate in the information security policy? | `information_security_policy.pdf` |
| How often must passwords change in the IT access policy? | `it_access_policy.pdf` |

---

## Hindi — cross-lingual retrieval (English PDFs)

| Question | Expected document |
|----------|-----------------|
| कर्मचारियों को आपातकालीन संपर्क विवरण कब तक अपडेट करना होता है? | `employee_compliance_notice.pdf` |
| प्रति वर्ष कितने दिन बीमारी की छुट्टी मिलती है? | `leave_policy.pdf` |
| सुरक्षा घटनाओं की रिपोर्ट DPO को कितने घंटों में करनी होती है? | `data_privacy_policy.pdf` |

---

## Marathi — cross-lingual retrieval

| Question | Expected document |
|----------|-----------------|
| आपत्कालीन संपर्क तपशील अपडेट करण्याची अंतिम तारीख काय आहे? | `employee_compliance_notice.pdf` |
| रिमोट कामासाठी VPN आणि कंपनी डिव्हाइस कोणत्या धोरणात आवश्यक आहे? | `remote_work_policy.pdf` |

---

## Should refuse (no grounding)

- What is the CEO's favorite programming language?
- What is Potens stock price forecast for 2030?

---

## Contradiction analysis (Streamlit tab)

| Document 1 | Document 2 | Topic |
|------------|------------|-------|
| `leave_policy.pdf` | `hr_handbook_excerpt.pdf` | annual leave entitlement |
| `remote_work_policy.pdf` | `workplace_attendance_policy.pdf` | remote work days per week |
| `information_security_policy.pdf` | `it_access_policy.pdf` | password rotation period |
| `data_privacy_policy.pdf` | `records_management_policy.pdf` | client contract retention |

---

## What to check in retrieval debug

- Top chunks include the expected `source_file`
- Similarity scores above threshold (~0.45) for answerable questions
- Chunk previews show the fact used in the answer
- Citations list source, page, and chunk ID
