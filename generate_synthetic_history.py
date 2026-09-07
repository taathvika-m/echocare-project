import json
from datetime import datetime, timedelta

# Week 1-2: stable baseline
baseline_checkins = [
    {"mood_summary": "Feeling good, went for a short walk", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "A bit tired but otherwise fine", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Good day, talked to daughter on phone", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Feeling fine, watched some TV", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Great day, gardened a little", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Okay, quiet day", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Feeling good, slept well", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Fine, a little achy", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Good, had breakfast with neighbor", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Feeling okay", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Good day overall", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Fine, watched a movie", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "A little tired but happy", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "Good, called her sister", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
]

# Week 3: gradual, realistic decline pattern
decline_checkins = [
    {"mood_summary": "Fine, but couldn't remember what day it was at first", "took_medication": True, "date_orientation_correct": False, "notable_quotes": [], "immediate_concern": False},
    {"mood_summary": "A little confused about the morning routine", "took_medication": True, "date_orientation_correct": True, "notable_quotes": ["I keep forgetting little things"], "immediate_concern": False},
    {"mood_summary": "Unsure if she took her pills, had to check twice", "took_medication": True, "date_orientation_correct": False, "notable_quotes": ["I'm not sure what day it is anymore"], "immediate_concern": False},
    {"mood_summary": "Repeated the same story about her garden from two days ago, word for word", "took_medication": True, "date_orientation_correct": False, "notable_quotes": ["Did I already tell you about the garden?"], "immediate_concern": False},
    {"mood_summary": "Seemed disoriented, asked what year it was", "took_medication": False, "date_orientation_correct": False, "notable_quotes": ["I don't remember taking my pills today"], "immediate_concern": False},
    {"mood_summary": "Forgot the check-in had already happened once today", "took_medication": True, "date_orientation_correct": False, "notable_quotes": ["Have we talked already today?"], "immediate_concern": False},
    {"mood_summary": "Very confused, repeated three different stories in one call", "took_medication": False, "date_orientation_correct": False, "notable_quotes": ["I don't know what's happening today", "I feel lost"], "immediate_concern": True},
]

with open("checkins.jsonl", "w") as f:  # overwrite for a clean synthetic test set
    start_date = datetime.now() - timedelta(days=21)
    all_checkins = baseline_checkins + decline_checkins
    for i, checkin in enumerate(all_checkins):
        record = {
            "date": (start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "person_name": "Margaret",
            **checkin,
            "immediate_concern_detail": checkin["notable_quotes"][0] if checkin.get("immediate_concern") else None
        }
        f.write(json.dumps(record) + "\n")

print(f"Generated {len(baseline_checkins) + len(decline_checkins)} synthetic check-ins into checkins.jsonl")
