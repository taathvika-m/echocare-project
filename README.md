# EchoCare

**An AI-powered daily check-in companion for elderly people living alone — built on Azure AI Foundry as a hands-on capstone for the Microsoft AI-103 certification.**

> ⚠️ **This is a research/portfolio prototype, not a validated medical device.** It does not diagnose any condition. All data used in development is synthetic.

---

## The Problem

Millions of elderly people live alone. Early signs of cognitive decline or medication issues often go unnoticed for months, because family can't call every day and doctors only see a snapshot every few months. Existing tools either offer one-time clinical voice screening or daily companionship with basic reminders — none combine **daily conversation**, **longitudinal pattern tracking against a person's own baseline**, and **evidence-gated alerting** designed explicitly to avoid false alarms.

EchoCare is built around one hard rule: **it must never alert a caregiver without being able to cite the specific evidence behind that decision.**

---

## What It Does

1. Holds a warm, natural daily voice-style check-in conversation
2. Confirms medication was taken — never guesses on ambiguous answers, always asks a follow-up
3. Catches and probes acute symptoms (headache, confusion, dizziness) that come up mid-conversation
4. Answers real questions about medications by retrieving the person's actual care plan — never invents an answer
5. Verifies photographed medication labels against the real prescription record via OCR
6. Tracks linguistic and sentiment patterns over time, comparing the person **against their own baseline** — not a population average
7. Recommends caregiver escalation only when backed by specific, citable evidence — enforced in code, not just prompted, and independently triggered by acute symptoms regardless of broader trend

---

## Architecture

| Component | What it does | Azure Service(s) |
|---|---|---|
| Check-in Agent | Multi-turn conversation, tool calling, concern detection | Azure OpenAI (GPT-4.1), function calling |
| RAG grounding | Answers medication questions from real care plan data | Azure AI Search (hybrid: keyword + vector) |
| Pattern Analysis Agent | Compares recent check-ins to the person's own 14-day baseline | Azure OpenAI + Azure AI Language (sentiment) |
| Escalation Agent | Decides whether to notify a caregiver, with a hard evidence gate | Azure OpenAI, code-enforced safety check |
| Medication Verification | OCR reads prescription labels, cross-checked against care plan | Azure AI Vision, Azure AI Document Intelligence |
| Infrastructure | Secured, reproducible deployment | Azure AI Foundry, Bicep (IaC), Managed Identity, GitHub Actions CI/CD |

**Design principle:** every escalation decision traces back to auditable evidence — either a direct quote from a transcript, a specific computed statistic (e.g., "date orientation dropped from 100% to 0%"), or an independently-computed sentiment score. Two independent signals agreeing is treated as stronger evidence than either alone.

---

## Evaluation

A golden test set of 5 deliberately varied scenarios was built to test the pipeline, including cases specifically designed to catch false positives:

- A clear, multi-day decline pattern (should escalate)
- A single bad day in an otherwise stable pattern (should NOT escalate)
- A person whose baseline has always included imperfect date orientation (should NOT escalate)
- A single acute symptom report with no broader trend (should escalate regardless of trend)
- A stable, healthy pattern (should NOT escalate)

**Result: 100% accuracy (5/5)** on this test set.

Full results and reasoning for every scenario are in `evaluation_results.json`. Every escalation decision made during evaluation is also logged with its full evidence trail in `escalation_log.jsonl`.

---

## Real Bugs Found and Fixed During Development

- **Retrieval failure causing a silent false negative:** early medication verification used `top_k=1` for RAG retrieval, which sometimes returned a topically-related but substantively empty chunk instead of the actual dosage information. Fixed by increasing to `top_k=3` and verified with a deliberate dosage-mismatch test.
- **Premature save on flagged concerns:** the Check-in Agent would sometimes save a check-in immediately after a vague response to a symptom follow-up. Fixed with a code-level gate (`concern_detail_is_adequate`) that rejects the tool call and forces a real follow-up.
- **Leaked API key caught by GitHub push protection:** an Azure Vision key was briefly hardcoded during debugging. GitHub blocked the push before it reached the repository. Remediated by rotating the key and migrating all credentials to environment variables.

---

## Responsible AI Notes

- **Content Safety** was tested with an adversarial prompt designed to elicit harmful medical misdirection; the model declined on its own.
- **The escalation safety gate is enforced in code**, not just prompted, and was tested directly with a fabricated "high confidence, no evidence" input to confirm it holds.
- **Computer vision is honestly scoped** — it confirms a photo was taken and cross-checks OCR-read label text, rather than claiming to identify pills by appearance.
- **Data policy** (`DATA_POLICY.md`) defines what is stored, retention limits, access boundaries, and deletion rights.

---

## Tech Stack

Azure AI Foundry, Azure OpenAI (GPT-4.1), Azure AI Search, Azure AI Vision, Azure AI Language, Azure AI Document Intelligence, Python, Bicep, GitHub Actions

---

## Setup

1. Clone the repo and create a virtual environment: python3 -m venv .venv && source .venv/bin/activate
2. Install dependencies: pip install -r requirements.txt
3. Deploy infrastructure: az deployment group create --resource-group rg-echocare --template-file infra/main.bicep
4. Copy .env.example to .env and fill in your resource endpoints/keys
5. Run a check-in: python3 checkin_agent.py
6. Run the evaluation suite: python3 run_evaluation.py

---

## Project Structure

infra/                        Bicep infrastructure-as-code
checkin_agent.py               Multi-turn Check-in Agent with RAG + safety guard
pattern_analysis_agent.py      Baseline comparison and trend detection
escalation_agent.py            Evidence-gated caregiver escalation decision
rag_utils.py                   Hand-built retrieval (Phase 2)
search_query.py                Production Azure AI Search hybrid retrieval (Phase 5)
vision_analysis.py             General image analysis
ocr_reader.py                  OCR label reading
verify_medication.py           OCR-to-care-plan cross-check
text_analysis.py               Sentiment, PII detection, entity recognition
document_intelligence.py       Structured invoice/document field extraction
golden_test_set.py             Evaluation scenarios
run_evaluation.py              Evaluation runner
DATA_POLICY.md                 Data handling policy

---

## What I'd Build Next

- Custom-trained Document Intelligence model for medication-specific field extraction
- Cross-checking entity recognition output against LLM tool-call extraction to catch extraction gaps
- Real notification delivery (SMS/email) instead of a logged, simulated alert
- A scheduled/serverless deployment so the Pattern Analysis Agent runs automatically on a weekly cadence
