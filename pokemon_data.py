import requests

def get_pokemon_info(name_or_id):
    """
    Fetches detailed Pokémon info including base stats, types, abilities,
    moves (with power, accuracy, and effects), and evolution chain data.
    """

    # Basic Pokémon data: stats, types, abilities, moves
    url = f"https://pokeapi.co/api/v2/pokemon/{name_or_id.lower()}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()

    # Base stats
    stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}

    # Types (list of strings)
    types = [t["type"]["name"] for t in data["types"]]

    # Abilities (list of names)
    abilities = [ab["ability"]["name"] for ab in data["abilities"]]

    # Moves with details: fetch power, accuracy, and status effects from move endpoint
    moves = []
    for move_entry in data["moves"]:
        move_name = move_entry["move"]["name"]
        move_url = move_entry["move"]["url"]
        move_data = requests.get(move_url).json()
        power = move_data.get("power")
        accuracy = move_data.get("accuracy")
        # Extract status effect chance if any (from effect entries)
        effect_chance = None
        effect_status = None

        # Sometimes the effect is nested in effect entries with conditions
        for effect_entry in move_data.get("effect_entries", []):
            if effect_entry.get("language", {}).get("name") == "en":
                effect_text = effect_entry.get("effect", "")
                # Attempt to parse common status keywords
                if "paralyze" in effect_text.lower():
                    effect_status = "paralyzed"
                elif "burn" in effect_text.lower():
                    effect_status = "burned"
                elif "poison" in effect_text.lower():
                    effect_status = "poisoned"

        # Effect chance is sometimes a separate field
        effect_chance = move_data.get("effect_chance")  # percent integer, e.g. 30 means 30%

        # Convert effect_chance to decimal probability if available
        chance_float = effect_chance / 100 if effect_chance else None

        move_info = {
            "name": move_name,
            "power": power,
            "accuracy": accuracy,
            "status": {effect_status: chance_float} if effect_status and chance_float else {}
        }
        moves.append(move_info)


    species_url = data["species"]["url"]
    species_data = requests.get(species_url).json()
    evo_chain_url = species_data.get("evolution_chain", {}).get("url")
    evolution_chain = None
    if evo_chain_url:
        evo_res = requests.get(evo_chain_url).json()
        evolution_chain = parse_evolution_chain(evo_res.get("chain"))

    return {
        "name": data["name"],
        "types": types,
        "stats": stats,
        "abilities": abilities,
        "moves": moves,
        "evolution_chain": evolution_chain
    }

def parse_evolution_chain(chain_node):
    """
    Recursive helper to parse evolution chain data into a nested dictionary.
    """
    if not chain_node:
        return None
    evo = {
        "species_name": chain_node["species"]["name"],
        "evolves_to": []
    }
    for next_evo in chain_node["evolves_to"]:
        evo["evolves_to"].append(parse_evolution_chain(next_evo))
    return evo


if __name__ == "__main__":
    import pprint
    name = "pikachu"
    info = get_pokemon_info(name)
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(info)
