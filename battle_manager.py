import battle
from logger import logger
from console_writer import log
import time
from globals import GLOBAL_BATTLE_LOG, uuid

def create_battle_instance(martial_artist_1, martial_artist_2, battle_regulations=None):
    """
    Create a battle instance with the given martial artists and battle regulations.
    
    Args:
        martial_artist_1 (MartialArtist): The first martial artist.
        martial_artist_2 (MartialArtist): The second martial artist.
        battle_regulations (str, optional): The battle regulations. Defaults to None.
    
    Returns:
        Battle: A new Battle instance.
    """
    return battle.Battle(martial_artist_1, martial_artist_2, battle_regulations=battle_regulations)

def create_duel_brackets(martial_artists, battle_regulations=None):
    """
    Create duel brackets for a list of martial artists.
    
    Args:
        martial_artists (list): A list of martial artists.
        battle_regulations (str, optional): The battle regulations. Defaults to None.
    
    Returns:
        list: A list of Battle instances representing the duel brackets.
    """
    brackets = {}
    spaced_artist = None
    martial_artists_list = list(martial_artists.values())
    if len(martial_artists) < 2:
        logger.execute("Battle Error", "error", "Not enough martial artists to create duel brackets.")
        return ValueError("Not enough martial artists to create duel brackets.")
    if len(martial_artists) % 2 != 0:
        spaced_artist = next(iter(martial_artists.values()))
        if isinstance(spaced_artist, dict):
            spaced_artist = spaced_artist["object"]
        martial_artists.pop(spaced_artist.name)
        martial_artists_list = list(martial_artists.values()) #Rewrite the list to remove the spaced artist
    
    for i in range(0, len(martial_artists), 2):
        m1 = martial_artists_list[i]
        m2 = martial_artists_list[i + 1]
        battle_instance = create_battle_instance(m1, m2, battle_regulations=battle_regulations)
        bracket_id = generate_bracket_id()
        brackets[bracket_id] = battle_instance
        log.info(f"{bracket_id} created between {m1.name} and {m2.name}.")
    
    return brackets, spaced_artist if spaced_artist else None


def execute_brackets(martial_list, battle_regulations=None):
    """
    Execute the duel brackets and manage the battles.
    
    Args:
        martial_list (list): A list of martial artists.
        battle_regulations (str, optional): The battle regulations. Defaults to None.
    
    Returns:
        None
    """
    next_fighters = {}
    
    brackets, spaced_artist = create_duel_brackets(martial_list, battle_regulations=battle_regulations)
    for bracket_name, battle_instance in brackets.items():
        log.info(f"Starting {bracket_name} between {battle_instance.martial_first.name} and {battle_instance.martial_second.name}.")
        battle_instance.start_battle()
        while not battle_instance.flag_end:
            time.sleep(0.1)
        winner = search_for_winner(battle_instance)
        next_fighters[winner.name] = winner
    if spaced_artist:
        next_fighters[spaced_artist.name] = spaced_artist
    if len(next_fighters) == 1:
        return next_fighters, "Yes"
    if len(next_fighters) > 1:
        return next_fighters, "No"
    if len(next_fighters) == 0:
        log.error("No martial artists left in the brackets.")
        logger.execute("Battle Error", "error", "No martial artists left in the brackets.")
        return ValueError("No martial artists left in the brackets.")
    
def search_for_winner(battle_instance:battle.Battle):
    """
    Search for the winner of a battle instance.
    
    Args:
        battle_instance (Battle): The battle instance.
    
    Returns:
        instance: The object of the winner.
    """
    if battle_instance.battle_id not in GLOBAL_BATTLE_LOG:
        logger.execute("Battle Error", "error", "Battle ID not found in the global battle log.")
        return ValueError("Battle ID not found in the global battle log.")
    participants = GLOBAL_BATTLE_LOG[battle_instance.battle_id]["participants"]
    if participants[battle_instance.martial_first.name]["identifier"] == "winner":
        return participants[battle_instance.martial_first.name]["object"]
    else:
        return participants[battle_instance.martial_second.name]["object"]

def generate_bracket_id():
    """
    Generate a unique bracket ID.
    
    Returns:
        str: A unique bracket ID.
    """
    return str(uuid.uuid4())

def manage_brackets(martial_list, battle_regulations=None):
    """
    Manage the duel brackets and start the battles.
    
    Args:
        martial_list (list): A list of martial artists.
        battle_regulations (str, optional): The battle regulations. Defaults to None.
    
    Returns:
        None
    """
    while True:
        next_fighters, is_final = execute_brackets(martial_list, battle_regulations=battle_regulations)
        if is_final == "Yes":
            winner = next(iter(next_fighters.values()))
            log.info(f"{winner.name} is the final winner of the tournament.")
            return winner
        martial_list = next_fighters
        time.sleep(0.3)
    