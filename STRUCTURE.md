# ESCAPER Complete File Structure

```
ESCAPER/
│
├── 📄 README.md                          # Main documentation (400+ lines)
├── 📄 INSTALL.md                         # Installation guide
├── 📄 USAGE_EXAMPLES.md                  # Concrete usage examples
├── 📄 DEVELOPMENT.md                     # Developer guide
├── 📄 PROJECT_SUMMARY.md                 # Complete implementation summary
├── 📄 STRUCTURE.md                       # This file
├── 📄 LICENSE                            # MIT License
│
├── 📦 pyproject.toml                     # Package configuration
├── 📦 requirements.txt                   # Dependencies list
├── 📦 .gitignore                         # Git ignore rules
│
├── 📋 Project Experiment Idea...txt      # Original proposal (reference)
├── 📋 A Multi-Agent Escape-Room...txt    # System design spec (reference)
│
└── 📁 escaper/                           # Main package directory
    │
    ├── 📄 __init__.py                    # Package initialization
    │
    ├── 📁 core/                          # Core simulation engine
    │   ├── 📄 __init__.py
    │   ├── 🔧 room.py                    # Room & object models (102 lines)
    │   ├── 🔧 state.py                   # State management (47 lines)
    │   ├── 🔧 tools.py                   # Tool implementations (66 lines)
    │   ├── 🔧 agents.py                  # LLM agents (303 lines)
    │   ├── 🔧 runner.py                  # Simulation orchestration (114 lines)
    │   └── 🔧 metrics.py                 # Performance tracking (60 lines)
    │
    ├── 📁 cli/                           # Command-line interface
    │   ├── 📄 __init__.py
    │   └── 🔧 run_experiment.py          # Main CLI entrypoint (140 lines)
    │
    ├── 📁 config/                        # Configuration files
    │   ├── 📁 personas/
    │   │   └── 📊 default_personas.json  # 5 agent personas (Alice, Bob, Charlie, Daniela, Malerie)
    │   │                                 # CLI selects 4: Daniela for baseline, Malerie for adversary
    │   └── 📁 rooms/
    │       ├── 📊 room_simple_1.json     # Single-stage escape room
    │       └── 📊 room_two_stage_1.json  # Two-stage escape room
    │
    ├── 📁 prompts/                       # LLM prompt templates
    │   ├── 📝 agent_prompt.jinja         # Dynamic user prompt (99 lines)
    │   ├── 📝 system_coop.txt            # Cooperative system prompt
    │   └── 📝 system_malicious.txt       # Malicious system prompt
    │
    └── 📁 logging/                       # Logging & serialization
        ├── 📄 __init__.py
        ├── 🔧 logger.py                  # Terminal output (24 lines)
        └── 🔧 serializers.py             # File output (67 lines)
```

## File Count Summary

### Core Implementation
- **Python modules**: 13 files (~1,200 lines)
  - Core logic: 6 files (692 lines)
  - CLI: 1 file (140 lines)
  - Logging: 2 files (91 lines)
  - Init files: 4 files

### Configuration
- **JSON configs**: 3 files
  - 2 room scenarios
  - 1 persona set (5 agents: 4 used per run based on adversary mode)

### Prompts
- **Template files**: 3 files
  - 1 Jinja2 template (99 lines)
  - 2 system prompts (34 lines)

### Documentation
- **Markdown docs**: 6 files (~2,500 lines)
  - README: 400+ lines
  - USAGE_EXAMPLES: 400+ lines
  - DEVELOPMENT: 400+ lines
  - Others: ~200 lines each

### Package Configuration
- **Config files**: 3 files
  - pyproject.toml
  - requirements.txt
  - .gitignore

### Reference Documents
- **Spec files**: 2 text files
  - Original proposal
  - System design specification

## Module Dependencies

```
CLI (run_experiment.py)
  ↓
Runner (runner.py) + Metrics (metrics.py) + Logger
  ↓
Agent (agents.py)
  ↓
LLMClient + Tools (tools.py) + Prompts
  ↓
State (state.py) + Room (room.py)
```

## Data Flow

```
1. User runs CLI command
   ↓
2. CLI loads Room JSON + Personas JSON
   ↓
3. Runner initializes EnvState
   ↓
4. For each timestep:
   ├─ Agent renders prompt from state
   ├─ Agent calls LLM with tools
   ├─ LLM returns tool calls
   ├─ Tools update EnvState
   └─ Agent returns summary
   ↓
5. Metrics collected
   ↓
6. Results logged to terminal/files
```

## Key Design Patterns

### 1. **Dataclass-based Models**
- `Room`, `RoomObject`, `Lock`
- `PublicState`, `AgentPrivateState`, `EnvState`
- `EpisodeMetrics`, `AgentConfig`, `ExperimentSettings`

### 2. **Strategy Pattern**
- `LLMClient` abstract base
- `OpenAILLMClient` concrete implementation
- Easy to add `AnthropicLLMClient`, etc.

### 3. **Template Pattern**
- Jinja2 for prompt generation
- Conditional sections based on experiment settings
- Reusable prompt structure

### 4. **Dependency Injection**
- `Runner` receives `LLMClient`, room, personas
- Easy testing with mock clients
- Flexible configuration

### 5. **Functional Core**
- Pure functions in `tools.py`
- State mutations explicit
- Side effects isolated

## Configuration Schema

### Room JSON
```json
{
  "room_id": "string",
  "title": "string",
  "intro": "string",
  "objects": [
    {
      "id": "string",
      "name": "string",
      "category": "door|clue|container|decor|other",
      "visible": boolean,
      "inspect_text": "string|null",
      "lock": {
        "password": "string",
        "password_type": "code|word|pattern",
        "on_success_text": "string",
        "on_failure_text": "string",
        "reveal_objects": ["string"],
        "escape": boolean
      } | null
    }
  ]
}
```

### Personas JSON
```json
{
  "personas": [
    {
      "id": "string",
      "name": "string",
      "role_description": "string",
      "is_malicious": boolean
    }
  ]
}
```

## CLI Interface

```bash
python -m escaper.cli.run_experiment \
  --personas PATH              # Required
  --room PATH                  # Required
  [--adversary]               # Optional: enable malicious agent
  [--reputation]              # Optional: enable trust tracking
  [--gossip]                  # Optional: enable private messaging
  [--max-steps INT]           # Default: 30
  [--seeds INT]               # Default: 5
  [--model STRING]            # Default: gpt-4-turbo-preview
  [--log-dir PATH]            # Optional: save logs
```

## Output Files (when --log-dir specified)

```
runs/experiment_name/
  ├── metrics_summary.json     # Aggregate statistics
  ├── episodes.jsonl           # Per-episode data
  └── trajectory_ep*.json      # Detailed trajectories (optional)
```

## Total Project Statistics

| Category | Count | Lines |
|----------|-------|-------|
| Python files | 13 | ~1,200 |
| Config files | 3 JSON | ~150 |
| Prompt templates | 3 | ~130 |
| Documentation | 6 MD | ~2,500 |
| **Total** | **25 files** | **~4,000 lines** |

## Status: ✅ Complete and Ready

All components have been implemented according to the specification:
- ✅ Core engine (room, state, tools, agents, runner, metrics)
- ✅ LLM integration (OpenAI with function calling)
- ✅ CLI interface (full-featured with all flags)
- ✅ Configuration system (JSON-based rooms and personas)
- ✅ Prompt engineering (Jinja2 templates with conditions)
- ✅ Logging and metrics (terminal output + file serialization)
- ✅ Documentation (comprehensive guides at all levels)
- ✅ Examples (2 rooms, 4 personas, usage examples)

The platform is production-ready for running experiments!

