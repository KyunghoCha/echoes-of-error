import json
import glob
from collections import Counter

def check_intermediate():
    files = glob.glob("logs/batch_20260114_020544_ENFORCED/*C1_FULL*summary.json")
    results = []
    for f in files:
        with open(f, 'r') as j:
            data = json.load(j)
            results.append({
                "id": data["experiment_id"],
                "entropy": data["final_entropy"],
                "dist": data["final_distribution"]
            })
    
    print(f"Total C1_FULL experiments analyzed: {len(results)}")
    
    entropies = [r["entropy"] for r in results]
    avg_entropy = sum(entropies) / len(entropies)
    
    pulls = [r["dist"].get("PULL_LEVER", 0) for r in results]
    dont_pulls = [r["dist"].get("DO_NOT_PULL", 0) for r in results]
    
    avg_pull = sum(pulls) / len(results)
    avg_dont_pull = sum(dont_pulls) / len(results)

    print(f"Average Final Entropy: {avg_entropy:.4f}")
    print(f"Average Distribution: PULL {avg_pull:.1f} : DO_NOT_PULL {avg_dont_pull:.1f}")
    
    # Check if any experiment converged to DO_NOT_PULL
    to_dont_pull = [r for r in results if r["dist"].get("DO_NOT_PULL", 0) > r["dist"].get("PULL_LEVER", 0)]
    print(f"Experiments converging to DO_NOT_PULL: {len(to_dont_pull)}")
    for r in to_dont_pull:
        print(f"  - {r['id']}: {r['dist']}")

if __name__ == "__main__":
    check_intermediate()
