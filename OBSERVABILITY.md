# ESCAPER Observability Guide

## Overview

ESCAPER provides three levels of observability to suit different needs:

1. **Verbose Mode** (`--verbose`) - Real-time narrative in terminal
2. **Detailed Logs** (`--detailed-logs`) - Same narrative saved to files
3. **Default Mode** - Minimal output for large-scale experiments

---

## Verbose Mode (`--verbose`)

### What You See

When you run with `--verbose`, ESCAPER transforms into a story that unfolds before your eyes:

#### 1. Story Introduction
```
==================================================================
🏠 ESCAPE ROOM SCENARIO
==================================================================

📍 Location: The Study

You are in a small study with a locked wooden door and a single painting.

👥 Your Team:
   • Alice
   • Bob
   • Charlie
   • Malerie

==================================================================

🎬 The scenario begins...
```

#### 2. Initial Room State
- 🔍 All visible objects
- 💬 Public chat (initially empty)
- 🔒 Each agent's private state

#### 3. Each Timestep Shows:

**Public View** (what everyone sees):
- Visible objects
- Recent public chat messages

**Each Agent's Turn**:
- 🤖 Agent name and ID
- 🔒 Their private observations
- 💌 Their private messages (if gossip enabled)
- ⭐ Their reputation scores (if reputation enabled)
- 🎯 Their actions
- 📤 Action results
- 💭 Their thought process/summary

#### 4. Room Events
- 🎉 Doors opening and revealing new areas
- 🎉 Successful escape

### Example Command

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary --reputation --gossip \
  --seeds 1 \
  --verbose
```

### When to Use

- ✅ **Single episode runs** - See the full story
- ✅ **Debugging** - Understand what's happening
- ✅ **Demonstrations** - Beautiful output for presentations
- ✅ **Learning** - See how agents think and collaborate
- ✅ **Trust dynamics** - Watch reputation evolve in real-time
- ❌ **Multiple episodes** - Too much output (use detailed-logs instead)

---

## Detailed Logs Mode (`--detailed-logs`)

### What It Does

Saves the exact same output as verbose mode to files, one per episode.

### Example Command

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary --reputation --gossip \
  --seeds 10 \
  --log-dir runs/my_experiment \
  --detailed-logs
```

### Output Files

Creates in your `--log-dir`:
- `episode_0_detailed.log` - Full narrative for episode 0
- `episode_1_detailed.log` - Full narrative for episode 1
- ... (one per seed)
- `metrics_summary.json` - Aggregate statistics
- `episodes.jsonl` - Per-episode metrics

### When to Use

- ✅ **Multiple episodes** - Keep complete records without terminal spam
- ✅ **Post-experiment analysis** - Review specific episodes later
- ✅ **Finding interesting cases** - Read logs to find notable behavior
- ✅ **Research records** - Complete audit trail
- ❌ **Real-time viewing** - Use verbose for that

---

## Default Mode (No Flags)

### What You See

Minimal, clean output:
```
Episode 0: ✓ SUCCESS
Steps taken: 12
Wrong password attempts: 0

Episode 1: ✓ SUCCESS
Steps taken: 14
Wrong password attempts: 1

...

📊 EXPERIMENT SUMMARY
Total episodes: 10
Success rate: 80.00%
Avg steps (if success): 13.50
```

### When to Use

- ✅ **Large-scale experiments** (many episodes/seeds)
- ✅ **Statistical analysis** - Clean results only
- ✅ **Quick checks** - Fast feedback
- ✅ **Production runs** - Minimal distraction

---

## Emoji Guide

Understanding the verbose output:

- 🏠 Room/scenario information
- 📍 Location
- 👥 Team members
- 🎬 Story events
- ⏱️ Timestep marker
- 📢 Public view
- 🔍 Visible objects
- 💬 Public chat
- 🤖 Agent turn
- 🔒 Private information
- 📝 Private observations
- 💌 Private messages (gossip)
- ⭐ Reputation scores
  - 🟢 High trust (≥0.7)
  - 🟡 Medium trust (0.4-0.7)
  - 🔴 Low trust (<0.4)
- 🎯 Action taken
- 📤 Action result
- 💭 Agent thoughts/summary
- 🎉 Room events (success, doors opening)
- ✓ Success
- ✗ Failure

---

## Combining with Other Flags

### Verbose + All Features
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --gossip \
  --max-steps 50 \
  --seeds 1 \
  --verbose
```

Shows everything: adversary behavior, reputation updates, private gossip!

### Detailed Logs + Multiple Conditions
```bash
# Run all 4 conditions with detailed logs
for condition in baseline adversary adv_rep adv_rep_gossip; do
  python -m escaper.cli.run_experiment \
    --personas escaper/config/personas/default_personas.json \
    --room escaper/config/rooms/room_two_stage_1.json \
    --adversary \
    --reputation \
    --gossip \
    --seeds 10 \
    --log-dir runs/$condition \
    --detailed-logs
done
```

---

## Tips and Best Practices

### For Verbose Mode

1. **Use with single episodes**: `--seeds 1`
2. **Pipe to less for navigation**: `... | less -R`
3. **Save to file**: `... > my_run.log 2>&1`
4. **Use smaller rooms** first to see complete stories

### For Detailed Logs

1. **Always specify log-dir**: Required for this mode
2. **Organize by experiment**: Use descriptive log-dir names
3. **Review interesting episodes**: Check logs for notable behaviors
4. **Grep for patterns**: Search logs for specific events

### General

1. **Start with verbose** to understand the system
2. **Use detailed-logs** for systematic experiments
3. **Use default** for large-scale statistical runs
4. **Mix modes**: Verbose for debugging, default for production

---

## Troubleshooting

### Verbose output is overwhelming

**Solution**: Use `--seeds 1` with verbose. For multiple episodes, use `--detailed-logs` instead.

### Emojis not displaying correctly

**Solution**: Ensure your terminal supports UTF-8 encoding. Most modern terminals do by default.

### Want to save verbose output

**Solution**: Either:
- Use `--detailed-logs` instead of `--verbose`
- Or redirect output: `... --verbose > output.log 2>&1`

### Logs are huge

**Solution**: Detailed logs can be large for long episodes. This is normal - they contain everything!

---

## Example: Watching Trust Evolve

Here's what a verbose run looks like when tracking trust:

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --max-steps 40 \
  --seeds 1 \
  --verbose
```

You'll see:
1. Initial reputation scores (all 1.0 - neutral)
2. Malerie makes misleading suggestion
3. Other agents try the wrong password
4. Reputation for Malerie drops (e.g., to 0.5)
5. Later turns show 🔴 red reputation for Malerie
6. Agents eventually ignore Malerie's suggestions
7. Team escapes without her help

This is incredibly valuable for understanding the dynamics!

---

## Summary

| Mode | Output | Best For | Command |
|------|--------|----------|---------|
| **Verbose** | Terminal | Single episode, debugging, demos | `--verbose` |
| **Detailed Logs** | Files | Multiple episodes, records | `--detailed-logs` |
| **Default** | Minimal | Statistics, large runs | (no flags) |

Choose the mode that fits your needs and enjoy full visibility into your multi-agent experiments!

