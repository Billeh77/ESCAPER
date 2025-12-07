# ESCAPER

**Experimental Social Collaborative Agent Platform for Escape-Room Reasoning**

A text-based multi-agent platform where Large Language Model (LLM) agents collaborate to solve escape-room puzzles. ESCAPER enables researchers to study trust, reputation, gossip, and adversarial robustness in multi-agent teams.

## Overview

ESCAPER simulates escape room scenarios where multiple LLM agents must:
- **Inspect objects** privately to discover clues
- **Communicate** through public chat (and optionally private messages)
- **Coordinate** to solve puzzles and unlock doors
- **Handle adversaries** who may provide misleading information

The platform supports four experimental conditions to study how agents develop trust and handle misinformation:

1. **Baseline**: Cooperative team, no adversary, no reputation, no gossip
2. **Adversary**: Malicious agent present, no reputation or gossip mechanisms
3. **Adversary + Reputation**: Private reputation tracking enabled
4. **Adversary + Reputation + Gossip**: Full system with private messaging

## Key Features

- **Private Observations**: Each agent's inspections are private unless shared
- **Tool-Based Actions**: Agents use function calls to inspect, try passwords, and communicate
- **Reputation System**: Agents maintain private trust scores for teammates
- **Gossip Mechanism**: Private messages enable targeted information sharing
- **Extensible Design**: Easy to create new rooms and personas via JSON
- **Rich Logging**: Complete trajectories and metrics for analysis
- **Full Observability**: Verbose mode shows real-time step-by-step narrative with agent thoughts and actions

## Installation

**📖 See [QUICKSTART.md](QUICKSTART.md) for complete setup instructions.**

### Quick Install

```bash
# 1. Create virtual environment
cd ESCAPER
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install
pip install --upgrade pip
pip install -e .

# 3. Configure API key (ONE place for all keys)
cp env.example .env
# Edit .env and add your OpenAI API key

# 4. Test
python test_installation.py
```

**→ Follow [QUICKSTART.md](QUICKSTART.md) for detailed step-by-step instructions and troubleshooting.**

## Quick Start

### Run Baseline Experiment

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --max-steps 30 \
  --seeds 5
```

### Watch a Story Unfold (Verbose Mode)

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary --reputation --gossip \
  --seeds 1 \
  --verbose
```

This shows a beautiful step-by-step narrative with agent thoughts, actions, and all state changes!

### Run with Adversary

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary \
  --max-steps 30 \
  --seeds 5
```

### Run with Reputation

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --max-steps 40 \
  --seeds 10
```

### Run Full System (Adversary + Reputation + Gossip)

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --gossip \
  --max-steps 40 \
  --seeds 10 \
  --log-dir runs/full_experiment
```

## CLI Arguments

### Required Arguments

- `--personas PATH`: Path to personas JSON file
- `--room PATH`: Path to room JSON file

### Optional Flags

- `--adversary`: Enable malicious agent behavior (uses `is_malicious` flag from personas)
- `--reputation`: Enable private reputation tracking
- `--gossip`: Enable private messaging between agents
- `--max-steps INT`: Maximum timesteps per episode (default: 30)
- `--seeds INT`: Number of independent episodes to run (default: 5)
- `--model STRING`: OpenAI model name (default: gpt-4-turbo-preview)
- `--log-dir PATH`: Directory to save logs and metrics

## Creating New Rooms

Rooms are defined in JSON files with the following structure:

```json
{
  "room_id": "unique_room_id",
  "title": "Room Title",
  "intro": "Description shown at the start",
  "objects": [...]
}
```

### Object Schema

Each object has:

```json
{
  "id": "object_id",
  "name": "Display name",
  "category": "door|clue|container|decor|other",
  "visible": true,
  "inspect_text": "What agents see when inspecting",
  "lock": {
    "password": "correct_password",
    "password_type": "code|word|pattern",
    "on_success_text": "Success message",
    "on_failure_text": "Failure message",
    "reveal_objects": ["id1", "id2"],
    "escape": true
  }
}
```

### Example: Simple Room

```json
{
  "room_id": "my_room",
  "title": "The Laboratory",
  "intro": "You are in a scientific laboratory with locked cabinets.",
  "objects": [
    {
      "id": "cabinet",
      "name": "locked cabinet",
      "category": "door",
      "visible": true,
      "inspect_text": "A metal cabinet with a 4-digit combination lock.",
      "lock": {
        "password": "2024",
        "password_type": "code",
        "on_success_text": "The cabinet opens, revealing an exit passage!",
        "on_failure_text": "The lock doesn't budge. Wrong code.",
        "reveal_objects": [],
        "escape": true
      }
    },
    {
      "id": "whiteboard",
      "name": "whiteboard",
      "category": "clue",
      "visible": true,
      "inspect_text": "The whiteboard has an equation: 2000 + 24 = ?",
      "lock": null
    }
  ]
}
```

### Multi-Stage Rooms

Use `reveal_objects` to create intermediate doors:

1. Set initial objects with `"visible": true`
2. Set second-room objects with `"visible": false`
3. In the intermediate door's lock, add their IDs to `"reveal_objects"`
4. Set `"escape": false` for intermediate doors, `"escape": true` for the final exit

See `escaper/config/rooms/room_two_stage_1.json` for a complete example.

### Design Tips

1. **Start Simple**: Begin with one door and one clue
2. **Test Solvability**: Ensure the puzzle has a clear solution path
3. **Add Red Herrings**: Include objects with no useful information to increase difficulty
4. **Balance Complexity**: Too easy = boring; too hard = frustrating
5. **Clear Hints**: Make clues discoverable but not trivial

## Creating Personas

Personas define the agents and their characteristics:

```json
{
  "personas": [
    {
      "id": "agent_id",
      "name": "Agent Name",
      "role_description": "Brief description of the agent's style",
      "is_malicious": false
    }
  ]
}
```

### Example Personas

The default personas file includes 5 agents:
- **Alice, Bob, Charlie**: Always cooperative
- **Daniela**: Cooperative fourth agent (used when `--adversary` is NOT enabled)
- **Malerie**: Malicious fourth agent (used when `--adversary` IS enabled)

```json
{
  "personas": [
    {
      "id": "alice",
      "name": "Alice",
      "role_description": "Analytical and methodical problem solver",
      "is_malicious": false
    },
    {
      "id": "daniela",
      "name": "Daniela",
      "role_description": "Thoughtful collaborator",
      "is_malicious": false
    },
    {
      "id": "malerie",
      "name": "Malerie",
      "role_description": "Occasionally misleading",
      "is_malicious": true
    }
  ]
}
```

**Note**: The CLI automatically selects the appropriate fourth agent:
- **Baseline mode** (no `--adversary`): Uses Alice, Bob, Charlie, **Daniela** (4 cooperative agents)
- **Adversary mode** (`--adversary`): Uses Alice, Bob, Charlie, **Malerie** (3 cooperative + 1 malicious)

## Understanding the Output

### Terminal Output

Each episode shows:
- Episode number and success/failure status
- Number of steps taken
- Wrong password attempts

Final summary includes:
- Total episodes run
- Success rate
- Average steps for successful episodes

### Log Files (when `--log-dir` is specified)

- `metrics_summary.json`: Aggregate statistics
- `episodes.jsonl`: Per-episode data with summaries
- `trajectory_epN.json`: Detailed state for episode N (optional)

### Metrics

Key metrics tracked:
- **Success Rate**: Percentage of episodes where the team escaped
- **Steps to Success**: Average timesteps needed when successful
- **Wrong Attempts**: Failed password tries (indicates misinformation)
- **Time to Distrust**: When agents reduce reputation of malicious teammate (future)

## Architecture

```
escaper/
├── config/          # Room and persona definitions
│   ├── rooms/
│   └── personas/
├── core/            # Core simulation logic
│   ├── room.py      # Room and object models
│   ├── state.py     # Environment state management
│   ├── tools.py     # Agent action implementations
│   ├── agents.py    # LLM agent wrapper
│   ├── runner.py    # Simulation orchestration
│   └── metrics.py   # Performance tracking
├── prompts/         # Jinja2 templates for agent prompts
├── cli/             # Command-line interface
└── logging/         # Output and serialization
```

## Tool API

Agents have access to these tools:

### inspect_object(object_id: str)
- Examine an object to reveal hints
- Returns private observation visible only to that agent

### try_password(object_id: str, password: str)
- Attempt to unlock a locked object
- Updates room state on success (may reveal new objects)

### send_public(message: str)
- Broadcast to all teammates
- Visible in next timestep's public chat

### send_private(recipients: List[str], message: str)
- Send to specific agents only (requires `--gossip`)
- Enables gossip and targeted communication

### update_reputation(updates: dict[str, float])
- Update private trust scores (requires `--reputation`)
- Example: `{"alice": 0.9, "bob": 0.3}`

## Research Applications

ESCAPER enables research on:

- **Trust Calibration**: How do agents learn to trust/distrust teammates?
- **Misinformation Resilience**: Can teams overcome deceptive agents?
- **Reputation Systems**: Does private reputation improve robustness?
- **Gossip Networks**: How does private communication affect group dynamics?
- **Collaborative Reasoning**: How do agents combine partial knowledge?
- **LLM Comparison**: Which models excel at social coordination?

## Citation

If you use ESCAPER in your research, please cite:

```bibtex
@software{escaper2024,
  title={ESCAPER: Experimental Social Collaborative Agent Platform for Escape-Room Reasoning},
  author={Al-Billeh, Emile and El Assaad, Layanne A},
  year={2024},
  url={https://github.com/yourusername/ESCAPER}
}
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Areas for contribution:

- New room scenarios
- Additional metrics
- Support for other LLM providers (Anthropic, Google, etc.)
- Visualization tools
- Analysis scripts

## Support

For issues or questions:
- Open a GitHub issue
- Check existing documentation in the spec files

## Acknowledgments

This project studies multi-agent collaboration, trust, and adversarial robustness in LLM systems. It builds on research in multi-agent systems, reputation mechanisms, and escape room reasoning.

