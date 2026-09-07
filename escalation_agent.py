import json
from datetime import datetime
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from pattern_analysis_agent import load_checkins, split_baseline_and_recent, summarize_period, analyze_pattern_change

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")
client = AzureOpenAI(
    azure_endpoint="https://oai-echocare-b9328.openai.azure.com/",
    azure_ad_token=token.token,
    api_version="2024-10-21",
)

EMERGENCY_CONTACT = {"name": "Susan Thompson", "relationship": "daughter", "phone": "(555) 123-4567"}

def decide_escalation(pattern_result, recent_checkins):
    immediate_concerns = [c for c in recent_checkins if c.get("immediate_concern")]

    prompt = f"""You are deciding whether to recommend contacting a family caregiver based on a
pattern analysis of an elderly person's daily check-ins.

PATTERN ANALYSIS RESULT:
{json.dumps(pattern_result, indent=2)}

IMMEDIATE CONCERNS FLAGGED DURING CHECK-INS (raw, not yet analyzed for trend):
{json.dumps(immediate_concerns, indent=2)}

Decide: should the family caregiver be notified? Consider:
- A single flagged pattern (even 'high confidence') from ONE analysis window may warrant a "monitor closely"
  recommendation rather than an immediate alert, unless there's also a direct immediate_concern (like a
  reported symptom) that independently warrants contact regardless of the trend.
- Never recommend escalation without being able to point to specific evidence.

Respond in this exact JSON format:
{{
  "recommend_escalation": true or false,
  "urgency": "monitor" or "notify_soon" or "notify_immediately",
  "message_to_family": "a warm, clear, non-alarming message explaining specifically what was observed and why - written for a worried family member to read, citing the actual evidence",
  "evidence_used": ["copy the specific evidence points this decision is actually based on"]
}}"""

    response = client.chat.completions.create(
        model="gpt-4-1-deployment",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def escalate_with_hard_gate(pattern_result, recent_checkins):
    decision = decide_escalation(pattern_result, recent_checkins)

    has_real_evidence = (
        len(decision.get("evidence_used", [])) > 0 and
        len(pattern_result.get("specific_evidence", [])) > 0
    )

    if decision.get("recommend_escalation") and not has_real_evidence:
        print("\n[SAFETY GATE TRIGGERED: escalation was recommended but evidence_used was empty "
              "or pattern_result had no specific_evidence. BLOCKING the alert.]")
        decision["recommend_escalation"] = False
        decision["urgency"] = "monitor"
        decision["message_to_family"] = None

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "decision": decision,
        "pattern_result": pattern_result
    }
    with open("escalation_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return decision

if __name__ == "__main__":
    checkins = load_checkins()
    baseline, recent = split_baseline_and_recent(checkins)
    baseline_summary = summarize_period(baseline)
    recent_summary = summarize_period(recent)

    print("Running pattern analysis...")
    pattern_result = analyze_pattern_change(baseline_summary, recent_summary, recent)

    print("\nRunning escalation decision...")
    decision = escalate_with_hard_gate(pattern_result, recent)

    print("\n=== ESCALATION DECISION ===")
    print(json.dumps(decision, indent=2))

    if decision.get("recommend_escalation"):
        print(f"\n📞 WOULD NOTIFY: {EMERGENCY_CONTACT['name']} ({EMERGENCY_CONTACT['relationship']}) "
              f"at {EMERGENCY_CONTACT['phone']}")
        print(f"Urgency: {decision['urgency']}")
        print(f"Message: {decision['message_to_family']}")
    else:
        print("\n✓ No escalation recommended at this time - continuing to monitor.")
