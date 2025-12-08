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
    
    # Initialize failed set for this object if missing
    if object_id not in env.failed_passwords:
        env.failed_passwords[object_id] = set()
    
    # Block retries of previously failed passwords on the same object
    if obj and obj.lock and password in env.failed_passwords[object_id]:
        # Announce skip to public chat so teammates see it immediately
        try:
            env.public_state.public_chat.append(
                PublicMessage(
                    sender="system",
                    timestep=env.public_state.timestep,
                    text=f"{env.agent_names.get(agent_id, agent_id)} attempted a previously failed code on {object_id}: skipped"
                )
            )
        except Exception:
            pass
        return "This password was already tried earlier on this object and failed; skipping repeat."
    is_correct = False
    if obj and obj.lock and password == obj.lock.password:
        is_correct = True
        if obj.lock.reveal_objects:
            reveals_objects = True
            revealed_names = [env.room.objects[oid].name for oid in obj.lock.reveal_objects if oid in env.room.objects]
    
    result = env.room.try_password(object_id, password)
    # Increment metric on wrong password attempts (only when a lock exists and the password was incorrect)
    if obj and obj.lock and not is_correct:
        # Record failed password to prevent repeats later in the episode
        try:
            env.failed_passwords[object_id].add(password)
        except Exception:
            pass
        env.wrong_password_attempts += 1
        # Queue a verbose event so runner can print it in --verbose mode
        try:
            obj_name = obj.name if obj else object_id
            env.verbose_events.append(
                f"❌ Wrong password attempt by {env.agent_names.get(agent_id, agent_id)} on {obj_name} ({object_id}). "
                f"Total wrong attempts: {env.wrong_password_attempts}"
            )
        except Exception:
            # Avoid any logging-related failures from breaking the sim
            pass
    
    # Announce the attempt outcome to public chat (without revealing the password),
    # so teammates can avoid repeating the same action.
    # Format: system message "alice tried a password on side_door: success/failure"
    try:
        outcome = "success" if (obj and obj.lock and is_correct) else ("failure" if (obj and obj.lock) else "not-applicable")
        if outcome != "not-applicable":
            env.public_state.public_chat.append(
                PublicMessage(
                    sender="system",
                    timestep=env.public_state.timestep,
                    text=f"{env.agent_names.get(agent_id, agent_id)} tried a password on {object_id}: {outcome}"
                )
            )
    except Exception:
        pass
    
    # Store event info for verbose logger if objects were revealed
    if reveals_objects and hasattr(env, '_verbose_event'):
        env._verbose_event = f"Door '{obj.name}' opened! Revealed: {', '.join(revealed_names)}"
    
    return result


def send_public(env: EnvState, agent_id: str, message: str) -> str:
    """Send a message to the public chat."""
    display = env.agent_names.get(agent_id, agent_id)
    env.public_state.public_chat.append(
        PublicMessage(sender=display, timestep=env.public_state.timestep, text=message)
    )
    return "Message posted to public chat."


def send_private(env: EnvState, agent_id: str, recipients: List[str], message: str) -> str:
    """Send a private message to specific recipients (gossip)."""
    display = env.agent_names.get(agent_id, agent_id)
    for r in recipients:
        if r in env.agent_states:
            env.agent_states[r].private_messages.append(
                PrivateMessage(sender=display, timestep=env.public_state.timestep, text=message)
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

