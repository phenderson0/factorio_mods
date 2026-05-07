import sys
import os
import json
import time

# Ensure the mcp_server directory is in path so we can import server
sys.path.append(os.path.dirname(__file__))

import server

def print_result(tool_name, result):
    if result.strip() == "":
        print(f"[ERROR] {tool_name} returned an empty string! (This usually means a Lua error occurred in-game)")
    elif "LUA ERROR" in result:
        print(f"[LUA ERROR] {tool_name} -> {result.strip()}")
    else:
        print(f"[SUCCESS] {tool_name} -> {result.strip()[:100]}...")

print("--- FACTORIO AI DYNAMIC TEST SUITE ---")
print("Make sure Factorio is running and hosting a multiplayer game.")
time.sleep(1)

print("\n1. Spawning AI...")
server.spawn_ai()
print("[SUCCESS] AI Spawn command sent.")

print("\n2. Getting Position...")
pos_str = server.get_position()
print_result("get_position", pos_str)
pos = json.loads(pos_str)

print("\n3. Getting Surroundings...")
surr_str = server.get_surroundings(radius=100)
surroundings = json.loads(surr_str)
print(f"[SUCCESS] Found {len(surroundings)} entities nearby.")

print("\n4. Testing Mining (Dynamic: Nearest Tree/Rock)...")
mine_target = None
min_dist = float('inf')

for ent in surroundings:
    # Try to find a tree or rock specifically
    name = ent['name']
    if ("tree" in name and "stump" not in name) or "rock" in name or "stone" in name:
        dist = (ent['position']['x'] - pos['x'])**2 + (ent['position']['y'] - pos['y'])**2
        if dist < min_dist:
            min_dist = dist
            mine_target = ent

if mine_target:
    print(f"Nearest minable found: {mine_target['name']} at ({mine_target['position']['x']:.2f}, {mine_target['position']['y']:.2f})")
    dist = ((mine_target['position']['x'] - pos['x'])**2 + (mine_target['position']['y'] - pos['y'])**2)**0.5
    walk_time = (dist / 5.0) + 1 # ~5 tiles per second + 1 sec buffer
    print(f"Moving to the tree (dist: {dist:.1f}, waiting {walk_time:.1f}s)...")
    server.move_to(mine_target['position']['x'], mine_target['position']['y'])
    
    # Wait for the character to walk there
    time.sleep(walk_time)
    server.stop_moving()
    
    print("Chopping it down...")
    res = server.mine_entity(mine_target['position']['x'], mine_target['position']['y'])
    print_result("mine_entity", res)
    
    # Wait a tiny bit just in case
    time.sleep(2)
else:
    print("[SKIP] No trees found in surroundings.")

print("\n5. Testing Building (Dynamic)...")
# Ensure we have a wooden-chest and some coal to test with
server.run_lua('game.surfaces[1].find_entities_filtered{name="character"}[1].insert({name="wooden-chest", count=1})')
server.run_lua('game.surfaces[1].find_entities_filtered{name="character"}[1].insert({name="coal", count=10})')

inv_str = server.get_inventory()
inventory = json.loads(inv_str)
build_item = None
if inventory:
    # Pick first item in inventory to build. NOTE: We can't build raw ores/wood, need a placeable item.
    for item in inventory:
        if item['name'] not in ["stone", "coal", "wood", "iron-ore", "copper-ore"]:
            build_item = item['name']
            break

if build_item:
    # Try to build it near the player's NEW position
    pos_str2 = server.get_position()
    pos2 = json.loads(pos_str2)
    import math
    bx = math.floor(pos2['x']) + 2
    by = math.floor(pos2['y']) + 2
    print(f"Attempting to build {build_item} at ({bx}, {by})")
    res = server.build(build_item, bx, by, "north")
    print_result("build", res)
    
    # If build succeeded, test container interaction
    if "true" in res:
        print("\n6. Testing Container Interaction (Dynamic)...")
        print(f"Inserting 5 coal into {build_item}...")
        res = server.insert_items(bx, by, "coal", 5)
        print_result("insert_items", res)
        
        print(f"Taking coal back from {build_item}...")
        res = server.take_items(bx, by, "coal", 5)
        print_result("take_items", res)
else:
    print("[SKIP] Inventory empty, cannot test building.")

print("\n7. Moving AI to (10, 10)...")
res = server.move_to(10, 10)
print_result("move_to", res)

print("\n--- TEST COMPLETE ---")
