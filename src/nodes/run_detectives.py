# Run detectives and collect evidence
# src/nodes/run_detectives.py

import asyncio
import argparse
import os
from src.state import AgentState
from src.nodes.detectives import run_detectives

async def main():
    parser = argparse.ArgumentParser(description="Run AI Detectives on a Repo, PDF, or Both")

    # Removed required=True to allow flexibility
    parser.add_argument("--repo", default=None, help="The GitHub repository URL (optional)")
    parser.add_argument("--pdf", default=None, help="Path to the report PDF (optional)")

    args = parser.parse_args()

    # 1. Validation: Ensure at least one argument is provided
    if not args.repo and not args.pdf:
        print("❌ Error: You must provide either --repo, --pdf, or both.")
        return

    # 2. Initialize state
    # Note: Your AgentState definition must support None values for these fields
    state = AgentState(repo_url=args.repo, pdf_path=args.pdf)

    print(f"--- 🕵️ Detective Active ---")
    if args.repo: print(f"Target Repo: {args.repo}")
    if args.pdf:  print(f"Target PDF:  {args.pdf}")
    print("---------------------------\n")

    await run_detectives(state)

    print("\n--- Evidence Found ---")
    print(state.evidences)

if __name__ == "__main__":
    asyncio.run(main())
