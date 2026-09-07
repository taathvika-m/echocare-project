"""
Golden test set: each scenario has a set of synthetic recent check-ins and the
CORRECT expected escalation decision, decided by human judgment (yours) in advance.
This is what your evaluation script will check the pipeline's actual output against.
"""

TEST_SCENARIOS = [
    {
        "name": "clear_decline_pattern",
        "expected_escalation": True,
        "baseline": [
            {"mood_summary": "Good day", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False}
        ] * 14,
        "recent": [
            {"mood_summary": "Confused about the day", "took_medication": True, "date_orientation_correct": False, "notable_quotes": ["I keep forgetting things"], "immediate_concern": False},
            {"mood_summary": "Repeated a story from yesterday", "took_medication": False, "date_orientation_correct": False, "notable_quotes": ["Did I already tell you this?"], "immediate_concern": False},
            {"mood_summary": "Very disoriented", "took_medication": False, "date_orientation_correct": False, "notable_quotes": ["I don't know what's happening", "I feel lost"], "immediate_concern": True},
        ]
    },
    {
        "name": "single_bad_day_should_NOT_escalate",
        "expected_escalation": False,
        "baseline": [
            {"mood_summary": "Good day", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False}
        ] * 14,
        "recent": [
            {"mood_summary": "Great day, feeling good", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
            {"mood_summary": "Tired, forgot the day once but otherwise fine", "took_medication": True, "date_orientation_correct": False, "notable_quotes": [], "immediate_concern": False},
            {"mood_summary": "Back to normal, good day", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
        ]
    },
    {
        "name": "always_forgetful_baseline_should_NOT_escalate",
        "expected_escalation": False,
        # This person has ALWAYS had imperfect date orientation - it's their normal, not a change
        "baseline": [
            {"mood_summary": "Fine, wasn't sure of the date", "took_medication": True, "date_orientation_correct": False, "notable_quotes": [], "immediate_concern": False}
        ] * 14,
        "recent": [
            {"mood_summary": "Fine, wasn't sure of the date again", "took_medication": True, "date_orientation_correct": False, "notable_quotes": [], "immediate_concern": False},
            {"mood_summary": "Good day", "took_medication": True, "date_orientation_correct": False, "notable_quotes": [], "immediate_concern": False},
            {"mood_summary": "Feeling fine", "took_medication": True, "date_orientation_correct": False, "notable_quotes": [], "immediate_concern": False},
        ]
    },
    {
        "name": "single_immediate_symptom_should_escalate_regardless_of_trend",
        "expected_escalation": True,
        "baseline": [
            {"mood_summary": "Good day", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False}
        ] * 14,
        "recent": [
            {"mood_summary": "Feeling fine overall", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
            {"mood_summary": "Feeling fine", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
            # Trend looks totally normal, BUT a real symptom was reported once - should still escalate
            {"mood_summary": "Had a sudden severe headache and felt dizzy, said it was the worst headache of her life", "took_medication": True, "date_orientation_correct": True, "notable_quotes": ["worst headache of my life"], "immediate_concern": True},
        ]
    },
    {
        "name": "stable_and_healthy_should_NOT_escalate",
        "expected_escalation": False,
        "baseline": [
            {"mood_summary": "Good day", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False}
        ] * 14,
        "recent": [
            {"mood_summary": "Great day", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
            {"mood_summary": "Feeling wonderful, went to the park", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
            {"mood_summary": "Good, quiet day", "took_medication": True, "date_orientation_correct": True, "notable_quotes": [], "immediate_concern": False},
        ]
    },
]
