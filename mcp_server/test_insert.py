import sys
sys.path.append('c:/Users/pjack/factorio_mods/mcp_server')
import server

lua_script = """
local status, err = pcall(function()
    local char = storage.ai_character
    if not char then return "no char" end
    local inv = char.get_inventory(defines.inventory.character_main)
    local r1 = inv.insert({name="wooden-chest", count=1})
    local r2 = inv.insert({name="coal", count=10})
    return "Inserted: " .. tostring(r1) .. ", " .. tostring(r2)
end)
if not status then return "ERROR: " .. tostring(err) end
return err
"""

print(server.run_lua(lua_script))
