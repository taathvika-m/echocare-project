import json
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")
client = AzureOpenAI(
    azure_endpoint="https://oai-echocare-b9328.openai.azure.com/",
    azure_ad_token=token.token,
    api_version="2024-10-21",
)

def load_checkins():
    import os
    filepath = "checkins_enriched.jsonl" if os.path.exists("checkins_enriched.jsonl") else "checkins.jsonl"
    with open(filepath) as f:
        return [json.loads(line) for line in f if line.strip()]

def split_baseline_and_recent(checkins, baseline_days=14, recent_days=7):
    """First N days = baseline (what 'normal' looks like for THIS person).
    Last M days = the period we're analyzing for change."""
    return checkins[:baseline_days], checkins[-recent_days:]

def summarize_period(checkins):
    total = len(checkins)
    if total == 0:
        return {}
    sentiment_scores = [c.get("sentiment_negative_score", 0) for c in checkins if "sentiment_negative_score" in c]
    return {
        "total_checkins": total,
        "pct_correct_date_orientation": sum(c["date_orientation_correct"] for c in checkins) / total * 100,
        "pct_medication_confirmed": sum(c["took_medication"] for c in checkins) / total * 100,
        "count_immediate_concerns": sum(c.get("immediate_concern", False) for c in checkins),
        "count_notable_quotes": sum(len(c.get("notable_quotes", [])) for c in checkins),
        "avg_negative_sentiment_score": round(sum(sentiment_scores) / len(sentiment_scores), 3) if sentiment_scores else None,
        "sample_moods": [c["mood_summary"] for c in checkins],
    }
    

def analyze_pattern_change(baseline_summary, recent_summary, recent_checkins):
    """This is where the model compares two summaries and produces a
    structured, EVIDENCE-CITED finding - never a vague 'something seems off'."""

    recent_quotes = []
    for c in recent_checkins:
        recent_quotes.extend(c.get("notable_quotes", []))

        prompt = f"""You are analyzing whether {recent_checkins[0]['person_name']}'s recent check-ins show a
MEANINGFUL CHANGE from their own established baseline. Do not compare to general population norms -
only compare to their own baseline below.

BASELINE (established pattern over 14 days):
{json.dumps(baseline_summary, indent=2)}

RECENT PERIOD (last 7 days):
{json.dumps(recent_summary, indent=2)}

RECENT NOTABLE QUOTES (verbatim, in order):
{json.dumps(recent_quotes, indent=2)}

IMPORTANT: this analysis includes BOTH your own qualitative reasoning about the structured fields AND
an independently-computed sentiment score (avg_negative_sentiment_score) from a separate NLP model.
If these two signals AGREE (both suggest decline, or both suggest stability), note that explicitly as
it strengthens confidence. If they DISAGREE, lower your confidence level and say so explicitly in your
reasoning - a disagreement between independent signals is itself meaningful information.

Respond in this exact JSON format:
{{
  "meaningful_change_detected": true or false,
  "confidence": "low", "medium", or "high",
  "signals_agree": true or false,
  "specific_evidence": ["exact data points or quotes that support your conclusion - be specific, cite numbers and quotes"],
  "reasoning": "brief explanation of why this is or isn't a meaningful pattern change from THIS person's baseline, explicitly noting whether the qualitative and quantitative signals agreed"
}}

Be conservative - a couple of off days is normal and should NOT be flagged as meaningful. Only flag a
genuine, evidenced trend, not isolated incidents."""

    response = client.chat.completions.create(
        model="gpt-4-1-deployment",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}  # forces valid JSON output
    )
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    checkins = load_checkins()
    baseline, recent = split_baseline_and_recent(checkins)

    baseline_summary = summarize_period(baseline)
    recent_summary = summarize_period(recent)

    print("=== BASELINE SUMMARY (first 14 days) ===")
    print(json.dumps(baseline_summary, indent=2))
    print("\n=== RECENT SUMMARY (last 7 days) ===")
    print(json.dumps(recent_summary, indent=2))

    print("\n=== ANALYZING PATTERN CHANGE ===")
    result = analyze_pattern_change(baseline_summary, recent_summary, recent)
    print(json.dumps(result, indent=2))
