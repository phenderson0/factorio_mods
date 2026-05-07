-- control.lua
-- This script manages the AI character and exposes RCON-callable remote functions.

local function init_ai_character()
    local surface = game.surfaces["nauvis"]
    if not surface then return end
    
    -- Find a safe spot near origin
    local safe_pos = surface.find_non_colliding_position("character", {0, 0}, 100, 1) or {0,0}
    
    storage.ai_character = surface.create_entity{
        name = "character",
        position = safe_pos,
        force = "player"
    }
end

script.on_init(function()
    init_ai_character()
end)

script.on_event(defines.events.on_tick, function(event)
    local char = storage.ai_character
    if not (char and char.valid) then return end
    
    -- Handle Movement
    if storage.target_position then
        local pos = char.position
        local tx = storage.target_position.x
        local ty = storage.target_position.y
        local dx = tx - pos.x
        local dy = ty - pos.y
        local dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0.5 then
            local direction = defines.direction.north
            if math.abs(dx) > math.abs(dy) * 2 then
                direction = dx > 0 and defines.direction.east or defines.direction.west
            elseif math.abs(dy) > math.abs(dx) * 2 then
                direction = dy > 0 and defines.direction.south or defines.direction.north
            else
                if dx > 0 and dy > 0 then direction = defines.direction.southeast
                elseif dx > 0 and dy < 0 then direction = defines.direction.northeast
                elseif dx < 0 and dy > 0 then direction = defines.direction.southwest
                else direction = defines.direction.northwest end
            end
            
            char.walking_state = {walking = true, direction = direction}
        else
            char.walking_state = {walking = false}
            storage.target_position = nil
        end
    end

    -- Mining is now handled instantly via mine_entity call
end)

remote.add_interface("ai", {
    spawn = function()
        if not (storage.ai_character and storage.ai_character.valid) then
            init_ai_character()
            return true
        end
        return false
    end,

    get_position = function()
        if storage.ai_character and storage.ai_character.valid then
            return storage.ai_character.position
        end
        return nil
    end,
    
    move_to = function(x, y)
        if storage.ai_character and storage.ai_character.valid then
            storage.target_position = {x = x, y = y}
            return true
        end
        return false
    end,
    
    stop_moving = function()
        storage.target_position = nil
        if storage.ai_character and storage.ai_character.valid then
            storage.ai_character.walking_state = {walking = false}
        end
        return true
    end,

    get_surroundings = function(radius)
        if not (storage.ai_character and storage.ai_character.valid) then return {} end
        local r = radius or 20
        local pos = storage.ai_character.position
        local entities = storage.ai_character.surface.find_entities_filtered{
            area = {{pos.x - r, pos.y - r}, {pos.x + r, pos.y + r}}
        }
        local result = {}
        for _, ent in pairs(entities) do
            -- Ignore characters or trivial things to save output space
            if ent.type ~= "character" and ent.type ~= "particle" then
                table.insert(result, {
                    name = ent.name,
                    type = ent.type,
                    position = ent.position,
                    force = ent.force.name
                })
            end
        end
        return result
    end,
    
    mine_entity = function(x, y)
        if storage.ai_character and storage.ai_character.valid then
            local surface = storage.ai_character.surface
            -- Search in a small radius around the target point
            local ents = surface.find_entities_filtered{
                area = {{x - 1.5, y - 1.5}, {x + 1.5, y + 1.5}}
            }
            local closest = nil
            local min_dist = 1000
            
            for _, ent in pairs(ents) do
                if ent.valid and ent.minable and ent.prototype.mineable_properties.minable then
                    local dist = (ent.position.x - x)^2 + (ent.position.y - y)^2
                    if dist < min_dist then
                        min_dist = dist
                        closest = ent
                    end
                end
            end
            
            if closest then
                return storage.ai_character.mine_entity(closest, false)
            end
        end
        return false
    end,

    get_inventory = function()
        if not (storage.ai_character and storage.ai_character.valid) then return {} end
        local inv = storage.ai_character.get_inventory(defines.inventory.character_main)
        if not inv then return {} end
        local contents = inv.get_contents()
        local result = {}
        -- Factorio 1.1/2.0 get_contents returns a dict/array depending on version
        for k, v in pairs(contents) do
            if type(v) == "number" then
                -- Factorio 1.1: {["iron-plate"] = 5}
                table.insert(result, {name = k, count = v})
            elseif type(v) == "table" or type(v) == "userdata" then
                -- Factorio 2.0: {{name="iron-plate", count=5}}
                if v.name then
                    table.insert(result, {name = v.name, count = v.count})
                end
            end
        end
        return result
    end,

    craft_recipe = function(recipe_name, count)
        if not (storage.ai_character and storage.ai_character.valid) then return false end
        -- Characters can craft natively if they have ingredients
        local success = storage.ai_character.begin_crafting{count = count or 1, recipe = recipe_name}
        if success and success > 0 then
            return true
        end
        return false
    end,

    build_entity = function(item_name, x, y, direction_str)
        if not (storage.ai_character and storage.ai_character.valid) then return false end
        local char = storage.ai_character
        local surface = char.surface
        
        local inv = char.get_inventory(defines.inventory.character_main)
        if not inv or inv.get_item_count(item_name) == 0 then
            return false -- Missing item
        end
        
        -- Approximate distance check
        local dist = math.sqrt((char.position.x - x)^2 + (char.position.y - y)^2)
        if dist > 15 then
            return false -- Too far
        end

        local dir_map = {
            north = defines.direction.north,
            east = defines.direction.east,
            south = defines.direction.south,
            west = defines.direction.west
        }
        local dir = dir_map[direction_str] or defines.direction.north

        local can_place = surface.can_place_entity{
            name = item_name, 
            position = {x, y}, 
            direction = dir,
            force = char.force,
            build_check_type = defines.build_check_type.manual_for_player
        }
        
        if can_place then
            local built = surface.create_entity{
                name = item_name,
                position = {x, y},
                direction = dir,
                force = char.force,
                raise_built = true
            }
            if built then
                inv.remove({name = item_name, count = 1})
                return true
            end
        end
        return false
    end,

    take_items = function(x, y, item_name, count)
        if not (storage.ai_character and storage.ai_character.valid) then return 0 end
        local char = storage.ai_character
        local surface = char.surface
        
        local dist = math.sqrt((char.position.x - x)^2 + (char.position.y - y)^2)
        if dist > 15 then return 0 end
        
        local ents = surface.find_entities_filtered{area={{x-0.5, y-0.5}, {x+0.5, y+0.5}}}
        local target = nil
        for _, ent in pairs(ents) do
            if ent.get_item_count(item_name) > 0 then
                target = ent
                break
            elseif ent.type == "container" or ent.type == "furnace" or ent.type == "mining-drill" then
                target = ent
            end
        end
        if not target then return 0 end
        
        local removed = target.remove_item({name=item_name, count=count})
        if removed > 0 then
            local inserted = char.insert({name=item_name, count=removed})
            if inserted < removed then
                target.insert({name=item_name, count=removed - inserted})
            end
            return inserted
        end
        return 0
    end,

    insert_items = function(x, y, item_name, count)
        if not (storage.ai_character and storage.ai_character.valid) then return 0 end
        local char = storage.ai_character
        local surface = char.surface
        
        local dist = math.sqrt((char.position.x - x)^2 + (char.position.y - y)^2)
        if dist > 15 then return 0 end
        
        local ents = surface.find_entities_filtered{area={{x-0.5, y-0.5}, {x+0.5, y+0.5}}}
        local target = nil
        for _, ent in pairs(ents) do
            if ent.type == "container" or ent.type == "furnace" or ent.type == "mining-drill" or ent.type == "assembling-machine" then
                target = ent
                break
            end
        end
        if not target then return 0 end
        
        local available = char.get_item_count(item_name)
        local to_insert = math.min(count, available)
        if to_insert <= 0 then return 0 end
        
        local removed = char.remove_item({name=item_name, count=to_insert})
        if removed > 0 then
            local inserted = target.insert({name=item_name, count=removed})
            if inserted < removed then
                char.insert({name=item_name, count=removed - inserted})
            end
            return inserted
        end
        return 0
    end
})
