"""
Utilities for resuming interrupted experiments.
Handles parsing of JSONL logs to find the last complete round and truncating incomplete data.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

def find_last_complete_round(jsonl_path: Path) -> Tuple[Optional[int], Dict[str, Dict[str, Any]]]:
    """
    Parse JSONL file to find the last successfully completed round.
    
    A round is considered complete if a "round_end" event exists for it.
    
    Args:
        jsonl_path: Path to the .jsonl log file
        
    Returns:
        Tuple containing:
        - last_round (int or None): The number of the last complete round, or None if no rounds completed
        - agent_states (Dict): Map of agent_id -> {stance, rationale} from that round
    """
    if not jsonl_path.exists():
        return None, {}
    
    last_complete_round = -1
    last_round_end_line_idx = -1
    
    # Store agent responses by round to reconstruct state
    # round_num -> {agent_id: {stance, rationale}}
    round_responses: Dict[int, Dict[str, Dict[str, Any]]] = {}
    
    complete_rounds = set()
    
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                event_type = data.get("type")
                
                if event_type == "agent_response":
                    r_num = data.get("round")
                    a_id = data.get("agent_id")
                    
                    if r_num not in round_responses:
                        round_responses[r_num] = {}
                    
                    round_responses[r_num][a_id] = {
                        "stance": data.get("stance"),
                        "rationale": data.get("rationale")
                    }
                    
                elif event_type == "round_end":
                    r_num = data.get("round")
                    complete_rounds.add(r_num)
                    if r_num > last_complete_round:
                        last_complete_round = r_num
                        last_round_end_line_idx = i
                        
            except json.JSONDecodeError:
                continue
        
        if last_complete_round == -1:
            return None, {}
            
        # Extract states for the last complete round
        agent_states = round_responses.get(last_complete_round, {})
        
        return last_complete_round, agent_states
        
    except Exception as e:
        print(f"[Resume] Error parsing log file {jsonl_path}: {e}")
        return None, {}


def truncate_log_to_round(jsonl_path: Path, target_round: int) -> bool:
    """
    Rewrite the JSONL file, removing all lines AFTER the 'round_end' event of target_round.
    
    Args:
        jsonl_path: Path to file
        target_round: The round number to keep up to (inclusive)
        
    Returns:
        True if successful
    """
    if not jsonl_path.exists():
        return False
        
    try:
        valid_lines = []
        found_target = False
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            valid_lines.append(line)
            
            try:
                data = json.loads(line)
                if data.get("type") == "round_end" and data.get("round") == target_round:
                    found_target = True
                    break
            except:
                pass
        
        if not found_target:
            print(f"[Resume] Could not find round_end for round {target_round} during truncation.")
            return False
            
        # Write back truncated content
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            f.writelines(valid_lines)
            
        print(f"[Resume] Truncated {jsonl_path.name} to end of Round {target_round}")
        return True
        
    except Exception as e:
        print(f"[Resume] Error truncating file: {e}")
        return False
