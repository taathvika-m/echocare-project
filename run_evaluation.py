import json
from golden_test_set import TEST_SCENARIOS
from pattern_analysis_agent import summarize_period, analyze_pattern_change
from escalation_agent import escalate_with_hard_gate

def run_scenario(scenario):
    baseline_summary = summarize_period(scenario["baseline"])
    recent_summary = summarize_period(scenario["recent"])

    # Add person_name since escalation_agent expects it
    recent_with_name = [{**c, "person_name": "TestPerson"} for c in scenario["recent"]]

    pattern_result = analyze_pattern_change(baseline_summary, recent_summary, recent_with_name)
    decision = escalate_with_hard_gate(pattern_result, recent_with_name)

    actual = decision.get("recommend_escalation", False)
    expected = scenario["expected_escalation"]
    correct = (actual == expected)

    return {
        "scenario": scenario["name"],
        "expected": expected,
        "actual": actual,
        "correct": correct,
        "reasoning": pattern_result.get("reasoning", ""),
        "evidence": pattern_result.get("specific_evidence", [])
    }

if __name__ == "__main__":
    results = []
    print(f"Running evaluation on {len(TEST_SCENARIOS)} scenarios...\n")

    for scenario in TEST_SCENARIOS:
        print(f"Running: {scenario['name']}...")
        result = run_scenario(scenario)
        results.append(result)
        status = "✓ PASS" if result["correct"] else "✗ FAIL"
        print(f"  {status} - expected: {result['expected']}, actual: {result['actual']}")

    print("\n" + "="*50)
    correct_count = sum(r["correct"] for r in results)
    total = len(results)
    accuracy = correct_count / total * 100

    print(f"RESULTS: {correct_count}/{total} correct ({accuracy:.1f}% accuracy)")
    print("="*50)

    failures = [r for r in results if not r["correct"]]
    if failures:
        print("\nFAILED SCENARIOS (investigate these):")
        for f in failures:
            print(f"\n- {f['scenario']}")
            print(f"  Expected: {f['expected']}, Got: {f['actual']}")
            print(f"  Model's reasoning: {f['reasoning']}")

    with open("evaluation_results.json", "w") as f:
        json.dump({"accuracy_pct": accuracy, "results": results}, f, indent=2)
    print(f"\nFull results saved to evaluation_results.json")

# Tracing note: escalation_log.jsonl (written by escalate_with_hard_gate) now contains
# a full audit trail of every decision made during this evaluation run - timestamp,
# the pattern analysis inputs, and the final decision. This is your "tracing" deliverable:
# you can open that file and reconstruct exactly why any given decision was made.
