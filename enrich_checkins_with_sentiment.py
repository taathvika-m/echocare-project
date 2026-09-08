import json
from text_analysis import analyze_sentiment

def enrich_checkins():
    enriched = []
    with open("checkins.jsonl") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            transcript = record.get("mood_summary", "")
            if transcript:
                sentiment = analyze_sentiment(transcript)
                record["sentiment_negative_score"] = sentiment["negative_score"]
                record["sentiment_label"] = sentiment["sentiment"]
            enriched.append(record)

    with open("checkins_enriched.jsonl", "w") as f:
        for record in enriched:
            f.write(json.dumps(record) + "\n")

    print(f"Enriched {len(enriched)} check-ins with sentiment scores -> checkins_enriched.jsonl")

if __name__ == "__main__":
    enrich_checkins()
