# ESCAPER Usage Examples

This guide provides concrete examples for running different types of experiments with ESCAPER.

## Table of Contents

1. [Basic Experiments](#basic-experiments)
2. [The Four Conditions](#the-four-conditions)
3. [Custom Configurations](#custom-configurations)
4. [Analyzing Results](#analyzing-results)

## Observability: Watching Experiments Unfold

### Verbose Mode - See Everything in Real-Time

For a beautiful, story-like experience, use `--verbose` with a single episode:

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary --reputation --gossip \
  --seeds 1 \
  --verbose
```

**What you'll see**:
- 🏠 Room introduction and scenario setup
- 🔍 Initial room state with all visible objects
- ⏱️ Each timestep with:
  - Public view (what everyone sees)
  - Each agent's turn showing:
    - Their private observations
    - Their reputation scores (if enabled)
    - Their private messages received (if enabled)
    - Their actions and results
    - Their thought process/summary
- 🎉 Room events (doors opening, escape)

Perfect for:
- Understanding how agents collaborate
- Debugging scenarios
- Demonstrations
- Seeing trust dynamics evolve

### Detailed Logs - Same Info, Saved to Files

For multiple episodes where you want complete records:

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary --reputation --gossip \
  --seeds 10 \
  --log-dir runs/detailed_experiment \
  --detailed-logs
```

This creates `episode_0_detailed.log`, `episode_1_detailed.log`, etc. in your log directory.

Perfect for:
- Running many episodes but keeping detailed records
- Post-experiment analysis
- Finding specific interesting episodes

### Default Mode - Minimal Output

For clean statistical runs:

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --seeds 50
```

Perfect for:
- Large-scale experiments
- Statistical analysis
- Quick results

---

## Basic Experiments

### Condition 1: Baseline (No Adversary)

Run a cooperative team with no malicious agent:

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --max-steps 30 \
  --seeds 10
```

**What happens**: All 4 agents (Alice, Bob, Charlie, Daniela) cooperate honestly to solve the puzzle. This establishes baseline performance metrics.

### Condition 2: Adversary Only

Add a malicious agent without any trust mechanisms:

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary \
  --max-steps 30 \
  --seeds 10
```

**What happens**: The fourth agent Malerie (marked `is_malicious: true`) provides misleading information. The team is now Alice, Bob, Charlie, and Malerie. Other agents have no mechanism to track trustworthiness.

### Condition 3: Adversary + Reputation

Enable private reputation tracking:

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --max-steps 40 \
  --seeds 10
```

**What happens**: Each agent maintains private trust scores. Agents can use `update_reputation()` to adjust scores based on observations, potentially learning to distrust the malicious agent.

### Condition 4: Full System (Adversary + Reputation + Gossip)

Enable all mechanisms:

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --gossip \
  --max-steps 40 \
  --seeds 10 \
  --log-dir runs/full_experiment_$(date +%Y%m%d_%H%M%S)
```

**What happens**: Agents can send private messages via `send_private()`, enabling them to share suspicions about the malicious agent without alerting them in public chat.

## The Four Conditions

### Comparing All Conditions

Run all four conditions sequentially:

```bash
# Condition 1: Baseline
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --max-steps 40 \
  --seeds 10 \
  --log-dir runs/condition1_baseline

# Condition 2: Adversary only
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --max-steps 40 \
  --seeds 10 \
  --log-dir runs/condition2_adversary

# Condition 3: Adversary + Reputation
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --max-steps 40 \
  --seeds 10 \
  --log-dir runs/condition3_rep

# Condition 4: Adversary + Reputation + Gossip
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --gossip \
  --max-steps 40 \
  --seeds 10 \
  --log-dir runs/condition4_full
```

Then compare metrics across `runs/condition*/metrics_summary.json`.

## Custom Configurations

### Using Different Models

Test with different OpenAI models:

```bash
# GPT-4 Turbo (default)
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --model gpt-4-turbo-preview \
  --seeds 5

# GPT-3.5 Turbo (faster, cheaper)
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --model gpt-3.5-turbo \
  --seeds 5
```

### Adjusting Episode Length

For more complex rooms, increase max steps:

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --gossip \
  --max-steps 60 \
  --seeds 10
```

### Running More Seeds

For statistical significance, run more episodes:

```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary \
  --reputation \
  --seeds 50 \
  --log-dir runs/large_sample
```

## Analyzing Results

### Quick Statistics

The CLI prints summary statistics automatically:

```
EXPERIMENT SUMMARY
============================================================
Total episodes: 10
Success rate: 80.00%
Avg steps (if success): 12.50
============================================================
```

### Saved Logs

When using `--log-dir`, you get:

1. **metrics_summary.json**: Aggregate statistics
   ```json
   {
     "num_episodes": 10,
     "success_rate": 0.8,
     "avg_steps_if_success": 12.5
   }
   ```

2. **episodes.jsonl**: Per-episode data
   ```json
   {"episode": 0, "success": true, "steps_taken": 12, ...}
   {"episode": 1, "success": false, "steps_taken": 30, ...}
   ```

### Comparing Conditions

Use Python to compare results:

```python
import json

# Load metrics from different conditions
with open('runs/condition1_baseline/metrics_summary.json') as f:
    baseline = json.load(f)

with open('runs/condition4_full/metrics_summary.json') as f:
    full = json.load(f)

print(f"Baseline success rate: {baseline['success_rate']:.2%}")
print(f"Full system success rate: {full['success_rate']:.2%}")
print(f"Improvement: {(full['success_rate'] - baseline['success_rate']):.2%}")
```

### Episode Summaries

Check agent reasoning in the summaries:

```python
import json

with open('runs/condition4_full/episodes.jsonl') as f:
    for line in f:
        ep = json.load(line)
        print(f"Episode {ep['episode']}: {ep['success']}")
        for summary in ep['summaries']:
            print(f"  {summary}")
```

## Research Questions Examples

### RQ1: Does reputation help?

Compare conditions 2 (adversary only) vs 3 (adversary + reputation):

```bash
# Without reputation
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --seeds 20 \
  --log-dir runs/rq1_no_rep

# With reputation
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --seeds 20 \
  --log-dir runs/rq1_with_rep
```

**Hypothesis**: Reputation should improve success rate and reduce wrong password attempts.

### RQ2: Does gossip accelerate detection?

Compare conditions 3 (reputation only) vs 4 (reputation + gossip):

```bash
# Reputation only
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --seeds 20 \
  --log-dir runs/rq2_no_gossip

# Reputation + Gossip
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --gossip \
  --seeds 20 \
  --log-dir runs/rq2_with_gossip
```

**Hypothesis**: Gossip enables faster convergence on identifying the malicious agent.

### RQ3: How does room complexity affect dynamics?

Test the same condition on different rooms:

```bash
# Simple room
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary \
  --reputation \
  --gossip \
  --seeds 15 \
  --log-dir runs/rq3_simple

# Complex room
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --gossip \
  --seeds 15 \
  --log-dir runs/rq3_complex
```

**Hypothesis**: More complex rooms require more coordination, making reputation/gossip more valuable.

## Tips

1. **Start small**: Test with `--seeds 1` or `--seeds 3` to verify your setup
2. **Use log directories**: Always use `--log-dir` for analysis
3. **Timestamp runs**: Use `$(date +%Y%m%d_%H%M%S)` in log directory names
4. **Monitor costs**: Each episode makes multiple LLM calls; watch your API usage
5. **Reproducibility**: Use the same seed count across conditions for fair comparison

## Troubleshooting

### Episodes always fail

- Try increasing `--max-steps`
- Check that your room is solvable (test manually first)
- Verify clues are clear enough

### Agents don't use reputation

- Ensure `--reputation` flag is set
- Check if agents mention trust scores in their summaries
- Try a scenario where misinformation is more obvious

### High API costs

- Use `gpt-3.5-turbo` instead of GPT-4
- Reduce `--seeds`
- Use simpler rooms (fewer objects = fewer tool calls)

## Next Steps

1. Create your own rooms (see README.md)
2. Design custom personas
3. Analyze logs programmatically
4. Visualize agent interactions
5. Compare different LLM models

