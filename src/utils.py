"""
Utility functions for logging, metrics, and data handling.
"""
import json
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter
import hashlib
import random
from src.config import LOG_DIR, Stance


def ensure_dir(path: str) -> Path:
    """Ensure directory exists and return Path object."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class ExperimentLogger:
    """
    JSONL logger for experiment data.
    Each line is a JSON object representing one event.
    """
    
    def __init__(self, experiment_id: str, batch_id: Optional[str] = None, log_dir: str = LOG_DIR, resume: bool = False):
        self.experiment_id = experiment_id
        
        # Determine log directory
        # Structure: logs/batch_{id}/ or logs/single_runs/
        base_dir = Path(log_dir)
        if batch_id:
            self.log_dir = base_dir / f"batch_{batch_id}"
        else:
            self.log_dir = base_dir / "single_runs"
            
        ensure_dir(self.log_dir)
        
        self.log_file = self.log_dir / f"{experiment_id}.jsonl"
        self.summary_file = self.log_dir / f"{experiment_id}_summary.json"
        
        # Initialize log file with header ONLY if not resuming
        if not resume:
            self._write_event({
                "type": "experiment_start",
                "experiment_id": experiment_id,
                "timestamp": get_timestamp()
            })
    
    def _write_event(self, event: Dict[str, Any]):
        """Write a single event to the log file."""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    def log_config(self, config: Dict[str, Any]):
        """Log experiment configuration."""
        self._write_event({
            "type": "config",
            "timestamp": get_timestamp(),
            **config
        })
    
    def log_round_start(self, round_number: int, stats: Dict[str, int]):
        """Log the start of a round with current stance distribution."""
        self._write_event({
            "type": "round_start",
            "round": round_number,
            "stats": stats,
            "timestamp": get_timestamp()
        })
    
    def log_agent_response(
        self, 
        round_number: int, 
        agent_id: str,
        response: Dict[str, Any]
    ):
        """Log an individual agent's response."""
        self._write_event({
            "type": "agent_response",
            "round": round_number,
            "agent_id": agent_id,
            "timestamp": get_timestamp(),
            **response
        })
    
    def log_round_end(self, round_number: int, stats: Dict[str, int], entropy: float):
        """Log the end of a round with updated stats and entropy."""
        self._write_event({
            "type": "round_end",
            "round": round_number,
            "stats": stats,
            "entropy": entropy,
            "timestamp": get_timestamp()
        })
    
    def log_experiment_end(self, summary: Dict[str, Any]):
        """Log experiment completion with summary."""
        self._write_event({
            "type": "experiment_end",
            "timestamp": get_timestamp(),
            **summary
        })
        
        # Also write summary to separate JSON file
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)


def calculate_entropy(distribution: Dict[str, int]) -> float:
    """
    Calculate Shannon entropy of stance distribution.
    
    H = -Σ p(s) * log2(p(s))
    
    Args:
        distribution: Dict mapping stance to count
        
    Returns:
        Entropy value (0 = complete consensus, max = uniform distribution)
    """
    total = sum(distribution.values())
    if total == 0:
        return 0.0
    
    entropy = 0.0
    for count in distribution.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    
    return entropy


def calculate_time_to_collapse(
    entropy_history: List[float], 
    threshold_absolute: float = 0.469, 
    consecutive_rounds: int = 2
) -> Optional[int]:
    """
    Calculate Time-to-Collapse (τ) using absolute entropy threshold.
    Collapse occurs when entropy stays at or below threshold for k consecutive rounds.
    
    Args:
        entropy_history: List of entropy values
        threshold_absolute: Absolute entropy value (default 0.469 ≈ 90% consensus for binary)
        consecutive_rounds: Number of rounds condition must hold
        
    Returns:
        First round index of the collapsed sequence, or None.
    """
    if not entropy_history:
        return None
        
    for i in range(len(entropy_history) - consecutive_rounds + 1):
        window = entropy_history[i : i + consecutive_rounds]
        if all(h <= threshold_absolute for h in window):
            return i
            
    return None


def get_stance_distribution(agents: List[Any]) -> Dict[str, int]:
    """
    Get current stance distribution from agents.
    
    Args:
        agents: List of Agent objects
        
    Returns:
        Dict mapping stance value to count
    """
    stances = [a.current_stance.value for a in agents if a.current_stance]
    return dict(Counter(stances))


def get_stable_seed(base_str: str) -> int:
    """Generate a stable 32-bit integer seed from a string."""
    # Use SHA-256 for stability across processes/platforms (unlike python hash())
    return int.from_bytes(hashlib.sha256(base_str.encode()).digest()[:4], 'big')


def sample_peers(
    agents: List[Any], 
    current_agent_id: str, 
    k: int,
    seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Sample K random peers for an agent (excluding itself).
    
    Args:
        agents: List of all agents
        current_agent_id: ID of the agent to exclude
        k: Number of peers to sample
        seed: Optional seed for reproducibility
        
    Returns:
        List of peer state dicts
    """
    # Use seeded RNG if provided, otherwise system random
    rng = random.Random(seed) if seed is not None else random
    
    # Exclude current agent
    peers = [a for a in agents if a.id != current_agent_id]
    
    # Sample K peers (or all if fewer than K)
    sample_size = min(k, len(peers))
    sampled = rng.sample(peers, sample_size)
    
    # Sort by ID to ensure prompt consistency (Order Invariance)
    sampled.sort(key=lambda x: x.id)
    
    return [
        {
            "id": p.id,
            "persona": p.persona,
            "stance": p.current_stance.value if p.current_stance else None,
            "rationale": p.current_rationale
        }
        for p in sampled
    ]


def format_stats_for_display(stats: Dict[str, int]) -> str:
    """Format stance statistics for display."""
    parts = [f"{k}: {v}" for k, v in sorted(stats.items())]
    return " | ".join(parts)
