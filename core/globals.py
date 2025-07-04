from utils.logger import logger
from utils.console_writer import log
import json
import math
import random
import gc
import battle_src.effect_manager as effect_manager
import time
import uuid
import os
from typing import Set

def load_json(filename="./json/builds.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.execute("Error in Json Decoding", "aviso", f"Failed to load or parse the JSON file. - Filename: {filename}")
        return {}


def calculate_odds(martial):
    cultivation_weight = round((1 *martial.realm['Multiplier']) * 0.6)
    qi_weight = martial.max_qi * 0.2
    battle_stats_weight = (martial.strength + martial.dexterity + martial.constitution + martial.wisdom) * 0.1
    experiencie_weight = (martial.wins - martial.losses) * 0.1 
            
    return cultivation_weight + qi_weight + battle_stats_weight + experiencie_weight

def is_empty_dict(d):
    return not bool(d)

def get_rival_element(element1, element2):
    """Element1 will ever be the primary element and element2 the secondary.
        Returns: element_superiority, the multiplier to calculate the damage.
    """
    element_superiority = 0
    element_block = {
        "earth": {"weakness": {"water", "ice", "nature", "metal"}, "strong": {"fire", "lightning"}},
        "water": {"weakness": {"lightning", "nature", "metal"}, "strong": {"fire", "earth"}},
        "fire": {"weakness": {"water", "earth"}, "strong": {"ice", "nature", "metal"}},
        "nature": {"weakness": {"fire", "ice", "metal"}, "strong": {"water", "earth"}},
        "lightning": {"weakness": {"earth"}, "strong": {"water", "metal"}},
        "ice": {"weakness": {"fire"}, "strong": {"nature", "earth"}},
        "metal": {"weakness": {"fire", "lightning"}, "strong": {"nature", "earth", "water"}}
}

    if element1 in element_block:
        if element2 in element_block[element1]["weakness"]:
            element_superiority = 0.70
            return element_superiority
        elif element2 in element_block[element1]["strong"]:
            element_superiority = 1.30
            return element_superiority
        else:
            element_superiority = 1
            return element_superiority


def transcribe_battle_log(winner, loser, battle_object):
    
    GLOBAL_BATTLE_LOG[battle_object.battle_id] = {
        "action_replay": battle_object.action_replay,
        "participants": {
            f"{winner.name}": {"object": winner, "identifier": "winner"},
            f"{loser.name}": {"object": loser, "identifier": "loser"},
        },
        "battle_object": battle_object,
    }
    
    winner.battle_record[f"Winner: {winner.name} vs. Loser: {loser.name}"] = {"action_replay": battle_object.action_replay}
    loser.battle_record[f"Winner: {winner.name} vs. Loser: {loser.name}"] = {"action_replay": battle_object.action_replay}
    
    correct_win_loss(winner, loser)
    
    
def correct_win_loss(winner, loser):
    winner.wins += 1
    loser.losses += 1
    return

def pairwise(iterable, step=2):
    items = list(iterable)
    for i in range(0, len(items), step):
        yield items[i:i+step]
    

def find_entry(value:str, nested_dict:dict):
    for c in nested_dict.values():
        if value in c:
            return c[value]
    return None

def search_dict(root_dir):
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            logger.execute(f"{item_path}", "sucesso", f"Directory Found {item_path}")
            search_dict(item_path)

def search_id(id):
    return MARTIAL_WORLD_LIST[id] if id in MARTIAL_WORLD_LIST else 0

ONGOING_BATTLES = {}
MARTIAL_WORLD_LIST = {}
SECT_WORLD_LIST = {}
SECT_BATTLE_LIST = {}
GLOBAL_BATTLE_LOG = {}
DONE_TRADES = {}
cities = {}
BUILD_SLOTS_DICT = load_json()
GLOBAL_BUILD_OBJECTS = {}
regions = load_json(filename="./json/regions.json")
techniques = load_json(filename="./json/techniques.json")
items = load_json(filename="./json/items.json")
resources_weight = load_json(filename="./json/resources.json")
realms_JSON = load_json(filename="./json/realms_list.json")
value_backups = {}
techniques_objects = {}
global_effect_manager = effect_manager.EffectManager()
WORLD_MAP = None
_USED_IDS: Set[str] = set()
NODE_TYPES = ["city", "sect"]