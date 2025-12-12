# ESCAPER Setup Guide

**THE ONLY GUIDE YOU NEED TO GET STARTED**

Follow these steps in order. Don't skip any.

---

## Step 1: Create Virtual Environment

```bash
# Navigate to ESCAPER
cd "/Users/emilebilleh/Documents/Columbia University/Senior Year/LLM Gen AI/ESCAPER"

# Create virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# On Windows instead:
# venv\Scripts\activate

# You should now see (venv) at the start of your prompt
```

## Step 2: Install

```bash
# Upgrade pip
pip install --upgrade pip

# Install ESCAPER
pip install -e .

# This should complete without errors
```

## Step 3: Configure API Keys

```bash
# Copy the example environment file
cp env.example .env

# Now open .env in any text editor and add your OpenAI API key
# Replace "your-openai-api-key-here" with your actual key
```

Or do it in one command:
```bash
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
```

**That's it for setup!** Your API key is now stored in `.env` and will be loaded automatically.

## Step 4: Test Installation

```bash
python test_installation.py
```

You should see all green checkmarks. If not, see Troubleshooting below.

## Step 5: Run Your First Experiment

### Option A: Quick Test (Minimal Output)
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --seeds 1
```

This runs 1 episode with minimal output. Should take less than 1 minute.

### Option B: Verbose Demo (See the Story!)
```bash
./demo_verbose.sh
```

Or run directly:
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary --reputation --gossip \
  --seeds 1 \
  --verbose
```

This shows the full narrative with agent thoughts, actions, and all state changes!

**If either runs successfully, you're done!**

---

## Quick Reference: Running Experiments

### Baseline (All Cooperative)
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --seeds 5
```
**Team**: Alice, Bob, Charlie, Daniela (all cooperative)

### With Detailed Observability (Verbose Mode)
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --seeds 1 \
  --verbose
```
**Shows**: Step-by-step narrative with all agent thoughts, actions, and state changes in real-time!
**Recommended**: Use with `--seeds 1` to see one complete story unfold

### With Adversary
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary \
  --seeds 5
```
**Team**: Alice, Bob, Charlie, Malerie (Malerie is malicious)

### Full System (Adversary + Reputation + Gossip)
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary \
  --reputation \
  --gossip \
  --max-steps 40 \
  --seeds 10 \
  --log-dir runs/experiment_001
```
**Team**: Alice, Bob, Charlie, Malerie (with trust and gossip enabled)

### Choose Adversary Style
```bash
# Subtle (harder to detect; no persona edits needed)
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary --adversary-style subtle \
  --seeds 1 --verbose
```

```bash
# Always-wrong (requires a persona with malice_style=always-wrong)
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary --adversary-style always-wrong \
  --seeds 1 --verbose
```

To enable “always-wrong”, add a second malicious persona to `escaper/config/personas/default_personas.json`:
```json
{
  "id": "malerie_aw",
  "name": "Malerie (AW)",
  "role_description": "Aggressively misleading (always wrong).",
  "is_malicious": true,
  "malice_style": "always-wrong"
}
```

---

## Important: Future Sessions

Every time you open a new terminal:

```bash
# 1. Navigate to directory
cd "/Users/emilebilleh/Documents/Columbia University/Senior Year/LLM Gen AI/ESCAPER"

# 2. Activate virtual environment
source venv/bin/activate

# 3. That's it! Your API key is already in .env
```

You'll know the venv is active when you see `(venv)` in your prompt.

---

## Troubleshooting

### Installation Failed

**Problem**: `pip install -e .` gives errors about email validation

**Solution**: You have an old version of `pyproject.toml`. The fix is already in the repo. Make sure you have the latest files.

**Problem**: "No module named 'escaper'" when running experiments

**Solution**: 
1. Make sure you activated the venv: `source venv/bin/activate`
2. Make sure you ran `pip install -e .` from the ESCAPER directory
3. Try: `pip list | grep escaper` - you should see it listed

### Test Installation Fails

**Problem**: `python test_installation.py` shows red X's

**Solution**: Read the specific error messages. Common issues:
- Python version too old (need 3.10+)
- Not in ESCAPER directory
- Dependencies not installed

### Runtime Errors

**Problem**: "OPENAI_API_KEY environment variable not set"

**Solution**: 
1. Make sure you created the `.env` file: `ls -la .env`
2. Make sure it has your key: `cat .env`
3. Your key should start with `sk-`

**Problem**: Episodes timeout or fail

**Solution**: Increase max steps: `--max-steps 50` or `--max-steps 60`

### API Key Issues

**Problem**: "Invalid API key" or authentication errors

**Solution**:
1. Check your key is correct at https://platform.openai.com/api-keys
2. Make sure there are no extra spaces in your `.env` file
3. The key should start with `sk-`

### Need to Start Over?

```bash
# Remove everything and start fresh
cd "/Users/emilebilleh/Documents/Columbia University/Senior Year/LLM Gen AI/ESCAPER"
deactivate  # Exit venv if in one
rm -rf venv  # Remove old venv
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .
cp env.example .env
# Now edit .env to add your API key
```

---

## Available Rooms

1. **room_simple_1.json**: One door, one clue (easy, ~5-10 steps)
2. **room_two_stage_1.json**: Two stages, intermediate door (harder, ~15-25 steps)

## Available Agents

- **Alice**: Analytical
- **Bob**: Detail-oriented
- **Charlie**: Coordinator
- **Daniela**: Cooperative (used in baseline)
- **Malerie**: Malicious (used with --adversary flag)

Each run uses 4 agents. CLI automatically picks the right 4.

## Observability Features

### Verbose Mode (--verbose)
See the story unfold in real-time! Shows:
- 🏠 Room introduction and initial state
- ⏱️ Each timestep with public and private views
- 🤖 Each agent's turn with their thoughts and actions
- 💬 All communication (public and private when enabled)
- ⭐ Reputation scores (when enabled)
- 🎉 Room events (doors opening, escape, etc.)

**Example**:
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary --reputation --gossip \
  --seeds 1 \
  --verbose
```

**Best for**: Single episode runs where you want to see everything happening

### Detailed Logs (--detailed-logs)
Same as verbose but saved to files instead of terminal. Creates `episode_N_detailed.log` for each episode.

**Example**:
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_two_stage_1.json \
  --adversary --reputation --gossip \
  --seeds 10 \
  --log-dir runs/experiment_001 \
  --detailed-logs
```

**Best for**: Multiple episodes where you want complete records

### Default Mode (no flags)
Minimal output - just episode results and final summary. Clean and concise.

**Output includes**:
- Success/failure per episode
- Steps taken
- Wrong password attempts
- **Final reputation scores** (when --reputation enabled) - shows average trust each agent has from teammates

**Best for**: Running many episodes for statistical analysis

## Command Line Flags

- `--personas PATH` - Persona config file (required)
- `--room PATH` - Room config file (required)
- `--adversary` - Enable malicious agent
- `--reputation` - Enable private trust tracking
- `--gossip` - Enable private messaging
- `--max-steps N` - Max timesteps (default: 30)
- `--seeds N` - Number of episodes (default: 5)
- `--model NAME` - OpenAI model (default: gpt-4-turbo-preview)
- `--log-dir PATH` - Save logs to directory with timestamps
- `--verbose` - Show detailed step-by-step output in terminal
- `--detailed-logs` - Save detailed step-by-step logs to files (requires --log-dir)

### What Gets Saved

When using `--log-dir`, these files are automatically created (with timestamps):

```
your_log_dir/
├── terminal_output_20241212_143022.txt        # Complete terminal output
├── metrics_summary_20241212_143022.json       # Statistics
├── episodes_20241212_143022.jsonl             # Per-episode data
├── experiment_config_20241212_143022.txt      # Your settings
└── episode_N_detailed_20241212_143022.log     # Detailed logs (if --detailed-logs)
```

**Benefit**: Run multiple experiments to the same folder - timestamps prevent overwrites!

## Need More Help?

- **This file (QUICKSTART.md)**: THE installation and usage guide
- **README.md**: Project overview and detailed documentation
- **USAGE_EXAMPLES.md**: More example commands and research scenarios
- **DEVELOPMENT.md**: Extending the platform

---

## Summary

**Setup (do once):**
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install --upgrade pip && pip install -e .`
4. `cp env.example .env` and edit `.env` to add your API key
5. `python test_installation.py`

**Every new terminal session:**
1. `cd ESCAPER`
2. `source venv/bin/activate`

**Run experiments:**
```bash
python -m escaper.cli.run_experiment --personas <personas> --room <room> [flags]
```

That's it!
