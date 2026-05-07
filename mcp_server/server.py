import os
from mcp.server.fastmcp import FastMCP
from mcrcon import MCRcon

# Initialize FastMCP server
mcp = FastMCP("FactorioAI")

RCON_HOST = os.environ.get("FACTORIO_RCON_HOST", "127.0.0.1")
RCON_PORT = int(os.environ.get("FACTORIO_RCON_PORT", "27015"))
RCON_PASSWORD = os.environ.get("FACTORIO_RCON_PASSWORD", "factorio_rcon_password")

import sys

def run_lua(script: str) -> str:
    """Helper to run a Lua script via RCON and return the result."""
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            lua_wrapper = (
                f"local status, res = pcall(function() return {script} end); "
                "if not status then rcon.print('LUA ERROR: ' .. tostring(res)) "
                "elseif type(res) == 'table' then rcon.print(helpers.table_to_json(res)) "
                "else rcon.print(tostring(res)) end"
            )
            print(f"[Factorio MCP] Sending command: {script}", file=sys.stderr)
            response = mcr.command(f"/c {lua_wrapper}")
            print(f"[Factorio MCP] Response: {response}", file=sys.stderr)
            return response
    except Exception as e:
        print(f"[Factorio MCP] Error: {e}", file=sys.stderr)
        return f"Error connecting or executing RCON: {e}"

@mcp.tool()
def spawn_ai() -> str:
    """Spawn the AI character if it doesn't already exist."""
    lua_code = "remote.call('ai', 'spawn')"
    return run_lua(lua_code)

@mcp.tool()
def get_position() -> str:
    """Get the current position of the AI character."""
    lua_code = "remote.call('ai', 'get_position')"
    return run_lua(lua_code)

@mcp.tool()
def move_to(x: float, y: float) -> str:
    """Move the AI character to the specified x, y coordinates.
    IMPORTANT: The AI moves in a "dumb" straight line and cannot pathfind around obstacles like trees or cliffs. 
    You MUST use get_surroundings() to identify obstacles in your path. If you get stuck, use mine_entity() to chop down trees or clear the obstruction!
    """
    lua_code = f"remote.call('ai', 'move_to', {x}, {y})"
    return run_lua(lua_code)

@mcp.tool()
def stop_moving() -> str:
    """Stop the AI character from moving."""
    lua_code = "remote.call('ai', 'stop_moving')"
    return run_lua(lua_code)

@mcp.tool()
def get_surroundings(radius: int = 20) -> str:
    """Get entities in the given radius around the AI character."""
    lua_code = f"remote.call('ai', 'get_surroundings', {radius})"
    return run_lua(lua_code)

@mcp.tool()
def mine_entity(x: float, y: float) -> str:
    """Command the AI character to mine the entity at the given coordinates."""
    lua_code = f"remote.call('ai', 'mine_entity', {x}, {y})"
    return run_lua(lua_code)

@mcp.tool()
def get_inventory() -> str:
    """Get the contents of the AI character's main inventory."""
    lua_code = "remote.call('ai', 'get_inventory')"
    return run_lua(lua_code)

@mcp.tool()
def craft(recipe_name: str, count: int = 1) -> str:
    """Command the AI character to craft a recipe. Returns true if crafting started."""
    lua_code = f"remote.call('ai', 'craft_recipe', '{recipe_name}', {count})"
    return run_lua(lua_code)

@mcp.tool()
def build(item_name: str, x: float, y: float, direction: str = "north") -> str:
    """Command the AI character to build an entity at x, y facing direction ('north', 'east', 'south', 'west')."""
    lua_code = f"remote.call('ai', 'build_entity', '{item_name}', {x}, {y}, '{direction}')"
    return run_lua(lua_code)

@mcp.tool()
def take_items(x: float, y: float, item_name: str, count: int) -> str:
    """Take items from a container/furnace/drill at x, y and put them in the AI's inventory. Returns the actual amount taken."""
    lua_code = f"remote.call('ai', 'take_items', {x}, {y}, '{item_name}', {count})"
    return run_lua(lua_code)

@mcp.tool()
def insert_items(x: float, y: float, item_name: str, count: int) -> str:
    """Insert items from the AI's inventory into a container/furnace/machine at x, y. Returns the actual amount inserted."""
    lua_code = f"remote.call('ai', 'insert_items', {x}, {y}, '{item_name}', {count})"
    return run_lua(lua_code)

if __name__ == "__main__":
    mcp.run(transport='stdio')
