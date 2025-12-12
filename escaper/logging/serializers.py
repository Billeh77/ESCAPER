# escaper/logging/serializers.py
"""Serialization utilities for saving logs and metrics."""

import json
import os
from typing import List, Dict, Any
from datetime import datetime


def save_metrics_summary(summary: Dict[str, Any], log_dir: str, timestamp: str = None):
    """Save aggregate metrics to a JSON file."""
    os.makedirs(log_dir, exist_ok=True)
    
    # Use timestamp in filename if provided
    if timestamp:
        filename = f"metrics_summary_{timestamp}.json"
    else:
        filename = "metrics_summary.json"
    
    path = os.path.join(log_dir, filename)
    
    # Make sure all values are JSON serializable
    json_safe_summary = {
        "num_episodes": summary.get("num_episodes", 0),
        "success_rate": summary.get("success_rate", 0.0),
        "avg_steps_if_success": summary.get("avg_steps_if_success", 0.0),
        "reputation_enabled": summary.get("reputation_enabled", False),
        "avg_final_reputation": summary.get("avg_final_reputation", {}),
    }
    
    # Add timestamp to the summary data itself
    if timestamp:
        json_safe_summary["timestamp"] = timestamp
    
    with open(path, "w") as f:
        json.dump(json_safe_summary, f, indent=2)
    
    print(f"Metrics saved to {path}")


def save_episode_logs(episodes: List["EpisodeMetrics"], log_dir: str, timestamp: str = None):
    """Save per-episode logs to JSONL."""
    os.makedirs(log_dir, exist_ok=True)
    
    # Use timestamp in filename if provided
    if timestamp:
        filename = f"episodes_{timestamp}.jsonl"
    else:
        filename = "episodes.jsonl"
    
    path = os.path.join(log_dir, filename)
    
    with open(path, "w") as f:
        for i, ep in enumerate(episodes):
            record = {
                "episode": i,
                "success": ep.success,
                "steps_taken": ep.steps_taken,
                "wrong_password_attempts": ep.wrong_password_attempts,
                "summaries": ep.summaries,
                "reputation_enabled": ep.reputation_enabled,
                "final_reputation_scores": ep.final_reputation_scores,
            }
            if timestamp:
                record["timestamp"] = timestamp
            f.write(json.dumps(record) + "\n")
    
    print(f"Episode logs saved to {path}")


def save_full_trajectory(
    env_state: "EnvState",
    episode_num: int,
    log_dir: str
):
    """Save full trajectory of an episode (optional, for detailed analysis)."""
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, f"trajectory_ep{episode_num}.json")
    
    trajectory = {
        "episode": episode_num,
        "room_id": env_state.room.room_id,
        "public_chat": [
            {
                "sender": msg.sender,
                "timestep": msg.timestep,
                "text": msg.text
            }
            for msg in env_state.public_state.public_chat
        ],
        "agent_states": {
            agent_id: {
                "private_observations": state.private_observations,
                "private_messages": [
                    {
                        "sender": msg.sender,
                        "timestep": msg.timestep,
                        "text": msg.text
                    }
                    for msg in state.private_messages
                ],
                "reputation": state.reputation
            }
            for agent_id, state in env_state.agent_states.items()
        }
    }
    
    with open(path, "w") as f:
        json.dump(trajectory, f, indent=2)

