import numpy as np
from core.martial_artist_definition import MartialArtist
from utils.max_values import MAX_VALUE_STATUS, MAX_VALUE_SYS, TALENT_MAX_VALUE, CULTIVATION_MAX_LEVEL, MAX_TECHNIQUE_TIER
from utils.world_avaliations import global_vector
from core.node_map import NodeMap
from core.globals import NODE_TYPES
from core.radar import Radar
artist_fields = [
    "health", "energy", "cultivation", "realm", "avg_technique_tier",
    "avg_stats", "artist_talent", "str", "dex", "con", "int", "wis", "cha",
    "total_health", "total_energy"
]

attribute_paths = [
    "qi", "vitality", "strength", "dexterity", "intelligence",
    "charisma", "constitution", "wisdom", "cultivation level", "talent"
]

def get_artist_vector(artist:MartialArtist, map:NodeMap):
    
    next_realm, next_realm_name = artist._get_next_cultivation_realm()
    
    health = min(artist.max_vitality/artist.vitality, 1)
    energy = min(artist.max_qi/artist.qi, 1)
   
    total_health = min(artist.vitality/MAX_VALUE_SYS, 1)
    total_energy = min(artist.qi/MAX_VALUE_SYS, 1)
    
    realm = min(artist.realm["Cultivation Level"] / CULTIVATION_MAX_LEVEL, 1)
    cultivation = artist.qi / next_realm["Qi Requirement"] if artist.qi / next_realm["Qi Requirement"] < 1 else 1
    
    avg_stats = min(artist.get_stat_avg() / (MAX_VALUE_STATUS * 6), 1)
    avg_technique_tier = min(artist.get_avg_tier() / (MAX_TECHNIQUE_TIER * 3), 1)
    artist_talent = min(artist.talent/TALENT_MAX_VALUE, 1)
    
    #Map Related Vectors
    position_vector = np.array([artist.coords[0] / map.grid_size["x"], artist.coords[1] / map.grid_size["y"]]) #Divide the coords from the artists(coords is a tuple) with the map grid size from the map
    position_node_type = node_one_hot(map.find_node_type(artist.coords))
    
    #Stat block Vectors
    str_ = min(artist.strength/MAX_VALUE_STATUS, 1)
    dex_ = min(artist.dexterity/MAX_VALUE_STATUS, 1)
    con_ = min(artist.constitution/MAX_VALUE_STATUS, 1)
    int_ = min(artist.intelligence/MAX_VALUE_STATUS, 1)
    wis_ = min(artist.wisdom/MAX_VALUE_STATUS, 1)
    cha_ = min(artist.charisma/MAX_VALUE_STATUS, 1)
    
    artist_vector = np.array([
        health,
        energy,
        cultivation,
        realm,
        avg_technique_tier,
        avg_stats,
        artist_talent,
        str_,
        dex_,
        con_,
        int_,
        wis_,            
        cha_,
        total_health,
        total_energy,
        position_vector[0],
        position_vector[1],
    ], dtype=np.float32)

    avg_vector = global_vector(attribute_paths)
    
    vector = np.concatenate([artist_vector, avg_vector, position_node_type]) 
    assert vector.dtype == np.float32
    return vector

_STATE_SIZE = 17 + len(attribute_paths)

def create_attribute_id():
    fields_ids = {}
    for i, name in enumerate(artist_fields):
        fields_ids[name] = i
    
    offset = len(artist_fields)
    
    for i, name in enumerate(attribute_paths):
        fields_ids[name] = offset + i
    return fields_ids

attribute_ids = create_attribute_id()

def node_one_hot(node_type: str, node_types=NODE_TYPES):
    one_hot = np.zeros(len(node_types), dtype=np.float32)
    if node_type in node_types:
        idx = node_types.index(node_type)
        one_hot[idx] = 1.0
    return one_hot

def radar_to_vector(radar: Radar):
    radar.scan()
    types = {"city": 0, "sect": 1, "ally": 2, "enemy": 3}
    counts = np.zeros(len(types), dtype=np.float32)
    
    for obj in radar.objects.values():
        kind = obj.type
        
        if kind == "artist":
            relation = obj.relations.get(radar.artist.name)
            if relation:
                if relation["intensity"] <= -100:
                    counts[types["enemy"]] += 1.0
                elif relation["intensity"] >= 100:
                    counts[types["ally"]] += 1.0
            continue
        
        if kind in types:
            counts[types[kind]] += 1.0
        
    max_possible = radar.detection_range ** 2
    counts /= max(1.0, max_possible)
    
    return counts    
    