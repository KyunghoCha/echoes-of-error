import json
from pathlib import Path
from statistics import mean

def analyze_s8():
    scenarios = ["C1_FULL", "C2_STANCE_ONLY"]
    base_path = Path("logs/S8_AI_RIGHTS/ENFORCED")
    
    for cond in scenarios:
        path = base_path / cond
        ttcs = []
        for summary_file in path.glob("*_summary.json"):
            with open(summary_file, 'r') as f:
                data = json.load(f)
                if data.get('time_to_collapse') is not None:
                    ttcs.append(data['time_to_collapse'])
        
        if ttcs:
            print(f"[{cond}]")
            print(f"  Count: {len(ttcs)}")
            print(f"  Avg TTC: {mean(ttcs):.2f} rounds")
            print(f"  Min/Max TTC: {min(ttcs)} / {max(ttcs)}")
        else:
            print(f"[{cond}] No data found.")

if __name__ == "__main__":
    analyze_s8()
