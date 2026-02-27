import asyncio
from src.state import AgentState
from src.nodes.detectives import run_detectives

async def main():
    state = AgentState(repo_url="...", pdf_path="report.pdf")
    await run_detectives(state)

    print(state.evidences)

asyncio.run(main())
