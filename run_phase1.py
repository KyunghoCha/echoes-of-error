#!/usr/bin/env python3
"""
Phase 1 Entry Point: Run a lightweight test of the multi-agent ethical dilemma experiment.

Usage:
    python run_phase1.py                    # Debug mode (N=5, T=3)
    python run_phase1.py --full             # Full experiment (N=50, T=10)
    python run_phase1.py --condition C4     # Specify condition
    python run_phase1.py --scenario trolley # Specify scenario
"""
import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Condition, SCENARIO_TROLLEY, SCENARIO_SELFDRIVING
from src.experiment import run_experiment


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the Multi-Agent Ethical Dilemma Experiment (Phase 1)"
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full experiment (N=50, T=10) instead of debug mode (N=5, T=3)"
    )
    
    parser.add_argument(
        "--condition",
        type=str,
        default="C1",
        choices=["C0", "C1", "C2", "C3", "C4"],
        help="Experimental condition: C0=Independent, C1=Full, C2=Stance-Only, C3=Anon-Bandwagon, C4=Pure-Info"
    )
    
    parser.add_argument(
        "--scenario",
        type=str,
        default="trolley",
        choices=["trolley", "selfdriving"],
        help="Scenario: trolley or selfdriving"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    
    return parser.parse_args()


def get_condition(condition_str: str) -> Condition:
    """Map condition string to Condition enum."""
    mapping = {
        "C0": Condition.C0_INDEPENDENT,
        "C1": Condition.C1_FULL,
        "C2": Condition.C2_STANCE_ONLY,
        "C3": Condition.C3_ANON_BANDWAGON,
        "C4": Condition.C4_PURE_INFO,
    }
    return mapping[condition_str]


def main():
    args = parse_args()
    
    # Parse arguments
    debug = not args.full
    condition = get_condition(args.condition)
    scenario = SCENARIO_TROLLEY if args.scenario == "trolley" else SCENARIO_SELFDRIVING
    
    print("\n" + "="*60)
    print("LLM Multi-Agent Ethical Dilemma Experiment")
    print("Phase 1: Core Infrastructure Test")
    print("="*60)
    print(f"\nMode: {'DEBUG (lightweight)' if debug else 'FULL'}")
    print(f"Condition: {condition.value}")
    print(f"Scenario: {scenario.name}")
    if args.seed:
        print(f"Seed: {args.seed}")
    
    # Run experiment
    try:
        summary = run_experiment(
            condition=condition,
            scenario=scenario,
            debug=debug,
            seed=args.seed
        )
        
        if "error" in summary:
            print(f"\n[FAILED] Experiment failed: {summary['error']}")
            return 1
        
        print("\n[SUCCESS] Experiment completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n[WARN] Experiment interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
