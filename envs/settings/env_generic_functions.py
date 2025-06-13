import numpy as np
from core.martial_artist_definition import MartialArtist
from utils.max_values import MAX_VALUE_STATUS, MAX_VALUE_SYS, TALENT_MAX_VALUE, CULTIVATION_MAX_LEVEL, MAX_TECHNIQUE_TIER
from utils.world_avaliations import global_vector


attribute_paths = [
    "qi", "vitality", "strength", "dexterity", "intelligence",
    "charisma", "constitution", "wisdom", "cultivation level", "talent"
]

def get_artist_vector(artist:MartialArtist):
    
    next_realm, next_realm_name = artist._get_next_cultivation_realm()
    
    health = artist.max_vitality/artist.vitality
    energy = artist.max_qi/artist.qi
   
    total_health = artist.vitality/MAX_VALUE_SYS
    total_energy = artist.qi/MAX_VALUE_SYS
    
    realm = artist.realm["Cultivation Level"] / CULTIVATION_MAX_LEVEL
    cultivation = artist.qi / next_realm["Qi Requirement"] if artist.qi / next_realm["Qi Requirement"] < 1 else 1
    
    avg_stats = artist.get_stat_avg() / (MAX_VALUE_STATUS * 6)
    avg_technique_tier = artist.get_avg_tier() / (MAX_TECHNIQUE_TIER * 3)
    talent = artist.talent/TALENT_MAX_VALUE
    
    
    #Stat block Vectors
    str = artist.strength/MAX_VALUE_STATUS
    dex = artist.dexterity/MAX_VALUE_STATUS
    con = artist.constitution/MAX_VALUE_STATUS
    intt = artist.intelligence/MAX_VALUE_STATUS
    wis = artist.wisdom/MAX_VALUE_STATUS
    cha = artist.charisma/MAX_VALUE_STATUS
    
    #Averages
    
    
    artist_vector = np.array([           #IDs
        health,                 #0
        energy,                 #1
        cultivation,            #2
        realm,                  #3
        avg_technique_tier,     #4
        avg_stats,              #5
        talent,                 #6
        str,                    #7
        dex,                    #8
        con,                    #9
        intt,                   #10
        wis,                    #11
        cha,                    #12
        total_health,           #13
        total_energy,           #14
    ], dtype=np.float32)

    avg_vector = global_vector(attribute_paths)
    
    vector = np.concatenate([artist_vector, avg_vector]) #artist[0:14], global[15:15+len(attribute_path)]
    assert vector.dtype == np.float32
    return vector
_STATE_SIZE = 15 + len(attribute_paths)