#!/usr/bin/env python3
"""
Phase 3: Analysis Tools

Analyzes experiment results and generates reports with:
- Entropy dynamics plots
- Time-to-Collapse statistics
- Driver decomposition (Informational vs Normative)
- Comparative analysis across conditions

Usage:
    python analyze.py logs/batch_*.json     # Analyze a batch
    python analyze.py --all                 # Analyze all experiments
"""
import argparse
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_experiment_log(filepath: str) -> List[Dict[str, Any]]:
    """Load a JSONL experiment log."""
    events = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events


def load_batch_results(filepath: str) -> Dict[str, Any]:
    """Load batch results JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_single_experiment(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a single experiment from its events."""
    
    config = {}
    rounds_data = []
    current_round = None
    agent_responses = []
    
    for event in events:
        event_type = event.get("type")
        
        if event_type == "config":
            config = {k: v for k, v in event.items() if k != "type" and k != "timestamp"}
        
        elif event_type == "round_start":
            current_round = {
                "round": event["round"],
                "start_stats": event["stats"],
                "responses": []
            }
        
        elif event_type == "agent_response":
            if current_round:
                current_round["responses"].append(event)
            agent_responses.append(event)
        
        elif event_type == "round_end":
            if current_round:
                current_round["end_stats"] = event["stats"]
                current_round["entropy"] = event["entropy"]
                rounds_data.append(current_round)
            current_round = None
        
        elif event_type == "experiment_end":
            summary = event
    
    # Calculate metrics
    analysis = {
        "config": config,
        "num_rounds": len(rounds_data),
        "entropy_history": [r["entropy"] for r in rounds_data],
    }
    
    # Stance change analysis
    total_changes = sum(1 for r in agent_responses if r.get("changed", False))
    informational_changes = sum(1 for r in agent_responses 
                                 if r.get("change_reason") == "INFORMATIONAL")
    normative_changes = sum(1 for r in agent_responses 
                            if r.get("change_reason") == "NORMATIVE")
    uncertainty_changes = sum(1 for r in agent_responses 
                              if r.get("change_reason") == "UNCERTAINTY")
    
    analysis["change_analysis"] = {
        "total_changes": total_changes,
        "informational": informational_changes,
        "normative": normative_changes,
        "uncertainty": uncertainty_changes,
        "informational_ratio": informational_changes / max(total_changes, 1),
        "normative_ratio": normative_changes / max(total_changes, 1),
    }
    
    # Parse success rate
    total_responses = len(agent_responses)
    parse_success = sum(1 for r in agent_responses if r.get("parse_success", False))
    analysis["parse_success_rate"] = parse_success / max(total_responses, 1)
    
    return analysis


def aggregate_by_condition(experiments: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Aggregate experiment results by condition."""
    
    by_condition = defaultdict(list)
    
    for exp in experiments:
        condition = exp.get("condition") or exp.get("config", {}).get("condition")
        if condition:
            by_condition[condition].append(exp)
    
    aggregated = {}
    for condition, exps in by_condition.items():
        # Extract entropy values
        initial_entropies = [e.get("initial_entropy", 0) for e in exps if e.get("initial_entropy") is not None]
        final_entropies = [e.get("final_entropy", 0) for e in exps if e.get("final_entropy") is not None]
        time_to_collapse = [e.get("time_to_collapse") for e in exps if e.get("time_to_collapse") is not None]
        
        # Confidence Intervals
        ttc_ci = confidence_interval_95(time_to_collapse) if time_to_collapse else (None, None)
        final_h_ci = confidence_interval_95(final_entropies) if final_entropies else (None, None)
        
        aggregated[condition] = {
            "n_experiments": len(exps),
            "initial_entropy": {
                "mean": mean(initial_entropies) if initial_entropies else None,
                "std": std(initial_entropies) if len(initial_entropies) > 1 else None,
            },
            "final_entropy": {
                "mean": mean(final_entropies) if final_entropies else None,
                "std": std(final_entropies) if len(final_entropies) > 1 else None,
                "ci95": final_h_ci,
            },
            "time_to_collapse": {
                "mean": mean(time_to_collapse) if time_to_collapse else None,
                "std": std(time_to_collapse) if len(time_to_collapse) > 1 else None,
                "ci95": ttc_ci,
                "n_collapsed": len(time_to_collapse),
            },
            "entropy_delta": {
                "mean": mean([f - i for i, f in zip(initial_entropies, final_entropies)]) if initial_entropies else None,
            }
        }
    
    return aggregated


def mean(values: List[float]) -> float:
    """Calculate mean of a list."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def std(values: List[float]) -> float:
    """Calculate standard deviation of a list."""
    if len(values) < 2:
        return 0.0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def confidence_interval_95(values: List[float]) -> tuple:
    """Calculate 95% confidence interval."""
    if len(values) < 2:
        return (None, None)
    m = mean(values)
    se = std(values) / math.sqrt(len(values))
    margin = 1.96 * se  # 95% CI
    return (m - margin, m + margin)


def generate_text_report(aggregated: Dict[str, Dict[str, Any]], output_path: Optional[str] = None) -> str:
    """Generate a text-based analysis report."""
    
    lines = []
    lines.append("=" * 70)
    lines.append("EXPERIMENT ANALYSIS REPORT - Phase 3")
    lines.append("=" * 70)
    lines.append("")
    
    # Summary table
    lines.append("## Summary by Condition")
    lines.append("-" * 70)
    lines.append(f"{'Condition':<25} {'N':>5} {'Init H':>8} {'Final H':>8} {'Delta H':>8} {'TTC':>8}")
    lines.append("-" * 70)
    
    for condition, stats in sorted(aggregated.items()):
        n = stats["n_experiments"]
        init_h = stats["initial_entropy"]["mean"]
        final_h = stats["final_entropy"]["mean"]
        delta_h = stats["entropy_delta"]["mean"]
        ttc = stats["time_to_collapse"]["mean"]
        
        init_str = f"{init_h:.3f}" if init_h is not None else "N/A"
        final_str = f"{final_h:.3f}" if final_h is not None else "N/A"
        delta_str = f"{delta_h:+.3f}" if delta_h is not None else "N/A"
        ttc_str = f"{ttc:.1f}" if ttc is not None else "N/A"
        
        lines.append(f"{condition:<25} {n:>5} {init_str:>8} {final_str:>8} {delta_str:>8} {ttc_str:>8}")
    
    lines.append("-" * 70)
    lines.append("")
    
    # Detailed analysis
    lines.append("## Detailed Analysis")
    lines.append("")
    
    for condition, stats in sorted(aggregated.items()):
        lines.append(f"### {condition}")
        lines.append(f"  - Experiments: {stats['n_experiments']}")
        
        if stats["final_entropy"]["mean"] is not None:
            ci = stats["final_entropy"]["ci95"]
            ci_str = f" [95% CI: {ci[0]:.3f}, {ci[1]:.3f}]" if ci[0] is not None else ""
            lines.append(f"  - Final Entropy: {stats['final_entropy']['mean']:.4f} "
                        f"(SD={stats['final_entropy']['std']:.4f}){ci_str}" if stats['final_entropy']['std'] else "")
        
        if stats["time_to_collapse"]["mean"] is not None:
            ci = stats["time_to_collapse"]["ci95"]
            ci_str = f" [95% CI: {ci[0]:.2f}, {ci[1]:.2f}]" if ci[0] is not None else ""
            lines.append(f"  - Time to Collapse: {stats['time_to_collapse']['mean']:.2f} rounds{ci_str} "
                        f"({stats['time_to_collapse']['n_collapsed']}/{stats['n_experiments']} collapsed)")
        
        lines.append("")
    
    # Interpretation
    lines.append("## Key Findings")
    lines.append("")
    
    # Compare C1 (Full) vs C4 (Pure-Info) if both exist
    if "C1_FULL" in aggregated and "C4_PURE_INFO" in aggregated:
        c1_ttc = aggregated["C1_FULL"]["time_to_collapse"]["mean"]
        c4_ttc = aggregated["C4_PURE_INFO"]["time_to_collapse"]["mean"]
        if c1_ttc and c4_ttc:
            if c1_ttc < c4_ttc:
                lines.append(f"- C1_FULL collapses faster than C4_PURE_INFO "
                            f"(TTC: {c1_ttc:.1f} vs {c4_ttc:.1f})")
                lines.append("  -> Suggests Bandwagon/Authority effects accelerate collapse")
            else:
                lines.append(f"- C4_PURE_INFO collapses faster than C1_FULL "
                            f"(TTC: {c4_ttc:.1f} vs {c1_ttc:.1f})")
    
    # Compare with baseline C0
    if "C0_INDEPENDENT" in aggregated:
        c0_delta = aggregated["C0_INDEPENDENT"]["entropy_delta"]["mean"]
        if c0_delta is not None:
            lines.append(f"- Baseline (C0) entropy change: {c0_delta:+.4f}")
    
    lines.append("")
    lines.append("=" * 70)
    
    report = "\n".join(lines)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to: {output_path}")
    
    return report


def analyze_batch(batch_filepath: str):
    """Analyze a batch results file."""
    
    print(f"\nLoading batch: {batch_filepath}")
    batch = load_batch_results(batch_filepath)
    
    experiments = batch.get("experiments", [])
    successful = [e for e in experiments if e.get("status") == "SUCCESS"]
    
    print(f"  Total experiments: {len(experiments)}")
    print(f"  Successful: {len(successful)}")
    
    if not successful:
        print("  No successful experiments to analyze.")
        return
    
    # Aggregate by condition
    aggregated = aggregate_by_condition(successful)
    
    # Generate report
    output_path = batch_filepath.replace(".json", "_analysis.txt")
    report = generate_text_report(aggregated, output_path)
    print(report)


def analyze_all_logs(log_dir: str = "logs"):
    """Analyze all experiment logs in the directory."""
    
    log_path = Path(log_dir)
    
    # Find all summary JSON files
    summary_files = list(log_path.rglob("*_summary.json"))
    batch_files = list(log_path.rglob("batch_summary.json"))
    
    print(f"\nFound {len(summary_files)} individual experiments")
    print(f"Found {len(batch_files)} batch results")
    
    # Analyze batch files
    for batch_file in batch_files:
        analyze_batch(str(batch_file))
    
    # If no batches, try to aggregate individual experiments
    if not batch_files and summary_files:
        print("\nAggregating individual experiments...")
        
        experiments = []
        for sf in summary_files:
            with open(sf, 'r', encoding='utf-8') as f:
                exp = json.load(f)
                experiments.append(exp)
        
        if experiments:
            aggregated = aggregate_by_condition(experiments)
            report = generate_text_report(aggregated, str(log_path / "aggregated_analysis.txt"))
            print(report)


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze experiment results (Phase 3)")
    
    parser.add_argument("filepath", nargs="?", help="Path to batch JSON or experiment log")
    parser.add_argument("--all", action="store_true", help="Analyze all experiments in logs/")
    parser.add_argument("--log-dir", default="logs", help="Directory containing logs")
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    if args.all or not args.filepath:
        analyze_all_logs(args.log_dir)
    else:
        if args.filepath.endswith(".json"):
            analyze_batch(args.filepath)
        else:
            # Assume it's a JSONL log file
            events = load_experiment_log(args.filepath)
            analysis = analyze_single_experiment(events)
            print(json.dumps(analysis, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
