import sys
sys.path.append('c:/Users/pjack/factorio_mods/mcp_server')
import server

lua_script = """
local items = game.surfaces[1].find_entities_filtered{type="item"}
local result = ""
for _, item in pairs(items) do
    result = result .. item.stack.name .. ": " .. item.stack.count .. " at " .. item.position.x .. "," .. item.position.y .. " | "
end
return result
"""
print("Items on ground:", server.run_lua(lua_script))
