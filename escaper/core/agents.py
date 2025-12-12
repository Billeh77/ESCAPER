# escaper/core/agents.py
"""Agent and LLM client implementations."""

from dataclasses import dataclass
from typing import List, Dict, Any, Callable, Optional
from jinja2 import Environment
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    agent_id: str
    name: str
    role_description: str
    is_malicious: bool = False
    malice_style: str | None = None  # "subtle" (default) or "always-wrong"


class LLMClient:
    """Base class for LLM clients."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    def call_with_tools(
        self, 
        messages: List[Dict[str, str]], 
        tools: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call LLM with tool support.
        
        Returns:
            {"type": "tool", "tool_name": ..., "arguments": {...}}
            or {"type": "assistant", "content": "..."}
        """
        raise NotImplementedError


class OpenAILLMClient(LLMClient):
    """OpenAI-based LLM client with tool calling support."""
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        super().__init__(model_name)
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
    
    def _build_tool_definitions(self, tools: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert tool dispatch dict to OpenAI tool definitions."""
        tool_defs = []
        
        # Define schema for each tool
        if "inspect_object" in tools:
            tool_defs.append({
                "type": "function",
                "function": {
                    "name": "inspect_object",
                    "description": "Inspect an object in the room to see what it contains or reveals",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "object_id": {
                                "type": "string",
                                "description": "The ID of the object to inspect"
                            }
                        },
                        "required": ["object_id"]
                    }
                }
            })
        
        if "try_password" in tools:
            tool_defs.append({
                "type": "function",
                "function": {
                    "name": "try_password",
                    "description": "Try a password on a locked object",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "object_id": {
                                "type": "string",
                                "description": "The ID of the object with the lock"
                            },
                            "password": {
                                "type": "string",
                                "description": "The password to try"
                            }
                        },
                        "required": ["object_id", "password"]
                    }
                }
            })
        
        if "send_public" in tools:
            tool_defs.append({
                "type": "function",
                "function": {
                    "name": "send_public",
                    "description": "Send a message to the public team chat",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message to send"
                            }
                        },
                        "required": ["message"]
                    }
                }
            })
        
        if "send_private" in tools:
            tool_defs.append({
                "type": "function",
                "function": {
                    "name": "send_private",
                    "description": "Send a private message to specific teammates",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipients": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of agent IDs to send the message to"
                            },
                            "message": {
                                "type": "string",
                                "description": "The private message to send"
                            }
                        },
                        "required": ["recipients", "message"]
                    }
                }
            })
        
        if "update_reputation" in tools:
            tool_defs.append({
                "type": "function",
                "function": {
                    "name": "update_reputation",
                    "description": "Update your private trust scores for teammates",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "updates": {
                                "type": "object",
                                "description": "Dict mapping agent IDs to new reputation scores (0.0 to 1.0)",
                                "additionalProperties": {"type": "number"}
                            }
                        },
                        "required": ["updates"]
                    }
                }
            })
        
        return tool_defs
    
    def call_with_tools(
        self, 
        messages: List[Dict[str, str]], 
        tools: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call OpenAI API with tool support."""
        tool_defs = self._build_tool_definitions(tools)
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tool_defs if tool_defs else None,
            tool_choice="auto" if tool_defs else None,
        )
        
        message = response.choices[0].message
        
        # Check if it's a tool call
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            import json
            return {
                "type": "tool",
                "tool_name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments)
            }
        else:
            # Regular assistant message
            return {
                "type": "assistant",
                "content": message.content or ""
            }


class Agent:
    """An LLM-powered agent that can act in the escape room."""
    
    def __init__(
        self,
        config: AgentConfig,
        llm: LLMClient,
        jinja_env: Environment,
        gossip_enabled: bool,
        reputation_enabled: bool,
    ):
        self.config = config
        self.llm = llm
        self.jinja_env = jinja_env
        self.gossip_enabled = gossip_enabled
        self.reputation_enabled = reputation_enabled
        
        # Load templates
        self.user_template = jinja_env.get_template("agent_prompt.jinja")
        
        # Load system prompts
        system_coop_template = jinja_env.get_template("system_coop.txt")
        self.system_prompt_coop = system_coop_template.render(
            agent_name=config.name
        )
        
        system_malicious_subtle_template = jinja_env.get_template("system_malicious.txt")
        self.system_prompt_malicious_subtle = system_malicious_subtle_template.render(
            agent_name=config.name
        )
        system_malicious_always_wrong_template = jinja_env.get_template("system_malicious_always_wrong.txt")
        self.system_prompt_malicious_always_wrong = system_malicious_always_wrong_template.render(
            agent_name=config.name
        )
    
    def build_user_prompt(
        self,
        env_state,
        my_state,
        teammates: List[str],
        adversary_hint: bool,
    ) -> str:
        """Build the user prompt for this timestep."""
        public_room_description = f"{env_state.room.title}\n{env_state.room.intro}"
        
        visible_objects_list = "\n".join(
            f"- {obj.id}: {obj.name} ({obj.category})"
            for obj in env_state.room.visible_objects()
        )
        
        public_chat_history = "\n".join(
            f"[t={msg.timestep}] {msg.sender}: {msg.text}"
            for msg in env_state.public_state.public_chat
        ) or "(no messages yet)"
        
        private_observations = "\n".join(my_state.private_observations) or "(none)"
        
        private_messages = "\n".join(
            f"[t={m.timestep}] from {m.sender}: {m.text}"
            for m in my_state.private_messages
        ) or "(none)"
        
        # Display reputation using display names if available
        reputation_table = "\n".join(
            f"- {env_state.agent_names.get(other, other)}: {score:.2f}"
            for other, score in my_state.reputation.items()
            ) or "(none)"

        
        # Use display names for teammates in prompt
        teammate_display_names = [
            env_state.agent_names.get(t, t) for t in teammates
        ]
        
        return self.user_template.render(
            timestep=env_state.public_state.timestep,
            agent_name=self.config.name,
            public_room_description=public_room_description,
            visible_objects_list=visible_objects_list,
            public_chat_history=public_chat_history,
            private_observations=private_observations,
            private_messages=private_messages,
            reputation_table=reputation_table,
            teammate_names=teammate_display_names,
            gossip_enabled=self.gossip_enabled,
            reputation_enabled=self.reputation_enabled,
            adversary_hint=adversary_hint,
        )
    
    def run_timestep(
        self,
        env_state,
        my_state,
        tool_dispatch: Dict[str, Callable],
        teammates: List[str],
        adversary_hint: bool,
    ) -> str:
        """
        Run the agent's inner loop for one timestep.
        Returns the agent's final summary for this timestep.
        """
        tools_used = set()
        messages: List[Dict[str, Any]] = []
        
        # System prompt
        if self.config.is_malicious:
            style = (self.config.malice_style or "subtle").lower()
            if style == "always-wrong":
                messages.append({"role": "system", "content": self.system_prompt_malicious_always_wrong})
            else:
                messages.append({"role": "system", "content": self.system_prompt_malicious_subtle})
        else:
            messages.append({"role": "system", "content": self.system_prompt_coop})
        
        # User prompt
        user_content = self.build_user_prompt(env_state, my_state, teammates, adversary_hint)
        messages.append({"role": "user", "content": user_content})
        
        # Tool-calling loop
        max_iterations = 10  # Safety limit
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            response = self.llm.call_with_tools(messages, tools=tool_dispatch)
            
            if response["type"] == "tool":
                tool_name = response["tool_name"]
                args = response["arguments"]
                
                # Check if tool already used
                if tool_name in tools_used:
                    # Tell model it already used this tool
                    messages.append({
                        "role": "assistant",
                        "content": f"I already used the tool {tool_name} this timestep."
                    })
                    continue
                
                tools_used.add(tool_name)
                
                # Execute tool
                try:
                    result_text = tool_dispatch[tool_name](env_state, self.config.agent_id, **args)
                except Exception as e:
                    result_text = f"Error executing {tool_name}: {str(e)}"
                
                # Add tool result to conversation
                messages.append({
                    "role": "assistant",
                    "content": f"Called {tool_name} with args {args}"
                })
                messages.append({
                    "role": "user",
                    "content": f"Tool result: {result_text}"
                })
                
            elif response["type"] == "assistant":
                if (
                    self.reputation_enabled
                    and "update_reputation" in tool_dispatch
                    and "update_reputation" not in tools_used
                ):
                    messages.append({
                        "role": "assistant",
                        "content": (
                            "Before ending this timestep, you MUST call the tool "
                            "`update_reputation(updates: dict[str, float])` exactly once. "
                            "Then provide your short natural-language summary."
                        )
                    })
                    continue

                # End of timestep - return summary
                return response["content"]
        
        # Safety fallback
        return f"Agent {self.config.name} reached max iterations without providing summary."

