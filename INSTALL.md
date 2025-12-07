# Installation Guide

**👉 See [QUICKSTART.md](QUICKSTART.md) for complete installation instructions.**

QUICKSTART.md is THE definitive installation and setup guide. It includes:

- Virtual environment setup
- Installation steps
- API key configuration
- Testing your installation
- Troubleshooting common issues
- Example commands to run experiments

Everything you need is in QUICKSTART.md - follow that guide step by step.

---

## Quick Summary (Full details in QUICKSTART.md)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install
pip install --upgrade pip
pip install -e .

# 3. Configure API key
cp env.example .env
# Edit .env and add your OpenAI API key

# 4. Test
python test_installation.py

# 5. Run first experiment
python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --seeds 1
```

**For detailed explanations, troubleshooting, and examples, see [QUICKSTART.md](QUICKSTART.md).**
