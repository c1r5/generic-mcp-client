import asyncio
import json
import logging
from contextlib import AsyncExitStack
from mcp_client import close_mcp_client, create_mcp_client

logger = logging.getLogger(__name__)


async def chat_loop():
    """Run an interactive chat loop"""
    print("\n🤖 MCP Client Started!")
    print("Type your queries or 'quit' to exit.")

    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() == "quit":
                break
            yield query
        except Exception as e:
            print(f"\n⚠️ Error: {str(e)}")
            continue


async def main():
    with open(".vscode/mcp.json", "r") as f:
        data = json.load(f)["servers"]

    async with AsyncExitStack() as exit_stack:
        try:
            await create_mcp_client(data, exit_stack)

            async for query in chat_loop():
                print(f"📨 Você perguntou: {query}")
                # Aqui você pode chamar algo como: await mcp_client.ask(query)

        except Exception as e:
            logger.error("❌ Erro durante execução do MCP:", exc_info=e)

        finally:
            await close_mcp_client(exit_stack)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

