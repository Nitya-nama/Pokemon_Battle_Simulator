import requests
import random


TYPE_CHART = {
    'fire': {'grass': 2.0, 'water': 0.5, 'electric': 1.0, 'fire': 0.5},
    'water': {'fire': 2.0, 'grass': 0.5, 'electric': 1.0, 'water': 0.5},
    'grass': {'water': 2.0, 'fire': 0.5, 'grass': 0.5, 'electric': 1.0},
    'electric': {'water': 2.0, 'grass': 0.5, 'fire': 1.0, 'electric': 0.5},
    'normal': {'ghost': 0.0},
    'ghost': {'normal': 0.0}
}

MOVE_POOL = {
    'fire': [
        {'name': 'Flamethrower', 'power': 90, 'accuracy': 1.0, 'status': {'burned': 0.1}},
        {'name': 'Fire Blast', 'power': 110, 'accuracy': 0.85, 'status': {'burned': 0.3}},
        {'name': 'Ember', 'power': 40, 'accuracy': 1.0, 'status': {'burned': 0.1}},
    ],
    'water': [
        {'name': 'Hydro Pump', 'power': 110, 'accuracy': 0.8, 'status': {}},
        {'name': 'Water Gun', 'power': 40, 'accuracy': 1.0, 'status': {}},
        {'name': 'Bubble Beam', 'power': 65, 'accuracy': 1.0, 'status': {}},
    ],
    'grass': [
        {'name': 'Vine Whip', 'power': 45, 'accuracy': 1.0, 'status': {}},
        {'name': 'Razor Leaf', 'power': 55, 'accuracy': 0.95, 'status': {}},
        {'name': 'Leech Seed', 'power': 0, 'accuracy': 0.9, 'status': {'poisoned': 1.0}},  # Using poison to simulate health drain
    ],
    'electric': [
        {'name': 'Thunderbolt', 'power': 90, 'accuracy': 1.0, 'status': {'paralyzed': 0.1}},
        {'name': 'Spark', 'power': 65, 'accuracy': 1.0, 'status': {'paralyzed': 0.3}},
        {'name': 'Thunder Shock', 'power': 40, 'accuracy': 1.0, 'status': {'paralyzed': 0.1}},
    ],
    'normal': [
        {'name': 'Tackle', 'power': 40, 'accuracy': 1.0, 'status': {}},
        {'name': 'Quick Attack', 'power': 40, 'accuracy': 1.0, 'status': {}},
        {'name': 'Headbutt', 'power': 70, 'accuracy': 1.0, 'status': {'paralyzed': 0.05}},
    ],
    'ghost': [
        {'name': 'Shadow Ball', 'power': 80, 'accuracy': 1.0, 'status': {}},
        {'name': 'Lick', 'power': 30, 'accuracy': 1.0, 'status': {'paralyzed': 0.05}},
        {'name': 'Night Shade', 'power': 0, 'accuracy': 1.0, 'status': {}},  # Special move, fixed damage skipped here for simplicity
    ]
}

ABILITY_EFFECTS = {
    'levitate': {'immune_to': ['ground']},  # Example immunity
    'sturdy': {'prevent_ohko': True},  # Prevent 1-hit KO
    'static': {'contact_paralyze_chance': 0.3},  # Chance to paralyze on contact moves
}

class PokemonInBattle:
    def __init__(self, data):
        self.name = data['name']
        self.types = data['types']
        self.hp = data['hp']
        self.max_hp = data['hp']
        self.attack = data['attack']
        self.defense = data['defense']
        self.speed = data['speed']
        self.abilities = data.get('abilities', [])
        self.status = None  # 'paralyzed', 'burned', 'poisoned' or None
        self.status_turns = 0  # Track how many turns status has been applied

    def apply_status_effects(self, log):
        # Paralysis
        if self.status == 'paralyzed':
            log.append(f"⚡ {self.name.capitalize()} is paralyzed and may be unable to move!")
            if random.random() < 0.25:  # 25% chance to skip turn
                log.append(f"❌ {self.name.capitalize()} is fully paralyzed and can't move this turn!")
                return False  # Skip attack this turn
            # Speed reduced - since speed used only to determine first attacker each turn,
            # speed reduction applied when comparing before battle starts, so skip here.

        # Burn effect: lose hp and attack reduced by half each turn
        if self.status == 'burned':
            burn_damage = max(1, self.max_hp // 16)
            self.hp -= burn_damage
            log.append(f"🔥 {self.name.capitalize()} is hurt by its burn and loses {burn_damage} HP!")
            # Burn halves attack stat effect during damage calculation (handled in compute_damage)

        # Poison effect: lose hp each turn without stat changes
        if self.status == 'poisoned':
            poison_damage = max(1, self.max_hp // 8)
            self.hp -= poison_damage
            log.append(f"☠️ {self.name.capitalize()} is hurt by poison and loses {poison_damage} HP!")

        return True  # No skip caused by status effects (except paralysis earlier)

    def is_fainted(self):
        return self.hp <= 0


def get_pokemon_data(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    data = res.json()
    stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
    types = [t['type']['name'] for t in data['types']]
    sprite = data['sprites']['front_default']
    abilities = [ab['ability']['name'] for ab in data['abilities']]
    return {
        'name': data['name'],
        'types': types,
        'attack': stats['attack'],
        'defense': stats['defense'],
        'speed': stats['speed'],
        'hp': stats['hp'],
        'sprite': sprite,
        'abilities': abilities
    }

def get_type_multiplier(attacker_types, defender_types):
    multiplier = 1.0
    for atk in attacker_types:
        for def_ in defender_types:
            effect = TYPE_CHART.get(atk, {}).get(def_, 1.0)
            multiplier *= effect
    return multiplier

def choose_move(types):
    # choose move from first matching type with moves
    for t in types:
        if t in MOVE_POOL:
            return random.choice(MOVE_POOL[t])
    # fallback move if no moves found for types
    return {'name': "Struggle", 'power': 50, 'accuracy': 1.0, 'status': {}}

def check_ability_immunity(attacker_move_type, defender_pokemon):
    """
    Check if defender's abilities provide immunity to this move type.
    Return True if immune, False otherwise.
    """
    for ability in defender_pokemon.abilities:
        ability_details = ABILITY_EFFECTS.get(ability)
        if ability_details and 'immune_to' in ability_details:
            if attacker_move_type in ability_details['immune_to']:
                return True
    return False

def apply_contact_ability(attacker, defender, log):
    """Apply Static ability chance to paralyze attacker if contact move."""
    if 'static' in defender.abilities:
        if random.random() < ABILITY_EFFECTS['static']['contact_paralyze_chance']:
            if attacker.status is None:
                attacker.status = 'paralyzed'
                log.append(f"⚡ {attacker.name.capitalize()} was paralyzed by {defender.name.capitalize()}'s Static ability!")

def simulate_battle(pokemon1_name, pokemon2_name):
    p1_data = get_pokemon_data(pokemon1_name)
    p2_data = get_pokemon_data(pokemon2_name)
    if not p1_data or not p2_data:
        return {"error": "One or both Pokémon not found."}

    p1 = PokemonInBattle(p1_data)
    p2 = PokemonInBattle(p2_data)

    log = []
    log.append(f"🎮 Battle Start! {p1.name.capitalize()} vs {p2.name.capitalize()}!")
    log.append("⚔️ Let the battle begin!\n")

    # Initial speed check with paralysis effect before battle
    # Paralysis cuts Speed by 50%, so applying speed reduction here 
    # if status is paralyzed at the start. Since they do no have status at start, skip.

    # Determine order based on speed; if tie, random choose
    if p1.speed > p2.speed:
        first, second = p1, p2
    elif p2.speed > p1.speed:
        first, second = p2, p1
    else:
        first, second = random.choice([(p1, p2), (p2, p1)])

    log.append(f"⚡ {first.name.capitalize()} is quicker and makes the first move!\n")

    turn = 1
    while not p1.is_fainted() and not p2.is_fainted():
        log.append(f"🌀 Turn {turn} starts!")

        for attacker, defender in [(first, second), (second, first)]:
            if attacker.is_fainted() or defender.is_fainted():
                continue  # Battle ended

            # Apply status effects that might skip turn or damage HP
            can_attack = attacker.apply_status_effects(log)
            if attacker.is_fainted():
                log.append(f"☠️ {attacker.name.capitalize()} has fainted!")
                break
            if not can_attack:
                # Skip attack due to paralysis skip turn
                continue

            # Choose a move for attacker
            move = choose_move(attacker.types)
            move_name = move['name']
            move_power = move['power']
            move_accuracy = move['accuracy']
            move_status = move['status']  # dict like {'burned': 0.1}

            log.append(f"🗡️ {attacker.name.capitalize()} tries to use {move_name}!")

            # Check accuracy
            if random.random() > move_accuracy:
                log.append(f"❌ {attacker.name.capitalize()}'s {move_name} missed!")
                continue

            # Check if defender is immune to this move type by abilities
            # We pick first type of move based on attacker's types
            move_type = attacker.types[0] if attacker.types else 'normal'
            if check_ability_immunity(move_type, defender):
                log.append(f"🚫 {defender.name.capitalize()}'s ability prevents damage from {move_name}!")
                continue

            # Damage calculation:
            # Base damage formula simplified:
            # damage = (((Attack - Defense/2) * Power) * type effectiveness * random_factor * critical)
            # Burn halves attacker Attack when burned
            attack_stat = attacker.attack
            if attacker.status == 'burned':
                attack_stat = int(attack_stat * 0.5)

            base_attack = attack_stat
            base_defense = defender.defense if defender.defense > 0 else 1  # avoid div by zero
            base_damage = max(1, int((base_attack - base_defense / 2) * move_power / 40))

            multiplier = get_type_multiplier(attacker.types, defender.types)
            crit = 2.0 if random.random() < 0.1 else 1.0  # 10% crit chance
            random_factor = random.uniform(0.85, 1.0)

            damage = max(1, int(base_damage * multiplier * crit * random_factor))

            # Apply Sturdy ability: prevent OHKO (damage < hp)
            if 'sturdy' in defender.abilities and damage >= defender.hp and defender.hp == defender.max_hp:
                damage = defender.hp - 1
                log.append(f"🛡️ {defender.name.capitalize()}'s Sturdy ability prevents it from fainting!")

            defender.hp -= damage
            if defender.hp < 0:
                defender.hp = 0

            log.append(f"💥 {attacker.name.capitalize()}'s {move_name} hit {defender.name.capitalize()} for {damage} damage!")

            if multiplier > 1:
                log.append("🔥 It's super effective!")
            elif 0 < multiplier < 1:
                log.append("🧊 It's not very effective...")
            elif multiplier == 0:
                log.append("🚫 It had no effect!")

            if crit > 1.0:
                log.append("💥 A critical hit!")

            log.append(f"🧪 {defender.name.capitalize()} has {defender.hp} HP left.")

            # Apply status effect from move if defender not already statused
            if defender.status is None:
                for status_name, chance in move_status.items():
                    if random.random() < chance:
                        defender.status = status_name
                        defender.status_turns = 0
                        log.append(f"☣️ {defender.name.capitalize()} is now {status_name}!")
                        break

        
            apply_contact_ability(attacker, defender, log)

            if defender.is_fainted():
                log.append(f"☠️ {defender.name.capitalize()} has fainted!")
                break

        turn += 1

    winner = None
    if p1.is_fainted() and p2.is_fainted():
        winner = "Draw"
        log.append("🤝 The battle ended in a draw!")
    elif p1.is_fainted():
        winner = p2.name
        log.append(f"\n🏆 {p2.name.upper()} wins the battle with style!\n🎉🎉🎉")
    elif p2.is_fainted():
        winner = p1.name
        log.append(f"\n🏆 {p1.name.upper()} wins the battle with style!\n🎉🎉🎉")
    else:
        winner = "Unknown"
        log.append("❓ Battle ended unexpectedly.")

    return {
        "winner": winner,
        "battle_log": log
    }

def get_evolution_chain(pokemon_name):
    """
    Fetches evolution chain info for given Pokémon from PokeAPI.
    Returns raw evolution data or None on failure.
    """
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name.lower()}"
    res = requests.get(species_url)
    if res.status_code != 200:
        return None
    species_data = res.json()
    evo_chain_url = species_data['evolution_chain']['url']
    evo_res = requests.get(evo_chain_url)
    if evo_res.status_code != 200:
        return None
    evo_data = evo_res.json()
    return evo_data

if __name__ == "__main__":
    import pprint
    battle_result = simulate_battle("pikachu", "bulbasaur")
    pprint.pprint(battle_result["battle_log"])
    print("Winner:", battle_result["winner"])
