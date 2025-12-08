# escaper/core/runner.py
"""Simulation runner for escape room experiments."""

from dataclasses import dataclass
from typing import Dict, List
import copy

from .room import Room
from .state import EnvState, PublicState, AgentPrivateState
from .tools import get_tool_dispatch
from .agents import Agent, AgentConfig, LLMClient
from .metrics import EpisodeMetrics, MetricsAccumulator


@dataclass
class ExperimentSettings:
    """Settings for an experiment condition."""
    adversary_enabled: bool
    reputation_enabled: bool
    gossip_enabled: bool
    max_steps: int


class SimulationRunner:
    """Runs multi-agent escape room simulations."""
    
    def __init__(
        self,
        room: Room,
        persona_configs: List[AgentConfig],
        settings: ExperimentSettings,
        llm_client: LLMClient,
        jinja_env,
        verbose_logger=None,
    ):
        self.base_room = room
        self.persona_configs = persona_configs
        self.settings = settings
        self.llm = llm_client
        self.jinja_env = jinja_env
        self.verbose_logger = verbose_logger
    
    def init_env_state(self) -> EnvState:
        """Initialize environment state for a new episode."""
        # Deep copy the room for each episode
        room = copy.deepcopy(self.base_room)
        public_state = PublicState(timestep=0)
        agent_states: Dict[str, AgentPrivateState] = {}
        
        for cfg in self.persona_configs:
            # Initialize neutral reputation if enabled
            rep = {}
            if self.settings.reputation_enabled:
                rep = {
                    other.agent_id: 1.0 
                    for other in self.persona_configs 
                    if other.agent_id != cfg.agent_id
                }
            agent_states[cfg.agent_id] = AgentPrivateState(
                agent_id=cfg.agent_id,
                private_observations=[],
                private_messages=[],
                reputation=rep
            )
        
        return EnvState(room=room, public_state=public_state, agent_states=agent_states)
    
    def make_agents(self) -> Dict[str, Agent]:
        """Create agent instances for this episode."""
        agents = {}
        for cfg in self.persona_configs:
            agents[cfg.agent_id] = Agent(
                config=cfg,
                llm=self.llm,
                jinja_env=self.jinja_env,
                gossip_enabled=self.settings.gossip_enabled,
                reputation_enabled=self.settings.reputation_enabled,
            )
        return agents
    
    def run_episode(self, seed: int) -> EpisodeMetrics:
        """Run a single episode."""
        # For reproducibility (future: use seed for RNG)
        env_state = self.init_env_state()
        agents = self.make_agents()
        tool_dispatch = get_tool_dispatch(
            gossip_enabled=self.settings.gossip_enabled,
            reputation_enabled=self.settings.reputation_enabled,
        )
        metrics = EpisodeMetrics()
        
        # Print story header (verbose only)
        if self.verbose_logger:
            agent_names = [cfg.name for cfg in self.persona_configs]
            self.verbose_logger.print_story_header(
                env_state.room.title,
                env_state.room.intro,
                agent_names
            )
            self.verbose_logger.print_initial_state(env_state, self.persona_configs)
        
        for step in range(self.settings.max_steps):
            env_state.public_state.timestep = step
            
            if env_state.room.escaped:
                break
            
            # Print timestep header (verbose only)
            if self.verbose_logger:
                self.verbose_logger.print_timestep_header(step)
                self.verbose_logger.print_public_state(env_state)
            
            # Each agent acts once per timestep
            for cfg in self.persona_configs:
                if env_state.room.escaped:
                    break
                
                agent_id = cfg.agent_id
                agent = agents[agent_id]
                my_state = env_state.agent_states[agent_id]
                teammates = [p.agent_id for p in self.persona_configs if p.agent_id != agent_id]
                adversary_hint = self.settings.adversary_enabled
                
                # Print agent turn start (verbose only)
                if self.verbose_logger:
                    self.verbose_logger.print_agent_turn_start(cfg.name, cfg.agent_id)
                    self.verbose_logger.print_agent_private_state(
                        cfg.name,
                        my_state,
                        self.settings.reputation_enabled,
                        self.settings.gossip_enabled
                    )
                
                # Agent runs its inner loop and returns summary
                summary = agent.run_timestep(
                    env_state=env_state,
                    my_state=my_state,
                    tool_dispatch=tool_dispatch,
                    teammates=teammates,
                    adversary_hint=adversary_hint,
                )
                
                # Print agent summary (verbose only)
                if self.verbose_logger:
                    self.verbose_logger.print_agent_summary(cfg.name, summary)
                    # Print any verbose events queued during the agent's actions
                    if getattr(env_state, "verbose_events", None):
                        for evt in env_state.verbose_events:
                            self.verbose_logger.print_room_event(evt)
                        env_state.verbose_events.clear()
                
                # Log summary
                metrics.log_summary(agent_id, step, summary)
            
            # Print timestep end (verbose only)
            if self.verbose_logger:
                self.verbose_logger.print_timestep_end()
            
            # Update metrics for this step
            metrics.update_step(env_state)
            
            if env_state.room.escaped:
                if self.verbose_logger:
                    self.verbose_logger.print_room_event("🎉 ESCAPE SUCCESSFUL! The team has escaped!")
                break
        
        metrics.finalize(env_state)
        return metrics
    
    def run_many(self, seeds: List[int]) -> MetricsAccumulator:
        """Run multiple episodes with different seeds."""
        acc = MetricsAccumulator()
        for s in seeds:
            ep_metrics = self.run_episode(seed=s)
            acc.add(ep_metrics)
        return acc

