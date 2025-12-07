# escaper/core/tools.py
"""Tool implementations for agent actions."""

from typing import Dict, Any, List
from .state import EnvState, PublicMessage, PrivateMessage


def inspect_object(env: EnvState, agent_id: str, object_id: str) -> str:
    """Inspect an object and add observation to agent's private state."""
    text = env.room.inspect_object(object_id)
    env.agent_states[agent_id].private_observations.append(
        f"[t={env.public_state.timestep}] inspected {object_id}: {text}"
    )
    return text


def try_password(env: EnvState, agent_id: str, object_id: str, password: str) -> str:
    """Try a password on a locked object."""
    # Check if this will reveal new objects
    obj = env.room.objects.get(object_id)
    reveals_objects = False
    if obj and obj.lock and password == obj.lock.password:
        if obj.lock.reveal_objects:
            reveals_objects = True
            revealed_names = [env.room.objects[oid].name for oid in obj.lock.reveal_objects if oid in env.room.objects]
    
    result = env.room.try_password(object_id, password)
    
    # Store event info for verbose logger if objects were revealed
    if reveals_objects and hasattr(env, '_verbose_event'):
        env._verbose_event = f"Door '{obj.name}' opened! Revealed: {', '.join(revealed_names)}"
    
    return result


def send_public(env: EnvState, agent_id: str, message: str) -> str:
    """Send a message to the public chat."""
    env.public_state.public_chat.append(
        PublicMessage(sender=agent_id, timestep=env.public_state.timestep, text=message)
    )
    return "Message posted to public chat."


def send_private(env: EnvState, agent_id: str, recipients: List[str], message: str) -> str:
    """Send a private message to specific recipients (gossip)."""
    for r in recipients:
        if r in env.agent_states:
            env.agent_states[r].private_messages.append(
                PrivateMessage(sender=agent_id, timestep=env.public_state.timestep, text=message)
            )
    return "Private message sent."


def update_reputation(env: EnvState, agent_id: str, updates: Dict[str, float]) -> str:
    """Update the agent's reputation scores for other agents."""
    rep = env.agent_states[agent_id].reputation
    for target, score in updates.items():
        rep[target] = float(score)
    return "Reputation updated."


def get_tool_dispatch(gossip_enabled: bool, reputation_enabled: bool) -> Dict[str, Any]:
    """Return a dispatch table of available tools based on experiment settings."""
    dispatch = {
        "inspect_object": inspect_object,
        "try_password": try_password,
        "send_public": send_public,
    }
    if gossip_enabled:
        dispatch["send_private"] = send_private
    if reputation_enabled:
        dispatch["update_reputation"] = update_reputation
    return dispatch

