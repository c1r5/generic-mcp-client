from venv import logger
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams, StreamableHTTPConnectionParams, StdioConnectionParams
from google.adk.agents import Agent

from mcp import StdioServerParameters
from typing import Any, Dict, Literal

from google.genai.types import HarmCategory, HarmBlockThreshold
from google.genai import types


Transport = Literal["stdio", "sse", "streamable_http"]
MCPServerConfig = dict[str, dict[str, str]]
Connection = Dict[str, Any]
DiscoveredServers = Dict[str, Connection]

      
def _mcp_config_server_parser(mcp_server_configs: MCPServerConfig) -> DiscoveredServers:
    discovered_servers: DiscoveredServers = {}

    for server_name in mcp_server_configs.keys():
        server_config = mcp_server_configs[server_name]

        server_config.pop("type", "<none>")

        discovered_servers[server_name] = {**server_config}
        
        stdio_required_params = ["command", "args"]
        
        if all([(required in server_config.keys()) for required in stdio_required_params]):
            discovered_servers[server_name]["transport"] = "stdio"
            
        elif "url" in server_config:
            url = server_config["url"]
            if "/mcp" in url:
                discovered_servers[server_name]["transport"] = "streamable_http"
            elif "/sse":
                discovered_servers[server_name]["transport"] = "sse"
        else:
            raise ValueError(
                "Does not able to determine server type, should be: SSE, HTTP or STDIO"
            )

    return discovered_servers


def _load_mcp_toolset(connection: Connection) -> MCPToolset:
    transport_type: Transport = connection['transport']
    
    match transport_type:
        case "stdio":
            return MCPToolset(
                connection_params=StdioConnectionParams(
                    timeout=60,
                    server_params=StdioServerParameters(
                        command=connection["command"],
                        args=connection["args"],
                        env=connection.get('env', {})
                    ),
                )
            )
        case "sse":
            return MCPToolset(
                connection_params=SseConnectionParams(
                    url=connection["url"],
                    headers=connection.get('headers', {}),
                    timeout=60
                )
            )
        case "streamable_http":
            return MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=connection["url"],
                    headers=connection.get('headers', {}),
                    timeout=60
                )
            )
        case _:
            raise ValueError(
                "Does not able to determine server type, should be: SSE, HTTP or STDIO"
            )


async def create_mcp_agent(mcp_config: MCPServerConfig):
    try:
        safety_settings = [
            types.SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE # Example: adjust as needed
            ),
        ]

        gen_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.9,
            safety_settings=safety_settings
        )

        servers = _mcp_config_server_parser(mcp_config)
        toolset = [_load_mcp_toolset(connection) for _, connection in servers.items()]
        
        logger.info(f"Discovered and Loaded {len(toolset)} tools")
        
        agent = Agent(
            model='gemini-1.5-pro-002',
            name='personal_generic_agent',
            tools=[*toolset],
            generate_content_config=gen_config,
            instruction="""
            You are a helpful assistant with access to tools. Your role is to decide the best tool to use based on the user's question.

            Important guidelines:

            1. **Always select the most appropriate tool** based on the user's intent.
            2. **Use the provided resources** to fill in any missing arguments for the tools. The resources are listed below.
            3. Do **not ask the user for missing arguments** if the information can be found in the loaded resources.
            4. Only if a required parameter is missing after checking the resources, then you may ask the user for clarification.
            5. After receiving the tool’s response, generate a friendly and concise reply summarizing the result.
            6. Respond in the same language as the user's message.
            """
        )
    except Exception as e:
        raise e
    
    return agent

