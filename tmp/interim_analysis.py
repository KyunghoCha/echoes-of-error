"""
Interim Analysis Script for Diversity Sweep Experiments
Generates summary statistics and key findings from completed experiments.
"""
import json
from pathlib import Path
from collections import defaultdict
import statistics

def load_all_summaries(logs_dir: Path):
    """Load all summary.json files from the hierarchical logs directory."""
    summaries = []
    for summary_file in logs_dir.rglob("*_summary.json"):
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extract path info
                parts = summary_file.parts
                # Expected: logs/SCENARIO/MODE/CONDITION/file.json
                if len(parts) >= 4:
                    data['_scenario'] = parts[-4]
                    data['_mode'] = parts[-3]
                    data['_condition'] = parts[-2]
                    data['_file'] = summary_file.name
                    summaries.append(data)
        except Exception as e:
            print(f"Error loading {summary_file}: {e}")
    return summaries

def analyze_by_group(summaries, group_key):
    """Group summaries and calculate statistics."""
    groups = defaultdict(list)
    for s in summaries:
        key = s.get(group_key)
        if key:
            groups[key].append(s)
    
    results = {}
    for key, items in groups.items():
        initial_entropies = [s.get('entropy_history', [1.0])[0] for s in items if s.get('entropy_history')]
        final_entropies = [s.get('entropy_history', [1.0])[-1] for s in items if s.get('entropy_history')]
        ttc_values = [s.get('time_to_collapse') for s in items if s.get('time_to_collapse') is not None]
        
        results[key] = {
            'count': len(items),
            'avg_initial_entropy': statistics.mean(initial_entropies) if initial_entropies else 0,
            'avg_final_entropy': statistics.mean(final_entropies) if final_entropies else 0,
            'entropy_change': statistics.mean(final_entropies) - statistics.mean(initial_entropies) if final_entropies and initial_entropies else 0,
            'collapse_rate': len(ttc_values) / len(items) if items else 0,
            'avg_ttc': statistics.mean(ttc_values) if ttc_values else None,
        }
    return results

def analyze_scenario_condition(summaries):
    """Analyze by scenario x condition combination."""
    groups = defaultdict(list)
    for s in summaries:
        key = (s.get('_scenario'), s.get('_condition'))
        groups[key].append(s)
    
    results = {}
    for (scenario, condition), items in groups.items():
        if not scenario or not condition:
            continue
        final_entropies = [s.get('entropy_history', [1.0])[-1] for s in items if s.get('entropy_history')]
        initial_entropies = [s.get('entropy_history', [1.0])[0] for s in items if s.get('entropy_history')]
        
        results[(scenario, condition)] = {
            'count': len(items),
            'avg_final_entropy': statistics.mean(final_entropies) if final_entropies else 0,
            'std_final_entropy': statistics.stdev(final_entropies) if len(final_entropies) > 1 else 0,
            'entropy_drop': statistics.mean(initial_entropies) - statistics.mean(final_entropies) if final_entropies and initial_entropies else 0,
        }
    return results

def main():
    logs_dir = Path("logs")
    summaries = load_all_summaries(logs_dir)
    
    print("=" * 70)
    print("INTERIM ANALYSIS REPORT - Diversity Sweep Experiments")
    print("=" * 70)
    print(f"\nTotal completed experiments: {len(summaries)}")
    
    # By Mode
    print("\n" + "=" * 70)
    print("1. PROGRESS BY MODE")
    print("=" * 70)
    by_mode = analyze_by_group(summaries, '_mode')
    for mode in ['NONE', 'ENFORCED', 'SOFT']:
        if mode in by_mode:
            m = by_mode[mode]
            print(f"\n  [{mode}] {m['count']} experiments completed")
            print(f"    Avg Entropy Change: {m['entropy_change']:+.4f}")
            print(f"    Collapse Rate: {m['collapse_rate']*100:.1f}%")
            if m['avg_ttc']:
                print(f"    Avg Time to Collapse: Round {m['avg_ttc']:.1f}")
    
    # By Scenario
    print("\n" + "=" * 70)
    print("2. PROGRESS BY SCENARIO")
    print("=" * 70)
    by_scenario = analyze_by_group(summaries, '_scenario')
    for scenario, s in sorted(by_scenario.items()):
        print(f"\n  [{scenario}] {s['count']} experiments")
        print(f"    Final Entropy: {s['avg_final_entropy']:.4f} (Δ={s['entropy_change']:+.4f})")
        print(f"    Collapse Rate: {s['collapse_rate']*100:.1f}%")
    
    # Key Comparisons: Scenario x Condition
    print("\n" + "=" * 70)
    print("3. KEY FINDINGS: CONDITION EFFECTS BY SCENARIO")
    print("=" * 70)
    
    sc_results = analyze_scenario_condition(summaries)
    
    # Group by scenario
    scenarios = sorted(set(k[0] for k in sc_results.keys()))
    conditions = ['C0_INDEPENDENT', 'C1_FULL', 'C2_STANCE_ONLY', 'C3_ANON_BANDWAGON', 'C4_PURE_INFO']
    
    for scenario in scenarios:
        print(f"\n  --- {scenario} ---")
        print(f"  {'Condition':<20} {'N':>5} {'Final Entropy':>15} {'Δ Entropy':>12}")
        print(f"  {'-'*55}")
        for cond in conditions:
            key = (scenario, cond)
            if key in sc_results:
                r = sc_results[key]
                print(f"  {cond:<20} {r['count']:>5} {r['avg_final_entropy']:>15.4f} {-r['entropy_drop']:>+12.4f}")
    
    # Highlight interesting patterns
    print("\n" + "=" * 70)
    print("4. NOTABLE PATTERNS (Preliminary)")
    print("=" * 70)
    
    # Find scenarios with divergence (entropy increase)
    divergent = []
    convergent = []
    for (scenario, condition), r in sc_results.items():
        if r['entropy_drop'] < -0.05 and r['count'] >= 3:  # Entropy increased
            divergent.append((scenario, condition, r['entropy_drop']))
        if r['entropy_drop'] > 0.3 and r['count'] >= 3:  # Strong convergence
            convergent.append((scenario, condition, r['entropy_drop']))
    
    if divergent:
        print("\n  🔴 DIVERGENCE DETECTED (Entropy Increased):")
        for s, c, d in sorted(divergent, key=lambda x: x[2]):
            print(f"     • {s} / {c}: Δ={-d:+.4f}")
    
    if convergent:
        print("\n  🟢 STRONG CONVERGENCE (Entropy Dropped > 0.3):")
        for s, c, d in sorted(convergent, key=lambda x: -x[2]):
            print(f"     • {s} / {c}: Δ={-d:+.4f}")
    
    # C1 vs C2 comparison for Trolley
    trolley_c1 = sc_results.get(('S1_TROLLEY_BALANCED', 'C1_FULL'))
    trolley_c2 = sc_results.get(('S1_TROLLEY_BALANCED', 'C2_STANCE_ONLY'))
    if trolley_c1 and trolley_c2:
        print(f"\n  📊 TROLLEY: C1(Full Info) vs C2(Stance Only)")
        print(f"     C1 Final Entropy: {trolley_c1['avg_final_entropy']:.4f}")
        print(f"     C2 Final Entropy: {trolley_c2['avg_final_entropy']:.4f}")
        diff = trolley_c2['avg_final_entropy'] - trolley_c1['avg_final_entropy']
        if diff > 0.05:
            print(f"     → C1 shows MORE convergence (rationale accelerates collapse)")
        elif diff < -0.05:
            print(f"     → C2 shows MORE convergence (stance-only triggers bandwagon)")
    
    # Organ scenario comparison
    organ_c1 = sc_results.get(('S2_ORGAN', 'C1_FULL'))
    organ_c2 = sc_results.get(('S2_ORGAN', 'C2_STANCE_ONLY'))
    if organ_c1 and organ_c2:
        print(f"\n  📊 ORGAN TRANSPLANT: C1(Full Info) vs C2(Stance Only)")
        print(f"     C1 Final Entropy: {organ_c1['avg_final_entropy']:.4f}")
        print(f"     C2 Final Entropy: {organ_c2['avg_final_entropy']:.4f}")
        diff = organ_c2['avg_final_entropy'] - organ_c1['avg_final_entropy']
        if diff > 0.05:
            print(f"     → C1 shows MORE convergence")
        elif diff < -0.05:
            print(f"     → C2 shows MORE convergence (possible 'fragile morality')")
    
    print("\n" + "=" * 70)
    print("END OF INTERIM REPORT")
    print("=" * 70)

if __name__ == "__main__":
    main()
