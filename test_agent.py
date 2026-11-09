import asyncio

from app.agents.graph import run_agent


async def main():
    prompts = [
        "Where is my order ORD-1024?",
        "Can I get a refund for ORD-1025?",
        "Check the status and refund eligibility of ORD-1024.",
    ]

    for prompt in prompts:
        print(f"\nUser: {prompt}")
        response = await run_agent(prompt)
        print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())