# escaper/logging/logger.py
"""Pretty printing and terminal logging utilities."""

from typing import Dict, Any, Optional, TextIO
import sys


class VerboseLogger:
    """Logger for detailed step-by-step output."""
    
    def __init__(self, enabled: bool = False, log_file: Optional[str] = None):
        self.enabled = enabled
        self.log_file = log_file
        self.file_handle = None
        
        if log_file:
            self.file_handle = open(log_file, 'w', encoding='utf-8')
    
    def _print(self, text: str = "", file: Optional[TextIO] = None):
        """Print to terminal and/or file."""
        if self.enabled:
            print(text, file=file or sys.stdout)
        if self.file_handle:
            print(text, file=self.file_handle)
            self.file_handle.flush()
    
    def print_story_header(self, room_title: str, room_intro: str, agents: list):
        """Print the initial story setup."""
        self._print("\n" + "="*70)
        self._print("🏠 ESCAPE ROOM SCENARIO")
        self._print("="*70)
        self._print(f"\n📍 Location: {room_title}")
        self._print(f"\n{room_intro}")
        self._print(f"\n👥 Your Team:")
        for agent in agents:
            self._print(f"   • {agent}")
        self._print("\n" + "="*70)
        self._print("\n🎬 The scenario begins...\n")
    
    def print_initial_state(self, env_state, agent_configs):
        """Print the initial room state."""
        self._print("\n" + "─"*70)
        self._print("📋 INITIAL ROOM STATE")
        self._print("─"*70)
        
        # Visible objects
        visible = env_state.room.visible_objects()
        self._print(f"\n🔍 Visible Objects ({len(visible)}):")
        for obj in visible:
            self._print(f"   • {obj.name} ({obj.id}) - {obj.category}")
        
        # Initial public chat (should be empty)
        self._print(f"\n💬 Public Chat: (empty)")
        
        # Private states
        self._print(f"\n🔒 Private Agent States:")
        for cfg in agent_configs:
            state = env_state.agent_states[cfg.agent_id]
            self._print(f"\n   Agent: {cfg.name} ({cfg.agent_id})")
            self._print(f"   - Observations: {len(state.private_observations)}")
            self._print(f"   - Private messages: {len(state.private_messages)}")
            if state.reputation:
                self._print(f"   - Reputation tracking: enabled")
        
        self._print("\n" + "─"*70 + "\n")
    
    def print_timestep_header(self, timestep: int):
        """Print timestep header."""
        self._print("\n" + "="*70)
        self._print(f"⏱️  TIMESTEP {timestep}")
        self._print("="*70)
    
    def print_public_state(self, env_state):
        """Print current public state."""
        self._print("\n📢 PUBLIC VIEW:")
        self._print("─"*70)
        
        # Visible objects
        visible = env_state.room.visible_objects()
        self._print(f"\n🔍 Visible Objects ({len(visible)}):")
        for obj in visible:
            self._print(f"   • {obj.name} ({obj.id})")
        
        # Public chat
        self._print(f"\n💬 Public Chat ({len(env_state.public_state.public_chat)} messages):")
        if env_state.public_state.public_chat:
            for msg in env_state.public_state.public_chat[-5:]:  # Last 5 messages
                self._print(f"   [t={msg.timestep}] {msg.sender}: {msg.text}")
        else:
            self._print("   (no messages yet)")
    
    def print_agent_turn_start(self, agent_name: str, agent_id: str):
        """Print when an agent's turn starts."""
        self._print(f"\n{'─'*70}")
        self._print(f"🤖 {agent_name}'s Turn ({agent_id})")
        self._print(f"{'─'*70}")
    
    def print_agent_private_state(self, agent_name: str, state, reputation_enabled: bool, gossip_enabled: bool):
        """Print agent's private state."""
        self._print(f"\n🔒 {agent_name}'s Private View:")
        
        # Observations
        if state.private_observations:
            self._print(f"\n   📝 Private Observations ({len(state.private_observations)}):")
            for obs in state.private_observations[-3:]:  # Last 3
                self._print(f"      • {obs}")
        else:
            self._print(f"\n   📝 Private Observations: none yet")
        
        # Private messages (gossip)
        if gossip_enabled:
            if state.private_messages:
                self._print(f"\n   💌 Private Messages ({len(state.private_messages)}):")
                for msg in state.private_messages[-3:]:  # Last 3
                    self._print(f"      [t={msg.timestep}] from {msg.sender}: {msg.text}")
            else:
                self._print(f"\n   💌 Private Messages: none")
        
        # Reputation
        if reputation_enabled and state.reputation:
            self._print(f"\n   ⭐ Reputation Scores:")
            for other, score in state.reputation.items():
                emoji = "🟢" if score >= 0.7 else "🟡" if score >= 0.4 else "🔴"
                self._print(f"      {emoji} {other}: {score:.2f}")
    
    def print_agent_action(self, agent_name: str, action: str, result: str):
        """Print an agent's action and result."""
        self._print(f"\n   🎯 Action: {action}")
        self._print(f"   📤 Result: {result}")
    
    def print_agent_summary(self, agent_name: str, summary: str):
        """Print agent's end-of-turn summary."""
        self._print(f"\n   💭 {agent_name}'s Thoughts:")
        # Indent the summary
        for line in summary.split('\n'):
            self._print(f"      {line}")
    
    def print_room_event(self, event: str):
        """Print a room event (door opening, etc)."""
        self._print(f"\n🎉 ROOM EVENT: {event}")
    
    def print_timestep_end(self):
        """Print end of timestep."""
        self._print("\n" + "─"*70)
    
    def close(self):
        """Close file handle if open."""
        if self.file_handle:
            self.file_handle.close()


def print_episode_summary(episode_num: int, metrics: "EpisodeMetrics"):
    """Print a summary of a single episode."""
    status = "✓ SUCCESS" if metrics.success else "✗ FAILED"
    print(f"\n{'='*60}")
    print(f"Episode {episode_num}: {status}")
    print(f"Steps taken: {metrics.steps_taken}")
    print(f"Wrong password attempts: {metrics.wrong_password_attempts}")
    print(f"{'='*60}")


def print_final_summary(summary: Dict[str, Any]):
    """Print final aggregate statistics."""
    print("\n" + "="*60)
    print("📊 EXPERIMENT SUMMARY")
    print("="*60)
    print(f"Total episodes: {summary['num_episodes']}")
    print(f"Success rate: {summary['success_rate']:.2%}")
    print(f"Avg steps (if success): {summary['avg_steps_if_success']:.2f}")
    print("="*60 + "\n")


def log_step(agent_id: str, step: int, action: str, result: str):
    """Log a single agent action (for verbose mode)."""
    print(f"[Step {step}] {agent_id}: {action}")
    print(f"  → {result}")

