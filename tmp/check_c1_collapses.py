import json
import glob

def check_all_c1():
    files = glob.glob("logs/batch_20260114_020544_ENFORCED/*C1_FULL*summary.json")
    print(f"{'Experiment ID':<45} {'Final Entropy':<15} {'Distribution':<20}")
    print("-" * 80)
    
    collapses = 0
    total = len(files)
    
    for f in files:
        with open(f, 'r') as j:
            data = json.load(j)
            entropy = data["final_entropy"]
            dist = data["final_distribution"]
            dist_str = f"P:{dist.get('PULL_LEVER', 0)} DNP:{dist.get('DO_NOT_PULL', 0)}"
            
            # Simple threshold for collapse: entropy < 0.7 (approx 24:6 or worse)
            is_collapsed = entropy < 0.7
            if is_collapsed:
                collapses += 1
            
            print(f"{data['experiment_id']:<45} {entropy:<15.4f} {dist_str:<20} {'[COLLAPSED]' if is_collapsed else '[DIVERSE]'}")

    print("-" * 80)
    print(f"Total: {total}, Collapsed: {collapses}, Diversity Preserved: {total - collapses}")

if __name__ == "__main__":
    check_all_c1()
