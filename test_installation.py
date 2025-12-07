#!/usr/bin/env python
"""
Quick test script to verify ESCAPER installation.
Run this after installation to check if everything is set up correctly.
"""

import sys
import os

def test_installation():
    """Test that ESCAPER is properly installed."""
    print("Testing ESCAPER installation...\n")
    
    # Test 1: Python version
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"  ✗ FAILED: Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
    
    # Test 2: Import core modules
    print("\n✓ Checking core modules...")
    try:
        from escaper.core import room, state, tools, agents, runner, metrics
        print("  ✓ Core modules imported successfully")
    except ImportError as e:
        print(f"  ✗ FAILED: Could not import core modules: {e}")
        print("  → Try: pip install -e .")
        return False
    
    # Test 3: Import CLI
    print("\n✓ Checking CLI module...")
    try:
        from escaper.cli import run_experiment
        print("  ✓ CLI module imported successfully")
    except ImportError as e:
        print(f"  ✗ FAILED: Could not import CLI: {e}")
        return False
    
    # Test 4: Check dependencies
    print("\n✓ Checking dependencies...")
    try:
        import openai
        print(f"  ✓ openai {openai.__version__}")
    except ImportError:
        print("  ✗ FAILED: openai not found")
        print("  → Try: pip install openai")
        return False
    
    try:
        import jinja2
        print(f"  ✓ jinja2 {jinja2.__version__}")
    except ImportError:
        print("  ✗ FAILED: jinja2 not found")
        print("  → Try: pip install jinja2")
        return False
    
    try:
        import dotenv
        print(f"  ✓ python-dotenv installed")
    except ImportError:
        print("  ✗ FAILED: python-dotenv not found")
        print("  → Try: pip install python-dotenv")
        return False
    
    # Test 5: Check configuration files
    print("\n✓ Checking configuration files...")
    required_files = [
        "escaper/config/rooms/room_simple_1.json",
        "escaper/config/rooms/room_two_stage_1.json",
        "escaper/config/personas/default_personas.json",
        "escaper/prompts/agent_prompt.jinja",
        "escaper/prompts/system_coop.txt",
        "escaper/prompts/system_malicious.txt",
    ]
    
    all_found = True
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"  ✓ {filepath}")
        else:
            print(f"  ✗ {filepath} NOT FOUND")
            all_found = False
    
    if not all_found:
        print("\n  → Make sure you're running this from the ESCAPER root directory")
        return False
    
    # Test 6: Check API key
    print("\n✓ Checking API key...")
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        print(f"  ✓ OPENAI_API_KEY is set (starts with: {api_key[:7]}...)")
    else:
        # Check for .env file
        if os.path.exists(".env"):
            print("  ⚠ OPENAI_API_KEY not in environment, but .env file exists")
            print("  → The key will be loaded from .env when you run experiments")
        else:
            print("  ⚠ WARNING: OPENAI_API_KEY not set")
            print("  → Set it with: export OPENAI_API_KEY='your-key-here'")
            print("  → Or create .env file with: echo 'OPENAI_API_KEY=your-key-here' > .env")
    
    # Test 7: Test loading a room
    print("\n✓ Testing room loading...")
    try:
        from escaper.core.room import Room
        room = Room.from_json("escaper/config/rooms/room_simple_1.json")
        print(f"  ✓ Loaded room: {room.title}")
        print(f"  ✓ Room has {len(room.objects)} objects")
    except Exception as e:
        print(f"  ✗ FAILED: Could not load room: {e}")
        return False
    
    # Test 8: Test loading personas
    print("\n✓ Testing persona loading...")
    try:
        import json
        with open("escaper/config/personas/default_personas.json") as f:
            personas_data = json.load(f)
        print(f"  ✓ Loaded {len(personas_data['personas'])} personas")
        names = [p['name'] for p in personas_data['personas']]
        print(f"  ✓ Personas: {', '.join(names)}")
    except Exception as e:
        print(f"  ✗ FAILED: Could not load personas: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("ESCAPER Installation Test")
    print("="*60 + "\n")
    
    success = test_installation()
    
    print("\n" + "="*60)
    if success:
        print("✓ ALL TESTS PASSED!")
        print("="*60)
        print("\nESCAPER is properly installed and ready to use!")
        print("\nNext steps:")
        print("1. Set your API key (if not already done):")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("\n2. Run a test experiment:")
        print("   python -m escaper.cli.run_experiment \\")
        print("     --personas escaper/config/personas/default_personas.json \\")
        print("     --room escaper/config/rooms/room_simple_1.json \\")
        print("     --seeds 1")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the issues above before running experiments.")
        print("See INSTALL.md for detailed troubleshooting.")
        sys.exit(1)

