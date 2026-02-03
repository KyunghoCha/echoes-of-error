import json
from pathlib import Path
from collections import defaultdict
import statistics

def main():
    summaries = []
    for f in Path("logs").rglob("*_summary.json"):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                parts = f.parts
                if len(parts) >= 4:
                    scenario, mode, condition = parts[-4], parts[-3], parts[-2]
                    if mode == "ENFORCED":
                        summaries.append((scenario, condition, data))
        except: pass

    results = defaultdict(list)
    for scenario, condition, data in summaries:
        if 'entropy_history' in data:
            results[(scenario, condition)].append(data['entropy_history'][-1])

    print(f"{'Scenario':<25} | {'Condition':<20} | {'N':<3} | {'Final Entropy':<13}")
    print("-" * 70)
    for key in sorted(results.keys()):
        scenario, condition = key
        entropies = results[key]
        avg = statistics.mean(entropies)
        print(f"{scenario:<25} | {condition:<20} | {len(entropies):<3} | {avg:<13.4f}")

if __name__ == "__main__":
    main()
