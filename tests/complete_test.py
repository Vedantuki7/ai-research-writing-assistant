"""
complete_test.py - Runs all test cases and saves evidence
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools import SourceCredibilityAnalyzer
from agents import ResearchWritingAgents

# Create directories
os.makedirs('evaluation_reports', exist_ok=True)
os.makedirs('test_evidence', exist_ok=True)

print("\n=== COMPLETE TEST SUITE WITH EVIDENCE ===\n")

# TEST 1: Custom Tool Accuracy
print("TEST 1: Custom Tool Accuracy")
print("-" * 40)
analyzer = SourceCredibilityAnalyzer()

test_results = []
urls = [
    ("https://www.nature.com/test", "high"),
    ("http://suspicious-site.com", "low"),
    ("https://stanford.edu/research", "high")
]

for url, expected in urls:
    result = analyzer._run(url)
    score = result.get('credibility_score', 0)
    test_results.append({
        "url": url,
        "expected": expected,
        "score": score,
        "passed": (score > 80 and expected == "high") or (score < 60 and expected == "low")
    })
    print(f"URL: {url}")
    print(f"Score: {score}, Expected: {expected}, Result: {'PASS' if test_results[-1]['passed'] else 'FAIL'}")

# Save evidence
with open('test_evidence/tool_accuracy_test.json', 'w') as f:
    json.dump(test_results, f, indent=2)
print("✓ Evidence saved to test_evidence/tool_accuracy_test.json\n")

# TEST 2: Agent Loading
print("TEST 2: Agent Loading Performance")
print("-" * 40)
start = time.time()
agents = ResearchWritingAgents()
agent_list = [
    "controller_agent",
    "research_specialist",
    "fact_checker",
    "content_strategist",
    "writing_specialist",
    "seo_specialist",
    "editor_agent"
]

loaded = []
for agent_name in agent_list:
    try:
        getattr(agents, agent_name)()
        loaded.append(agent_name)
        print(f"✓ {agent_name} loaded")
    except:
        print(f"✗ {agent_name} failed")

load_time = time.time() - start

# Save evidence
with open('test_evidence/agent_loading_test.json', 'w') as f:
    json.dump({
        "agents_loaded": loaded,
        "total": len(loaded),
        "load_time": f"{load_time:.2f}s"
    }, f, indent=2)
print(f"\n✓ All {len(loaded)} agents loaded in {load_time:.2f}s")
print("✓ Evidence saved to test_evidence/agent_loading_test.json\n")

# Generate final report
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report = {
    "test_date": datetime.now().isoformat(),
    "tests_executed": {
        "custom_tool_accuracy": {
            "passed": all(t['passed'] for t in test_results),
            "accuracy": f"{sum(1 for t in test_results if t['passed'])/len(test_results)*100:.0f}%"
        },
        "agent_loading": {
            "passed": len(loaded) == 7,
            "agents_loaded": f"{len(loaded)}/7"
        }
    },
    "evidence_files": [
        "test_evidence/tool_accuracy_test.json",
        "test_evidence/agent_loading_test.json"
    ]
}

report_path = f'evaluation_reports/complete_test_{timestamp}.json'
with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)

print("=== TEST COMPLETE ===")
print(f"✓ Report saved: {report_path}")
print("✓ Evidence saved in test_evidence/ folder")
print("\nAll test cases have evidence files!")