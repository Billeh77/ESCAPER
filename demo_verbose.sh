#!/bin/bash
# Demo script to show off ESCAPER's verbose mode

echo "=================================================="
echo "ESCAPER Verbose Mode Demo"
echo "=================================================="
echo ""
echo "This will run a single episode with full observability."
echo "You'll see:"
echo "  🏠 Room introduction"
echo "  🔍 Initial state"
echo "  ⏱️ Each timestep with agent thoughts and actions"
echo "  💬 All communication"
echo "  ⭐ Reputation scores (in this demo)"
echo "  💌 Private gossip messages"
echo "  🎉 Room events"
echo ""
echo "Press Enter to start..."
read

python -m escaper.cli.run_experiment \
  --personas escaper/config/personas/default_personas.json \
  --room escaper/config/rooms/room_simple_1.json \
  --adversary \
  --reputation \
  --gossip \
  --seeds 1 \
  --verbose

echo ""
echo "=================================================="
echo "Demo complete!"
echo "=================================================="
echo ""
echo "To try it yourself:"
echo "  python -m escaper.cli.run_experiment \\"
echo "    --personas escaper/config/personas/default_personas.json \\"
echo "    --room escaper/config/rooms/room_simple_1.json \\"
echo "    --adversary --reputation --gossip \\"
echo "    --seeds 1 \\"
echo "    --verbose"

