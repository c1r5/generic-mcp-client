from mcp.server.fastmcp import FastMCP
from datetime import datetime
import pytz

mcp = FastMCP(
    "get_time",
    description="A tool to get the current time in a specified timezone.",
    version="1.0.0",
)

@mcp.tool(
    name="get_current_time",
    description="Returns the current time for a given IANA timezone (e.g. 'America/Sao_Paulo')."
)
async def get_current_time(timezone: str = "America/Sao_Paulo") -> str:
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except pytz.UnknownTimeZoneError:
        return f"Unknown timezone: '{timezone}'. Try something like 'America/Sao_Paulo'."
    except Exception as e:
        return f"Error: {e}"

@mcp.resource(
    name="available_timezones",
    uri="helper://timezones",
    description="Returns all supported IANA timezones."
)
def available_timezones() -> str:
    return "\n".join(pytz.all_timezones)

if __name__ == "__main__":
    mcp.run("stdio")