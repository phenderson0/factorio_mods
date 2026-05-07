from mcrcon import MCRcon
import os

RCON_HOST = os.environ.get("FACTORIO_RCON_HOST", "127.0.0.1")
RCON_PORT = int(os.environ.get("FACTORIO_RCON_PORT", "27015"))
RCON_PASSWORD = os.environ.get("FACTORIO_RCON_PASSWORD", "factorio_rcon_password")

print(f"Attempting to connect to RCON at {RCON_HOST}:{RCON_PORT} with password '{RCON_PASSWORD}'...")

try:
    with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
        print("[SUCCESS] Successfully connected to Factorio RCON!")
        
        print("Sending test command: get_surroundings")
        response = mcr.command("/c local res = remote.call('ai', 'get_surroundings'); rcon.print(helpers.table_to_json(res))")
        print(f"[SUCCESS] Response from Factorio: {response}")
        
except ConnectionRefusedError:
    print("[ERROR] Connection Refused.")
    print("This usually means Factorio is not running, or was not started with RCON enabled.")
    print("Make sure you started Factorio from the command line or a shortcut with:")
    print("  factorio.exe --rcon-port 27015 --rcon-password \"factorio_rcon_password\"")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
