import os
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

client = TextAnalyticsClient(
    endpoint=os.environ["LANGUAGE_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["LANGUAGE_KEY"])
)

def analyze_sentiment(text):
    result = client.analyze_sentiment([text])[0]
    return {
        "sentiment": result.sentiment,
        "positive_score": round(result.confidence_scores.positive, 3),
        "neutral_score": round(result.confidence_scores.neutral, 3),
        "negative_score": round(result.confidence_scores.negative, 3)
    }

def extract_key_phrases(text):
    result = client.extract_key_phrases([text])[0]
    return result.key_phrases

def detect_pii(text):
    result = client.recognize_pii_entities([text])[0]
    entities = [{"text": e.text, "category": e.category} for e in result.entities]
    redacted = result.redacted_text
    return {"entities": entities, "redacted_text": redacted}

if __name__ == "__main__":
    test_transcripts = [
        "I'm feeling great today, went for a walk and talked to my daughter Susan Thompson.",
        "I don't know, I feel a bit lost and confused about what's happening today.",
        "Fine I guess. My phone number is 555-123-4567 if you need to reach my doctor."
    ]

    for text in test_transcripts:
        print(f"\n--- Transcript: '{text}' ---")
        print("Sentiment:", analyze_sentiment(text))
        print("Key phrases:", extract_key_phrases(text))
        print("PII check:", detect_pii(text))

def extract_entities(text):
    result = client.recognize_entities([text])[0]
    return [{"text": e.text, "category": e.category, "confidence": round(e.confidence_score, 2)} for e in result.entities]
