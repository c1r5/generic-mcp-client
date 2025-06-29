import asyncio
import json
import logging

from mcp_agent import create_mcp_agent
from mcp_client import MCPClient


logger = logging.getLogger(__name__)


def chat_loop():
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

    mcp_agent = await create_mcp_agent(data)
    mcp_client = MCPClient(agent=mcp_agent)
    await mcp_client.create_session()

    try:
        for query in chat_loop():
            async for response in mcp_client.ask(query):
                print(response)
            
    except KeyboardInterrupt as e:
        logger.error("❌ Execução interrompida pelo usuário")

    finally:
        await mcp_client.close()


if __name__ == "__main__":
    try:
        logging.basicConfig(
            level=logging.INFO,
            filename='.logs/logs.txt',
            filemode='a',  # or 'w' to overwrite on every run
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        asyncio.run(main())
    except Exception as e:
        logger.info("bye")

