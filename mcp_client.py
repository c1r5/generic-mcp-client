import asyncio
from mcp import ClientSession, StdioServerParameters, stdio_client
from typing import Any, Dict, Literal
from contextlib import AsyncExitStack


Transport = Literal["stdio", "sse", "streamable_http"]

MCPServerConfig = dict[str, dict[str, str]]
Connection = Dict[str, Any]
DiscoveredServers = Dict[str, Connection]

async def create_mcp_client(mcp_config: MCPServerConfig):
    exit_stack = AsyncExitStack()
    
    ...

async def close_mcp_client(exit_stack: AsyncExitStack):
    await exit_stack.aclose()
    
async def _create_mcp_server_session(
    mcp_server_configs: MCPServerConfig, 
    exit_stack: AsyncExitStack
):
    discovered_servers: DiscoveredServers = {}
    
    for server_name in mcp_server_configs.keys():
        server_config = mcp_server_configs[server_name]
        
        server_config.pop("type", "<none>")
        
        discovered_servers[server_name] = {**server_config}
                
        if "command" in server_config:
            discovered_servers[server_name]['transport'] = "stdio"
            
        elif "url" in server_config:
            url = server_config['url']
            if "/mcp" in url:
                discovered_servers[server_name]['transport'] = "streamable_http"
            elif "/sse":
                discovered_servers[server_name]['transport'] = "sse"
        else:
            raise ValueError("Does not able to determine server type, should be: SSE, HTTP or STDIO")
    
    discover_and_create_session = [_connect_and_discover(discovered_servers[server_name], exit_stack) for server_name in discovered_servers.keys()]

    sessions = await asyncio.gather(*discover_and_create_session)
    
    
        
async def _connect_and_discover(connection: Connection, exit_stack: AsyncExitStack) -> ClientSession:
    transport_type: Transport = connection['transport']
    session: ClientSession | None = None
    
    match transport_type:
        case 'stdio':
            stdio_transport = await exit_stack.enter_async_context(stdio_client(StdioServerParameters(**connection)))
            stdio, write = stdio_transport
            session = await exit_stack.enter_async_context(ClientSession(stdio, write))
        case 'streamable_http':
            ...
        case 'sse':
            ...
        case _:
            ...
    
    if session is None:
        raise UnboundLocalError(f"ClientSession not defined to this transport type {transport_type}")
    
    await session.initialize()
    response = await session.list_tools()
    print("\nConnected to server with tools:", [tool.name for tool in response.tools])
    return session
        
    
    
    