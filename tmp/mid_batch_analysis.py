import json
import os
from pathlib import Path
import numpy as np

def analyze_batch(batch_dir):
    results = {"C1_FULL": [], "C2_STANCE_ONLY": [], "C0_INDEPENDENT": []}
    
    files = os.listdir(batch_dir)
    summary_files = [f for f in files if f.endswith("_summary.json")]
    
    for f in summary_files:
        try:
            with open(os.path.join(batch_dir, f), 'r') as jf:
                data = json.load(jf)
                if "config" not in data or "condition" not in data["config"]:
                    print(f"Skipping {f}: missing config or condition")
                    continue
                cond = data["config"]["condition"]
                if cond in results:
                    results[cond].append(data)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            continue
    
    print(f"{'Condition':<20} | {'N':<3} | {'Avg Final Ent':<15} | {'Collapse Rate':<15} | {'Avg Time'}")
    print("-" * 75)
    
    for cond, data_list in results.items():
        if not data_list:
            continue
            
        final_entropies = [d["final_entropy"] for d in data_list]
        collapses = [1 if d["final_entropy"] < 0.7 else 0 for d in data_list]
        times = [d["time_to_collapse"] for d in data_list if d["time_to_collapse"] is not None]
        
        avg_ent = np.mean(final_entropies)
        collapse_rate = np.mean(collapses) * 100
        avg_time = np.mean(times) if times else 0
        
        print(f"{cond:<20} | {len(data_list):<3} | {avg_ent:<15.4f} | {collapse_rate:<14.1f}% | {avg_time:.1f}")

        # Count convergence direction
        dominance = {"PULL": 0, "DO_NOT_PULL": 0, "DIVERSE": 0}
        for d in data_list:
            if d["final_entropy"] > 0.7:
                dominance["DIVERSE"] += 1
            else:
                dist = d["final_distribution"]
                pull = dist.get("PULL_LEVER", 0)
                no_pull = dist.get("DO_NOT_PULL", 0)
                if pull > no_pull:
                    dominance["PULL"] += 1
                else:
                    dominance["DO_NOT_PULL"] += 1
        print(f"  -> Dominance: {dominance}")

if __name__ == "__main__":
    batch_path = r"c:\Experiment\echoes-of-error\logs\batch_20260114_020544_ENFORCED"
    analyze_batch(batch_path)
