# escaper/core/metrics.py
"""Metrics tracking and accumulation."""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class EpisodeMetrics:
    """Metrics for a single episode."""
    summaries: List[str] = field(default_factory=list)
    success: bool = False
    steps_taken: int = 0
    wrong_password_attempts: int = 0
    final_reputation_scores: Dict[str, float] = field(default_factory=dict)  # agent_id -> avg reputation from others
    reputation_enabled: bool = False
    
    def log_summary(self, agent_id: str, step: int, summary: str):
        """Log an agent's end-of-timestep summary."""
        self.summaries.append(f"[t={step}] {agent_id}: {summary}")
    
    def update_step(self, env_state):
        """Update metrics after a step."""
        self.steps_taken = env_state.public_state.timestep + 1
    
    def finalize(self, env_state, reputation_enabled: bool = False):
        """Finalize metrics at end of episode."""
        self.success = env_state.room.escaped
        self.reputation_enabled = reputation_enabled
        
        # Calculate final average reputation scores for each agent
        if reputation_enabled:
            # For each agent, compute the average reputation score others have for them
            all_agent_ids = list(env_state.agent_states.keys())
            
            for target_agent_id in all_agent_ids:
                # Collect all reputation scores that others have for this agent
                scores_for_target = []
                
                for observer_agent_id, observer_state in env_state.agent_states.items():
                    if observer_agent_id != target_agent_id:  # Don't include self-reputation
                        if target_agent_id in observer_state.reputation:
                            scores_for_target.append(observer_state.reputation[target_agent_id])
                
                # Compute average
                if scores_for_target:
                    avg_score = sum(scores_for_target) / len(scores_for_target)
                    self.final_reputation_scores[target_agent_id] = avg_score
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
                "avg_final_reputation": {},
            }
        
        success_count = sum(1 for e in self.episodes if e.success)
        success_rate = success_count / n
        
        successful_episodes = [e for e in self.episodes if e.success]
        avg_steps = (
            sum(e.steps_taken for e in successful_episodes) / len(successful_episodes)
            if successful_episodes
            else 0.0
        )
        
        # Compute average reputation scores across all episodes
        avg_reputation = {}
        reputation_enabled = any(e.reputation_enabled for e in self.episodes)
        
        if reputation_enabled:
            # Collect all agent IDs that appear in any episode
            all_agent_ids = set()
            for ep in self.episodes:
                all_agent_ids.update(ep.final_reputation_scores.keys())
            
            # For each agent, average their reputation scores across episodes
            for agent_id in all_agent_ids:
                scores = [
                    ep.final_reputation_scores[agent_id]
                    for ep in self.episodes
                    if agent_id in ep.final_reputation_scores
                ]
                if scores:
                    avg_reputation[agent_id] = sum(scores) / len(scores)
        
        return {
            "num_episodes": n,
            "success_rate": success_rate,
            "avg_steps_if_success": avg_steps,
            "avg_final_reputation": avg_reputation,
            "reputation_enabled": reputation_enabled,
        }

