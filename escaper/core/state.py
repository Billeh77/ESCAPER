# escaper/core/state.py
"""State management for the escape room environment."""

from dataclasses import dataclass, field
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .room import Room


@dataclass
class PublicMessage:
    """A message in the public chat."""
    sender: str
    timestep: int
    text: str


@dataclass
class PrivateMessage:
    """A private message between agents."""
    sender: str
    timestep: int
    text: str


@dataclass
class PublicState:
    """Shared state visible to all agents."""
    timestep: int = 0
    public_chat: List[PublicMessage] = field(default_factory=list)


@dataclass
class AgentPrivateState:
    """Private state for a single agent."""
    agent_id: str
    private_observations: List[str] = field(default_factory=list)
    private_messages: List[PrivateMessage] = field(default_factory=list)
    reputation: Dict[str, float] = field(default_factory=dict)  # other_agent_id -> score


@dataclass
class EnvState:
    """Complete environment state."""
    room: "Room"
    public_state: PublicState
    agent_states: Dict[str, AgentPrivateState]  # agent_id -> state
    wrong_password_attempts: int = 0
    verbose_events: List[str] = field(default_factory=list)
    agent_names: Dict[str, str] = field(default_factory=dict)  # agent_id -> display name

