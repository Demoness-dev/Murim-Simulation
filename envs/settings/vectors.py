import numpy as np
from core.martial_artist_definition import MartialArtist
from utils.max_values import MAX_VALUE_STATUS, MAX_VALUE_SYS, TALENT_MAX_VALUE, CULTIVATION_MAX_LEVEL, MAX_TECHNIQUE_TIER
from utils.world_avaliations import global_vector
from core.node_map import NodeMap
from core.globals import NODE_TYPES, WORLD_MAP, MARTIAL_WORLD_LIST
from core.radar import Radar
from settings.counter import MAX_ARTIST, MAX_OBJECTS
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
    
    avg_stats = min(artist.get_stat_avg() / (MAX_VALUE_STATUS), 1)
    avg_technique_tier = min(artist.get_avg_tier() / (MAX_TECHNIQUE_TIER), 1)
    artist_talent = min(artist.talent/TALENT_MAX_VALUE, 1)
    
    #Map Related Vectors
    position_vector = np.array([artist.coords[0] / map.grid_size["x"], artist.coords[1] / map.grid_size["y"]]) #Divide the coords from the artists(coords is a tuple) with the map grid size from the map
    position_node_type = node_one_hot(map.find_node_type(artist.coords))
    
    radar, rel_pos, artist_array = radar_to_vector(artist.radar)
    
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
    
    vector = np.concatenate([artist_vector, avg_vector, position_node_type, radar, rel_pos, artist_array]) 
    assert vector.dtype == np.float32
    return vector

def get_state_size():
    burner_vector = get_artist_vector(next(iter(MARTIAL_WORLD_LIST.values())), WORLD_MAP)
    return len(burner_vector)

_STATE_SIZE = get_state_size()

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

def radar_to_vector(radar: Radar, max_objects = MAX_OBJECTS, max_artist = MAX_ARTIST):
    radar.scan()
    types = {"city": 0, "sect": 1, "ally": 2, "enemy": 3}
    counts = np.zeros(len(types), dtype=np.float32)
    artist_info = []
    rel_positions = []
    
    for obj in radar.objects.values():
        kind = obj.type
        dx = (obj.coords[0] - radar.artist.coords[0]) / radar.detection_range
        dy = (obj.coords[1] - radar.artist.coords[1]) / radar.detection_range
        dx = np.clip(dx, -1, 1)
        dy = np.clip(dy, -1, 1)
        if kind == "artist":
            relation = obj.relations.get(radar.artist.name)
            if relation:
                if relation["intensity"] <= -100:
                    counts[types["enemy"]] += 1.0
                    rel_positions.append([dx, dy, types["enemy"]])
                elif relation["intensity"] >= 100:
                    counts[types["ally"]] += 1.0
                    rel_positions.append([dx, dy, types["ally"]])
                #Artist Data.
                normalized_qi = min(getattr(obj, "qi", 0) / MAX_VALUE_SYS , 1)
                stat_avg = getattr(obj, "get_stat_avg", lambda: 0 )()
                normalized_stat_avg = min(stat_avg / MAX_VALUE_STATUS, 1)
                normalized_talent = min(getattr(obj, "talent", 0 ) / TALENT_MAX_VALUE, 1)
                avg_tier = getattr(obj, "get_avg_tier", lambda: 0)()
                normalized_tier = min(avg_tier/MAX_TECHNIQUE_TIER, 1)
                
                threat_score = (
                    normalized_qi * 0.3 + 
                    normalized_stat_avg * 0.3 +
                    normalized_talent * 0.2 +
                    normalized_tier + 0.2
                )
                
                artist_info.append([dx, dy, normalized_qi, threat_score])
            continue
        
        if kind in types:
            counts[types[kind]] += 1.0
            rel_positions.append([dx, dy, types[kind]])
    total = counts.sum()
    if total > 0:
        counts /= total
    
    while len(rel_positions) < max_objects:
        rel_positions.append([0.0, 0.0, -1.0])
    rel_positions = rel_positions[:max_objects]
    
    rel_array = np.array(rel_positions, dtype=np.float32).flatten()
    
    while len(artist_info) < max_artist:
        artist_info.append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    artist_info = artist_info[:max_artist]
    artist_array = np.array(artist_info, dtype=np.float32).flatten()
    return counts, rel_array, artist_array