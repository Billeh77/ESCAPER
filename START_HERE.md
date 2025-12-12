# 👉 START HERE

## New to ESCAPER? Follow these in order:

### 1. **[QUICKSTART.md](QUICKSTART.md)** ⭐ **READ THIS FIRST**
   - Complete installation guide
   - API key setup (ONE place: `env.example` → `.env`)
   - Running your first experiment
   - Troubleshooting
   
   **This is THE guide. Follow it step by step.**

### 2. **[README.md](README.md)**
   - What ESCAPER is
   - Features and capabilities
   - Creating custom rooms
   - Creating personas
   - Tool API reference

### 3. **[OBSERVABILITY.md](OBSERVABILITY.md)** ⭐ **NEW - Watch Experiments Unfold!**
   - Verbose mode guide (see everything in real-time)
   - Detailed logs (save complete narratives)
   - Beautiful story-like output
   - Perfect for understanding agent behavior

### 4. **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)**
   - More example commands
   - Research scenarios
   - Comparing conditions
   - Analysis examples

---

## File Organization

### Setup & Installation
- **QUICKSTART.md** - THE installation guide ⭐
- **INSTALL.md** - Quick reference (points to QUICKSTART)
- **env.example** - Template for API keys (copy to `.env`)
- **test_installation.py** - Test your setup
- **RATE_LIMIT_HANDLING.md** - How automatic retry works

### Documentation
- **README.md** - Project overview and documentation
- **USAGE_EXAMPLES.md** - Command examples
- **DEVELOPMENT.md** - Extending the platform
- **STRUCTURE.md** - Repository structure
- **PROJECT_SUMMARY.md** - Implementation details
- **CHANGELOG.md** - Version history

### Configuration
- **escaper/config/rooms/** - Room scenarios (JSON)
- **escaper/config/personas/** - Agent personas (JSON)
- **escaper/prompts/** - LLM prompt templates

### Code
- **escaper/core/** - Main simulation engine
- **escaper/cli/** - Command-line interface
- **escaper/logging/** - Output and metrics

---

## Quick Reference

### Setup (do once)
```bash
cd ESCAPER
python -m venv venv
source venv/bin/activate
pip install --upgrade pip && pip install -e .
cp env.example .env  # Then edit .env to add your API key
python test_installation.py
```

### Every new session
```bash
cd ESCAPER
source venv/bin/activate
```

### Run experiment
```bash
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --seeds 5
```

---

## 📖 **→ Go to [QUICKSTART.md](QUICKSTART.md) now**

