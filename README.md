# Factorio AI Agent

This project provides an AI agent capable of interacting with the world of Factorio through a Model Context Protocol (MCP) server. The project consists of two main components:
1. **Factorio Mod (`ai_character`)**: A custom mod that spawns a controllable AI character and exposes a Lua interface for actions.
2. **FastMCP Server (`mcp_server`)**: A Python-based FastMCP server that connects to Factorio via RCON to execute actions on behalf of an AI model.

## Features

The AI agent can perform a wide range of tasks, giving it strong capabilities to automate base building:

* **Movement**: Navigate the map using coordinate-based movement (`move_to`, `stop_moving`, `get_position`).
* **Sensing**: Understand the local environment by listing nearby entities within a given radius (`get_surroundings`).
* **Mining & Harvesting**: Chop trees, mine rocks, and harvest ores interactively via Factorio's native mining actions (`mine_entity`).
* **Inventory Management**: Check character inventory contents with support for Factorio 1.1 and 2.0 item formats (`get_inventory`).
* **Crafting**: Instruct the character to manually craft recipes from their available ingredients (`craft`).
* **Building**: Place buildings and entities into the world with specific orientations (`build`).
* **Item Transfer**: Seamlessly move items between the character's inventory and various interactable machines (furnaces, assembling machines, containers, mining drills) using `insert_items` and `take_items`.
* **Research**: View available technologies, their costs, the current research queue, and queue up new research (`get_available_research`, `get_research_queue`, `queue_research`).

## Usage

### Mod Installation
1. Install the `ai_character_0.1.0` mod into your Factorio `mods` directory.
2. Ensure you have RCON enabled when starting the Factorio server. You will need to configure `FACTORIO_RCON_PASSWORD` and `FACTORIO_RCON_PORT`.

### Running the MCP Server
1. Navigate to the `mcp_server` directory.
2. Install the required dependencies: `pip install -r requirements.txt`.
3. Set your environment variables (default is localhost:27015 with password "factorio_rcon_password").
4. Run the server, which connects the `FastMCP` tools via standard I/O for use with compatible AI agents.

### Tool Overview
The MCP server exposes the following tools:
- `spawn_ai()`
- `get_position()`
- `move_to(x, y)`
- `stop_moving()`
- `get_surroundings(radius)`
- `mine_entity(x, y)`
- `get_inventory()`
- `craft(recipe_name, count)`
- `build(item_name, x, y, direction)`
- `take_items(x, y, item_name, count)`
- `insert_items(x, y, item_name, count)`
- `get_available_research()`
- `get_research_queue()`
- `queue_research(technology_name)`
