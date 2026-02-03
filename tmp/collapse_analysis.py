import json
from pathlib import Path
from collections import defaultdict
import statistics

def main():
    path = Path("logs")
    # scenario -> condition -> {collapse_count, total_runs, ttc_list, entropy_drops}
    stats = defaultdict(lambda: defaultdict(lambda: {
        "collapse_count": 0,
        "total_runs": 0,
        "ttc_list": [],
        "entropy_drops": []
    }))

    summaries = list(path.rglob("*_summary.json"))
    
    for f in summaries:
        try:
            # We only look at ENFORCED mode for now as requested
            if "ENFORCED" not in str(f):
                continue
                
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            parts = f.parts
            # logs/SCENARIO/MODE/CONDITION/file
            if len(parts) >= 4:
                scenario = parts[-4]
                condition = parts[-2]
                
                s_stat = stats[scenario][condition]
                s_stat["total_runs"] += 1
                
                # Check for collapse
                ttc = data.get("time_to_collapse")
                if ttc is not None:
                    s_stat["collapse_count"] += 1
                    s_stat["ttc_list"].append(ttc)
                
                # Entropy drop
                history = data.get("entropy_history", [])
                if len(history) >= 2:
                    drop = history[0] - history[-1]
                    s_stat["entropy_drops"].append(drop)
        except Exception as e:
            pass

    print(f"{'Scenario':<22} | {'Condition':<18} | {'Collapse':<8} | {'Avg Speed':<10} | {'Sum Drop':<8}")
    print("-" * 75)
    
    for sc in sorted(stats.keys()):
        for cond in sorted(stats[sc].keys()):
            d = stats[sc][cond]
            count = f"{d['collapse_count']}/{d['total_runs']}"
            avg_speed = statistics.mean(d['ttc_list']) if d['ttc_list'] else 0
            avg_speed_str = f"R{avg_speed:.1f}" if avg_speed > 0 else "N/A"
            avg_drop = statistics.mean(d['entropy_drops']) if d['entropy_drops'] else 0
            
            print(f"{sc[:22]:<22} | {cond[:18]:<18} | {count:<8} | {avg_speed_str:<10} | {avg_drop:<8.3f}")

if __name__ == "__main__":
    main()
