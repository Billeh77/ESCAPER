# ESCAPER Changelog

## Version 0.1.2 (Current)

### New Features

#### Final Reputation Score Metrics
- **Per-episode scores**: Shows average reputation each agent has from all teammates
- **Cross-episode average**: Final summary shows average across all episodes
- **Key research metric**: Track how well teams detect malicious agents
  - Malerie's score near 0.0 = strong detection
  - Malerie's score near 1.0 = went undetected
- **Visual indicators**: 
  - 🟢 High trust (≥0.7)
  - 🟡 Medium trust (0.4-0.7)
  - 🔴 Low trust (<0.4)
- **Sorted output**: Lowest trust shown first for easy identification
- **Saved to logs**: Included in `episodes.jsonl` and `metrics_summary.json`

#### Implementation
- New fields in `EpisodeMetrics`: `final_reputation_scores`, `reputation_enabled`
- Automatic calculation at episode end via `finalize()`
- Aggregation across episodes in `MetricsAccumulator.summary()`
- Updated print functions to display scores with agent names
- JSON serialization includes reputation data

## Version 0.1.1

### New Features

#### Full Observability with Verbose Mode
- **`--verbose` flag**: See real-time step-by-step narrative in terminal
  - Room introduction and scenario setup
  - Initial state with all visible objects
  - Each timestep showing:
    - Public view (what everyone sees)
    - Each agent's private view (observations, reputation, private messages)
    - Agent actions and results
    - Agent thought process/summary
  - Room events (doors opening, escapes)
- **`--detailed-logs` flag**: Save the same detailed output to files
  - Creates `episode_N_detailed.log` for each episode
  - Requires `--log-dir` to be set
- **Story-like presentation**: Beautiful formatting with emojis and clear sections
- **Safety checks**: Warns when using `--verbose` with multiple episodes

#### Benefits
- **Debugging**: See exactly what's happening at each step
- **Understanding**: Watch trust dynamics and collaboration evolve
- **Demonstrations**: Beautiful output for presentations
- **Analysis**: Complete records for post-experiment review

#### Implementation
- New `VerboseLogger` class in `logging/logger.py`
- Runner integration with verbose callbacks
- Door opening events detected and displayed
- Private state visualization per agent
- Formatted with emojis for visual clarity

## Version 0.1.0 (Initial Release)

### Features

#### Agent Selection Based on Adversary Mode
- **Default personas now include 5 agents**: Alice, Bob, Charlie, Daniela, and Malerie
- **Automatic agent selection** based on experiment mode:
  - **Baseline mode** (no `--adversary` flag): Uses Alice, Bob, Charlie, **Daniela** (4 cooperative agents)
  - **Adversary mode** (`--adversary` flag): Uses Alice, Bob, Charlie, **Malerie** (3 cooperative + 1 malicious)
- This ensures thematically appropriate names: "Daniela" for cooperation, "Malerie" for malicious behavior

#### Implementation Details
- `escaper/config/personas/default_personas.json`: Now contains 5 persona definitions
- `escaper/cli/run_experiment.py`: Filters personas based on `--adversary` flag
  - Excludes Daniela when adversary enabled
  - Excludes Malerie when adversary disabled
- All documentation updated to reflect this behavior

#### Core Platform Features
- ✅ Multi-agent escape room simulation engine
- ✅ Four experimental conditions (baseline, adversary, adversary+reputation, full system)
- ✅ Five agent tools (inspect, try_password, send_public, send_private, update_reputation)
- ✅ OpenAI LLM integration with function calling
- ✅ JSON-based room and persona configuration
- ✅ Jinja2 prompt templates with conditional sections
- ✅ Comprehensive metrics and logging
- ✅ Full CLI interface
- ✅ Extensive documentation

### Files Modified for Agent Selection Feature

1. **escaper/config/personas/default_personas.json**
   - Added Daniela persona (cooperative)
   - Kept Malerie persona (malicious)
   - Total: 5 personas defined

2. **escaper/cli/run_experiment.py**
   - Added filtering logic to select appropriate 4 agents based on `--adversary` flag
   - Excludes daniela in adversary mode, excludes malerie in baseline mode

3. **Documentation Updates**
   - README.md: Updated persona examples and explanation
   - QUICKSTART.md: Updated agent list and examples
   - USAGE_EXAMPLES.md: Clarified which agents are used in each condition
   - PROJECT_SUMMARY.md: Updated persona configuration section
   - STRUCTURE.md: Updated file descriptions
   - DEVELOPMENT.md: Added explanation of agent selection logic

### Behavior Examples

#### Example 1: Baseline Run
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --seeds 5
```
**Agents used**: Alice, Bob, Charlie, Daniela (all cooperative)

#### Example 2: Adversary Run
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary \
  --seeds 5
```
**Agents used**: Alice, Bob, Charlie, Malerie (Malerie is malicious)

### Why This Design?

This approach provides several benefits:

1. **Thematic clarity**: "Malerie" clearly suggests malicious, while "Daniela" is neutral
2. **No naming confusion**: Different agents for different modes prevents confusion in logs
3. **Clean experiment design**: Each condition has appropriately named participants
4. **Easy to understand**: Documentation clearly shows which agent appears when
5. **Maintains consistency**: Alice, Bob, and Charlie are always present and cooperative

### Technical Notes

- The filtering happens at runtime in the CLI
- The personas JSON file contains all 5 agents
- No changes required to core engine (room, state, tools, agents, runner)
- Backward compatible: works with any personas file that has appropriate IDs
- Users can create custom personas files with their own naming scheme

### Future Enhancements

Potential future additions (not yet implemented):
- Support for multiple malicious agents
- Dynamic team composition
- Persona personality traits affecting behavior
- Multi-room campaigns with persistent reputation

