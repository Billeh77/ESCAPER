# escaper/core/metrics.py
"""Metrics tracking and accumulation."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class EpisodeMetrics:
    """Metrics for a single episode."""
    summaries: List[str] = field(default_factory=list)
    success: bool = False
    steps_taken: int = 0
    wrong_password_attempts: int = 0
    
    def log_summary(self, agent_id: str, step: int, summary: str):
        """Log an agent's end-of-timestep summary."""
        self.summaries.append(f"[t={step}] {agent_id}: {summary}")
    
    def update_step(self, env_state):
        """Update metrics after a step."""
        self.steps_taken = env_state.public_state.timestep + 1
    
    def finalize(self, env_state):
        """Finalize metrics at end of episode."""
        self.success = env_state.room.escaped
        # Capture wrong password attempts accumulated during the episode
        self.wrong_password_attempts = getattr(env_state, "wrong_password_attempts", 0)


@dataclass
class MetricsAccumulator:
    """Accumulates metrics across multiple episodes."""
    episodes: List[EpisodeMetrics] = field(default_factory=list)
    
    def add(self, ep: EpisodeMetrics):
        """Add an episode's metrics."""
        self.episodes.append(ep)
    
    def summary(self) -> dict:
        """Compute aggregate statistics."""
        n = len(self.episodes)
        if n == 0:
            return {
                "num_episodes": 0,
                "success_rate": 0.0,
                "avg_steps_if_success": 0.0,
            }
        
        success_count = sum(1 for e in self.episodes if e.success)
        success_rate = success_count / n
        
        successful_episodes = [e for e in self.episodes if e.success]
        avg_steps = (
            sum(e.steps_taken for e in successful_episodes) / len(successful_episodes)
            if successful_episodes
            else 0.0
        )
        
        return {
            "num_episodes": n,
            "success_rate": success_rate,
            "avg_steps_if_success": avg_steps,
        }

