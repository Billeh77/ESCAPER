# escaper/logging/serializers.py
"""Serialization utilities for saving logs and metrics."""

import json
import os
from typing import List, Dict, Any
from datetime import datetime


def save_metrics_summary(summary: Dict[str, Any], log_dir: str):
    """Save aggregate metrics to a JSON file."""
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, "metrics_summary.json")
    
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"Metrics saved to {path}")


def save_episode_logs(episodes: List["EpisodeMetrics"], log_dir: str):
    """Save per-episode logs to JSONL."""
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, "episodes.jsonl")
    
    with open(path, "w") as f:
        for i, ep in enumerate(episodes):
            record = {
                "episode": i,
                "success": ep.success,
                "steps_taken": ep.steps_taken,
                "wrong_password_attempts": ep.wrong_password_attempts,
                "summaries": ep.summaries,
            }
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

