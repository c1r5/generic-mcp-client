import asyncio
import json
import logging

from dotenv import load_dotenv

from mcp_client import create_mcp_client

logger = logging.getLogger(__name__)

async def main():
    
    with open(".vscode/mcp.json", 'r') as f:
        data = json.load(f)['servers']
        
    mcp_client  = await create_mcp_client(data)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO
    )
    asyncio.run(main())
        
    