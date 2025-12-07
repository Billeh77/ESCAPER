# Development Guide

This guide is for researchers and developers who want to extend or modify ESCAPER.

## Architecture Overview

ESCAPER follows a modular design with clear separation of concerns:

```
Core simulation flow:
CLI → Runner → Agent → LLM → Tools → State → Room
       ↓
    Metrics → Logger → Serializer
```

### Key Components

1. **Room** (`core/room.py`): Defines the escape room environment
2. **State** (`core/state.py`): Manages public and private agent state
3. **Tools** (`core/tools.py`): Implements agent actions
4. **Agents** (`core/agents.py`): LLM wrapper with tool-calling loop
5. **Runner** (`core/runner.py`): Orchestrates episodes and experiments
6. **Metrics** (`core/metrics.py`): Tracks performance
7. **CLI** (`cli/run_experiment.py`): Command-line interface

## Adding New Features

### Adding a New Tool

1. **Define the tool function in `core/tools.py`:**

```python
def my_new_tool(env: EnvState, agent_id: str, param1: str) -> str:
    # Implement tool logic
    # Update env state as needed
    return "Tool result message"
```

2. **Add to tool dispatch:**

```python
def get_tool_dispatch(gossip_enabled: bool, reputation_enabled: bool, my_tool_enabled: bool):
    dispatch = {
        "inspect_object": inspect_object,
        "try_password": try_password,
        "send_public": send_public,
    }
    if gossip_enabled:
        dispatch["send_private"] = send_private
    if reputation_enabled:
        dispatch["update_reputation"] = update_reputation
    if my_tool_enabled:
        dispatch["my_new_tool"] = my_new_tool
    return dispatch
```

3. **Add tool schema in `core/agents.py`:**

```python
def _build_tool_definitions(self, tools: Dict[str, Any]) -> List[Dict[str, Any]]:
    tool_defs = []
    # ... existing tools ...
    
    if "my_new_tool" in tools:
        tool_defs.append({
            "type": "function",
            "function": {
                "name": "my_new_tool",
                "description": "What this tool does",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Description of param1"
                        }
                    },
                    "required": ["param1"]
                }
            }
        })
    
    return tool_defs
```

4. **Update prompt template** (`prompts/agent_prompt.jinja`):

```jinja
{% if my_tool_enabled %}
- `my_new_tool(param1: str)`
  - Description of what it does
{% endif %}
```

5. **Add CLI flag** (`cli/run_experiment.py`):

```python
parser.add_argument(
    "--my-tool",
    action="store_true",
    help="Enable my new tool"
)
```

### Adding Support for New LLM Providers

Currently, ESCAPER uses OpenAI. To add another provider:

1. **Create a new client class in `core/agents.py`:**

```python
class AnthropicLLMClient(LLMClient):
    def __init__(self, model_name: str = "claude-3-opus-20240229"):
        super().__init__(model_name)
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    def _build_tool_definitions(self, tools: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Convert to Anthropic's tool format
        pass
    
    def call_with_tools(self, messages: List[Dict[str, str]], tools: Dict[str, Any]) -> Dict[str, Any]:
        # Call Anthropic API
        # Parse response
        # Return standardized format
        pass
```

2. **Update CLI to support provider selection:**

```python
parser.add_argument(
    "--provider",
    choices=["openai", "anthropic"],
    default="openai",
    help="LLM provider to use"
)

# In main():
if args.provider == "openai":
    llm = OpenAILLMClient(model_name=args.model)
elif args.provider == "anthropic":
    llm = AnthropicLLMClient(model_name=args.model)
```

### Adding New Metrics

1. **Extend `EpisodeMetrics` in `core/metrics.py`:**

```python
@dataclass
class EpisodeMetrics:
    summaries: List[str] = field(default_factory=list)
    success: bool = False
    steps_taken: int = 0
    wrong_password_attempts: int = 0
    # New metrics:
    time_to_distrust: Optional[int] = None
    collaboration_score: float = 0.0
    
    def compute_collaboration_score(self, env_state):
        # Analyze public chat to measure collaboration
        pass
```

2. **Update `MetricsAccumulator.summary()`:**

```python
def summary(self) -> dict:
    # ... existing metrics ...
    
    avg_time_to_distrust = (
        sum(e.time_to_distrust for e in self.episodes if e.time_to_distrust)
        / sum(1 for e in self.episodes if e.time_to_distrust)
        if any(e.time_to_distrust for e in self.episodes)
        else None
    )
    
    return {
        # ... existing fields ...
        "avg_time_to_distrust": avg_time_to_distrust,
    }
```

3. **Log metrics during episode** in `runner.py`:

```python
def run_episode(self, seed: int) -> EpisodeMetrics:
    # ... existing code ...
    
    # Track when agents first distrust adversary
    if self.settings.reputation_enabled:
        for agent_id, state in env_state.agent_states.items():
            if not self._persona_is_malicious(agent_id):
                malicious_id = self._get_malicious_agent_id()
                if state.reputation.get(malicious_id, 1.0) < 0.5:
                    if metrics.time_to_distrust is None:
                        metrics.time_to_distrust = step
```

### Creating Analysis Tools

Create analysis scripts in a new `analysis/` directory:

```python
# analysis/compare_conditions.py
import json
import sys
from pathlib import Path

def compare_conditions(baseline_dir, experimental_dir):
    with open(f"{baseline_dir}/metrics_summary.json") as f:
        baseline = json.load(f)
    
    with open(f"{experimental_dir}/metrics_summary.json") as f:
        experimental = json.load(f)
    
    print("Comparison:")
    print(f"Success rate change: {experimental['success_rate'] - baseline['success_rate']:.2%}")
    print(f"Steps change: {experimental['avg_steps_if_success'] - baseline['avg_steps_if_success']:.2f}")

if __name__ == "__main__":
    compare_conditions(sys.argv[1], sys.argv[2])
```

## Testing

### Unit Tests

Create tests in `tests/` directory:

```python
# tests/test_room.py
from escaper.core.room import Room

def test_room_loading():
    room = Room.from_json("escaper/config/rooms/room_simple_1.json")
    assert room.room_id == "room_simple_1"
    assert len(room.objects) == 2

def test_password_correct():
    room = Room.from_json("escaper/config/rooms/room_simple_1.json")
    result = room.try_password("door_main", "419")
    assert "escaped" in result.lower()
    assert room.escaped

def test_password_incorrect():
    room = Room.from_json("escaper/config/rooms/room_simple_1.json")
    result = room.try_password("door_main", "000")
    assert "incorrect" in result.lower()
    assert not room.escaped
```

Run tests:
```bash
pytest tests/
```

### Integration Tests

```python
# tests/test_integration.py
from escaper.core.runner import SimulationRunner, ExperimentSettings
from escaper.core.room import Room
from escaper.core.agents import AgentConfig, OpenAILLMClient

def test_baseline_run():
    room = Room.from_json("escaper/config/rooms/room_simple_1.json")
    personas = [
        AgentConfig("alice", "Alice", "", False),
        AgentConfig("bob", "Bob", "", False),
    ]
    settings = ExperimentSettings(False, False, False, 30)
    
    # Mock LLM client for testing
    llm = MockLLMClient()
    
    runner = SimulationRunner(room, personas, settings, llm, jinja_env)
    metrics = runner.run_episode(0)
    
    assert metrics.steps_taken > 0
```

## Code Style

Follow PEP 8 conventions. Use `black` for formatting:

```bash
black escaper/
```

### Type Hints

Use type hints throughout:

```python
from typing import List, Dict, Optional

def process_messages(messages: List[Dict[str, str]]) -> Optional[str]:
    if not messages:
        return None
    return messages[-1]["content"]
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def inspect_object(env: EnvState, agent_id: str, object_id: str) -> str:
    """Inspect an object and record the observation.
    
    Args:
        env: Current environment state
        agent_id: ID of the agent performing inspection
        object_id: ID of the object to inspect
    
    Returns:
        Text description of what the agent observes
    
    Raises:
        ValueError: If object_id doesn't exist
    """
    pass
```

### Comments

Comment complex logic:

```python
# Track reputation changes over time to detect when agents
# first identify the malicious teammate
if reputation_changed and reputation < DISTRUST_THRESHOLD:
    metrics.time_to_distrust = current_step
```

## Performance Considerations

### Reducing LLM Costs

1. **Use cheaper models for development:**
   ```python
   llm = OpenAILLMClient(model_name="gpt-3.5-turbo")
   ```

2. **Implement response caching** (for deterministic scenarios)

3. **Batch experiments efficiently**

### Optimizing Runtime

1. **Parallel episode execution:**
   ```python
   from concurrent.futures import ProcessPoolExecutor
   
   with ProcessPoolExecutor(max_workers=4) as executor:
       futures = [executor.submit(runner.run_episode, seed) for seed in seeds]
       results = [f.result() for f in futures]
   ```

2. **Reduce prompt size** by summarizing chat history

## Debugging

### Verbose Logging

Add a `--verbose` flag:

```python
# In runner.py
if self.verbose:
    print(f"[Step {step}] {agent_id} calling {tool_name}")
```

### Inspecting LLM Calls

Log raw LLM requests/responses:

```python
# In agents.py
if os.environ.get("DEBUG_LLM"):
    with open("llm_debug.log", "a") as f:
        f.write(f"Messages: {messages}\n")
        f.write(f"Response: {response}\n\n")
```

### Trajectory Visualization

Create a visualization tool:

```python
# analysis/visualize_trajectory.py
import json
import matplotlib.pyplot as plt

def visualize_trajectory(trajectory_file):
    with open(trajectory_file) as f:
        data = json.load(f)
    
    # Plot reputation over time
    # Plot message counts
    # etc.
```

## Contributing Guidelines

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/my-feature`
3. **Write tests** for new functionality
4. **Ensure all tests pass:** `pytest tests/`
5. **Format code:** `black escaper/`
6. **Update documentation**
7. **Submit a pull request**

### PR Checklist

- [ ] Code follows PEP 8 style
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)

## Common Extensions

### Important: Agent Selection Logic

The default personas file contains 5 agents, but only 4 are used per run:
- **Baseline mode** (no `--adversary`): Alice, Bob, Charlie, **Daniela**
- **Adversary mode** (`--adversary`): Alice, Bob, Charlie, **Malerie**

This is implemented in `cli/run_experiment.py`:
```python
if args.adversary:
    personas = [p for p in all_personas if p.agent_id != "daniela"]
else:
    personas = [p for p in all_personas if p.agent_id != "malerie"]
```

### 1. Multi-Room Sequences

Extend runner to chain multiple rooms:

```python
class CampaignRunner:
    def run_campaign(self, rooms: List[Room]):
        # Run rooms in sequence
        # Carry reputation across rooms
        pass
```

### 2. Human-in-the-Loop

Add option for human agents:

```python
class HumanAgent(Agent):
    def run_timestep(self, ...):
        # Display state to human
        # Get input via CLI or web interface
        pass
```

### 3. Visualization Dashboard

Create a web dashboard:
- Real-time episode monitoring
- Interactive trajectory replay
- Aggregate statistics visualization

### 4. Benchmark Suite

Create standardized benchmark:
- Suite of rooms with varying difficulty
- Standard evaluation protocol
- Leaderboard for different LLMs

## Resources

- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
- **Jinja2 Docs**: https://jinja.palletsprojects.com/
- **Multi-Agent Systems**: Papers on MAS coordination and trust

## Getting Help

- Check existing issues on GitHub
- Review the spec document
- Read through example code in `escaper/core/`
- Join discussions (if community exists)

