"""Simple reproducible evaluation; checks reference text and source attribution."""
import json
from pathlib import Path
from backend import run_rag_agent

def main():
    tests = json.loads((Path(__file__).parent / "testset.json").read_text(encoding="utf-8"))
    passed = 0
    for i, test in enumerate(tests, 1):
        result = run_rag_agent(test["question"])
        answer = result["answer"].lower()
        expected = test["expected_answer"].lower()
        # A lightweight baseline, not a substitute for expert grading or RAGAS.
        answer_match = expected in answer
        source_match = not test["expected_source"] or any(test["expected_source"] in s["source"] for s in result["sources"])
        ok = answer_match and source_match
        passed += ok
        print(f"{i}. {'PASS' if ok else 'FAIL'} | {test['question']}")
        print(f"   Answer: {result['answer'][:250]}")
    print(f"\nBaseline exact-substring score: {passed}/{len(tests)}")

if __name__ == "__main__":
    main()
