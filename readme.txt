============================================================
                   POKÉMON BATTLE SIMULATOR
                           MCP SERVER
============================================================

Overview:
---------
This project implements a Pokémon Battle Simulator MCP server with the following capabilities:

1) Pokémon Data Resource
   - Provides detailed Pokémon information:
     * Base stats (HP, Attack, Defense, Special Attack, Special Defense, Speed)
     * Types (Fire, Water, Grass, etc.)
     * Abilities
     * Moves with power, accuracy, and status effects
     * Evolution chains

2) Battle Simulation Tool
   - Simulates turn-based battles between two Pokémon
   - Implements core mechanics:
     * Type effectiveness multipliers
     * Damage calculation using moves and stats
     * Speed-based turn order
     * Status effects: Paralysis, Burn, Poison
     * Basic ability effects (e.g., immunity, Sturdy, Static)
   - Produces detailed battle logs and determines the winner


Requirements:
--------------
- Python 3.8 or later
- Flask (for API server)
- requests (for external API calls)

Install dependencies using:
   pip install -r requirements.txt


Running the Server:
-------------------
1. Make sure Python and required packages are installed.
2. Run the Flask app by executing:
     python app.py
3. The server listens by default on http://127.0.0.1:5000


Using the API:
--------------
POST /tool/simulate
- Input (JSON):
  {
    "pokemon1": "<name_of_pokemon1>",
    "pokemon2": "<name_of_pokemon2>"
  }

- Response (JSON):
  {
    "winner": "<winning_pokemon_name>",
    "battle_log": [
       "Log lines describing the detailed battle steps..."
    ]
  }

- Returns error if Pokémon names are invalid or missing.


Frontend UI:
------------
- Open the included `index.html` file in a modern browser.
- Enter two Pokémon names (supports autocomplete).
- Click "Simulate Battle" to start the simulation.
- View the battle log, winner, Pokémon sprites, and abilities.

Note: Ensure the Flask server is running and accessible by the frontend to simulate battles.


Project Structure:
------------------
app.py                   - Flask application exposing the simulation API
battle_simulator.py      - Core battle mechanics, status and ability handling
pokemon_data.py          - Utilities for fetching Pokémon data and evolution info from PokeAPI
requirements.txt         - Python dependencies list for easy installation
index.html               - Frontend UI for interacting with the battle simulator


Extending the Project:
---------------------
- Expand battle mechanics with more abilities and move effects.
- Implement AI strategies for selecting moves.
- Improve front-end visuals and animations.
- Optimize data fetching with caching to avoid API rate limits.
- Package as a fully compliant MCP server with detailed LLM query examples.


Troubleshooting:
----------------
- If Pokémon names do not work, verify proper spelling and availability in PokeAPI.
- For CORS issues, ensure your frontend and backend are allowed to communicate (CORS enabled in Flask).
- If the frontend fails to connect, confirm Flask server is running on correct port.
- Consider adding error handling or retries for network/API latency.


Acknowledgements:
-----------------
- Data provided by the PokeAPI (https://pokeapi.co)
- Powered by Flask and Python
- Inspired by the MCP protocol for AI integration


Contact:
---------
For questions or support, please contact nityanama101@gmail.com
