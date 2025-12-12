# escaper/cli/run_experiment.py
"""CLI entrypoint for running ESCAPER experiments."""

import argparse
import os
import sys
from jinja2 import Environment, FileSystemLoader

from escaper.core.room import Room
from escaper.core.runner import SimulationRunner, ExperimentSettings
from escaper.core.agents import AgentConfig, OpenAILLMClient
from escaper.core.metrics import MetricsAccumulator
from escaper.logging.logger import print_episode_summary, print_final_summary, VerboseLogger
from escaper.logging.serializers import save_metrics_summary, save_episode_logs


def load_personas(path: str):
    """Load persona configurations from JSON file."""
    import json
    with open(path, "r") as f:
        data = json.load(f)
    
    configs = []
    for p in data["personas"]:
        configs.append(AgentConfig(
            agent_id=p["id"],
            name=p["name"],
            role_description=p.get("role_description", ""),
            is_malicious=p.get("is_malicious", False),
            malice_style=p.get("malice_style")
        ))
    return configs


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Run ESCAPER experiments: multi-agent escape room simulations with LLMs."
    )
    parser.add_argument(
        "--personas", 
        required=True, 
        help="Path to personas JSON file."
    )
    parser.add_argument(
        "--room", 
        required=True, 
        help="Path to room JSON file."
    )
    parser.add_argument(
        "--adversary", 
        action="store_true", 
        help="Enable malicious agent behavior (uses is_malicious flag from personas)."
    )
    parser.add_argument(
        "--adversary-style",
        choices=["subtle", "always-wrong"],
        default=None,
        help="When --adversary is set, choose which malicious persona style to use."
    )
    parser.add_argument(
        "--reputation", 
        action="store_true", 
        help="Enable private reputation tracking."
    )
    parser.add_argument(
        "--gossip", 
        action="store_true", 
        help="Enable private messaging (gossip) between agents."
    )
    parser.add_argument(
        "--max-steps", 
        type=int, 
        default=30,
        help="Maximum timesteps per episode (default: 30)."
    )
    parser.add_argument(
        "--seeds", 
        type=int, 
        default=5,
        help="Number of independent episodes to run (default: 5)."
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default="gpt-4-turbo-preview",
        help="OpenAI model name (default: gpt-4-turbo-preview)."
    )
    parser.add_argument(
        "--log-dir", 
        type=str, 
        default=None,
        help="Directory to write logs and metrics. If not provided, logs are not saved to disk."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed step-by-step output to terminal (recommended for single episode runs)."
    )
    parser.add_argument(
        "--detailed-logs",
        action="store_true",
        help="Save detailed step-by-step logs to files (one per episode). Requires --log-dir."
    )
    
    args = parser.parse_args()
    
    # Validate environment
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.", file=sys.stderr)
        print("Please set it before running experiments.", file=sys.stderr)
        sys.exit(1)
    
    # Load configuration
    print(f"Loading room from: {args.room}")
    room = Room.from_json(args.room)
    
    print(f"Loading personas from: {args.personas}")
    all_personas = load_personas(args.personas)
    
    # Filter personas based on adversary flag and style
    if args.adversary:
        # include malicious, exclude Daniela
        candidates = [p for p in all_personas if p.agent_id != "daniela" and p.is_malicious]
        if args.adversary_style:
            preferred = [p for p in candidates if (p.malice_style or "subtle") == args.adversary_style]
            chosen = preferred[0] if preferred else (candidates[0] if candidates else None)
        else:
            chosen = candidates[0] if candidates else None
        # fallback: if none found, keep existing behavior by excluding daniela and keeping others non-malicious
        if chosen:
            personas = [p for p in all_personas if p.agent_id not in ("daniela",) and not p.is_malicious]
            personas.append(chosen)
        else:
            personas = [p for p in all_personas if p.agent_id != "daniela"]
    else:
        # Use cooperative fourth agent (Daniela), exclude all malicious
        personas = [p for p in all_personas if not p.is_malicious]
    
    # Create experiment settings
    settings = ExperimentSettings(
        adversary_enabled=args.adversary,
        reputation_enabled=args.reputation,
        gossip_enabled=args.gossip,
        max_steps=args.max_steps,
    )
    
    # Print experiment configuration
    print("\n" + "="*60)
    print("EXPERIMENT CONFIGURATION")
    print("="*60)
    print(f"Room: {room.title} ({room.room_id})")
    print(f"Agents: {', '.join(p.name for p in personas)}")
    print(f"Adversary enabled: {settings.adversary_enabled}")
    print(f"Reputation enabled: {settings.reputation_enabled}")
    print(f"Gossip enabled: {settings.gossip_enabled}")
    print(f"Max steps: {settings.max_steps}")
    print(f"Number of episodes: {args.seeds}")
    print(f"Model: {args.model}")
    print("="*60 + "\n")
    
    # Set up Jinja environment for prompt templates
    template_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    # Create LLM client
    print("Initializing LLM client...")
    llm = OpenAILLMClient(model_name=args.model)
    
    # Warn about verbose with multiple seeds
    if args.verbose and args.seeds > 1:
        print("\n⚠️  WARNING: --verbose is enabled with multiple episodes.")
        print("   This will produce A LOT of output. Consider using --seeds 1 for verbose mode.")
        print("   Or use --detailed-logs instead to save logs to files.\n")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Check detailed-logs requires log-dir
    if args.detailed_logs and not args.log_dir:
        print("Error: --detailed-logs requires --log-dir to be set.", file=sys.stderr)
        sys.exit(1)
    
    # Run episodes
    print(f"\nRunning {args.seeds} episodes...\n")
    seeds = list(range(args.seeds))
    acc: MetricsAccumulator = MetricsAccumulator()
    
    for i, seed in enumerate(seeds):
        # Create verbose logger for this episode if requested
        verbose_logger = None
        if args.verbose or args.detailed_logs:
            log_file = None
            if args.detailed_logs:
                log_file = os.path.join(args.log_dir, f"episode_{i}_detailed.log")
            verbose_logger = VerboseLogger(enabled=args.verbose, log_file=log_file)
        
        # Create runner with verbose logger
        runner = SimulationRunner(
            room=room,
            persona_configs=personas,
            settings=settings,
            llm_client=llm,
            jinja_env=jinja_env,
            verbose_logger=verbose_logger,
        )
        
        # Run episode
        ep_metrics = runner.run_episode(seed=seed)
        acc.add(ep_metrics)
        
        # Close verbose logger
        if verbose_logger:
            verbose_logger.close()
        
        # Print episode summary (also in verbose to show metrics like wrong password attempts)
        agent_names_map = {p.agent_id: p.name for p in personas}
        print_episode_summary(i, ep_metrics, agent_names=agent_names_map)
    
    # Print and save final summary
    summary = acc.summary()
    agent_names_map = {p.agent_id: p.name for p in personas}
    print_final_summary(summary, agent_names=agent_names_map)
    
    # Save logs if requested
    if args.log_dir:
        print(f"\nSaving logs to: {args.log_dir}")
        save_metrics_summary(summary, args.log_dir)
        save_episode_logs(acc.episodes, args.log_dir)
    
    print("\nExperiment complete!")


if __name__ == "__main__":
    main()

