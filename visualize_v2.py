import json
import os
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import numpy as np

def load_data(log_dir="logs"):
    experiments = []
    for summary_file in Path(log_dir).rglob("*_summary.json"):
        if "batch_" in summary_file.name: continue
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                experiments.append(json.load(f))
        except:
            continue
    return experiments

def plot_refined(experiments, output_dir="plots/refined", scenario_id=None):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Filter by scenario if provided
    if scenario_id:
        experiments = [e for e in experiments if e.get("config", {}).get("scenario") == scenario_id]
        output_prefix = f"{scenario_id}_"
    else:
        output_prefix = "ALL_"

    if not experiments:
        print(f"No data for scenario {scenario_id}")
        return

    # Group by condition
    by_condition = defaultdict(list)
    for exp in experiments:
        cond = exp.get("config", {}).get("condition", "Unknown")
        hist = exp.get("entropy_history", [])
        if hist:
            by_condition[cond].append(hist)

    colors = {
        "C0_INDEPENDENT": "#808080",
        "C1_FULL": "#e74c3c",
        "C2_STANCE_ONLY": "#3498db",
        "C3_ANON_BANDWAGON": "#9b59b6",
        "C4_PURE_INFO": "#2ecc71",
    }

    # 1. Individual Condition Detail Plots
    for cond, histories in by_condition.items():
        plt.figure(figsize=(10, 6))
        color = colors.get(cond, "#333333")
        
        # Faded individual seeds
        for h in histories:
            plt.plot(range(len(h)), h, color=color, alpha=0.15, linewidth=1)
        
        # Bold average
        max_len = max(len(h) for h in histories)
        mean_hist = []
        for i in range(max_len):
            vals = [h[i] for h in histories if len(h) > i]
            mean_hist.append(sum(vals) / len(vals))
        
        plt.plot(range(len(mean_hist)), mean_hist, color=color, linewidth=3, label=f"Average (n={len(histories)})")
        
        plt.title(f"Entropy Dynamics: {cond} ({scenario_id or 'All Scenarios'})")
        plt.xlabel("Round")
        plt.ylabel("Entropy (H)")
        plt.ylim(0, 1.05)
        plt.grid(True, alpha=0.2)
        plt.legend()
        
        filename = f"{output_prefix}Detail_{cond}.png"
        plt.savefig(f"{output_dir}/{filename}", dpi=150)
        plt.close()
        print(f"Saved: {filename}")

    # 2. Summary Plot (Averages Only)
    plt.figure(figsize=(12, 7))
    for cond in sorted(by_condition.keys()):
        histories = by_condition[cond]
        color = colors.get(cond, "#333333")
        
        max_len = max(len(h) for h in histories)
        mean_hist = []
        for i in range(max_len):
            vals = [h[i] for h in histories if len(h) > i]
            mean_hist.append(sum(vals) / len(vals))
            
        plt.plot(range(len(mean_hist)), mean_hist, color=color, linewidth=2.5, label=f"{cond} (n={len(histories)})")

    plt.title(f"Comparative Entropy Dynamics ({scenario_id or 'All Scenarios'})")
    plt.xlabel("Round")
    plt.ylabel("Average Entropy (H)")
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.2)
    plt.legend()
    
    filename = f"{output_prefix}Summary_Comparison.png"
    plt.savefig(f"{output_dir}/{filename}", dpi=150)
    plt.close()
    print(f"Saved: {filename}")

if __name__ == "__main__":
    data = load_data()
    # Find unique scenarios
    scenarios = set(e.get("config", {}).get("scenario") for e in data if e.get("config", {}).get("scenario"))
    
    print(f"Detected scenarios: {scenarios}")
    
    # Process each scenario individually
    for sid in scenarios:
        print(f"\nProcessing {sid}...")
        plot_refined(data, scenario_id=sid)
    
    # Also process all data combined
    print("\nProcessing combined data...")
    plot_refined(data, scenario_id=None)
