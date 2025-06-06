import numpy as np
from core.martial_artist_definition import MartialArtist


def get_artist_vector(artist:MartialArtist):
    
    next_realm, next_realm_name = artist._get_next_cultivation_realm()
    
    health = artist.max_vitality/artist.vitality
    energy = artist.max_qi/artist.qi
   
    realm = artist.realm["Cultivation Level"] / 20
    cultivation = artist.qi / next_realm["Qi Requirement"] if artist.qi / next_realm["Qi Requirement"] < 1 else 1
    
    avg_stats = artist.get_stat_avg() / 6000
    avg_technique_tier = artist.get_avg_tier() / 30
    talent = artist.talent
    
    
    #Stat block Vectors
    str = artist.strength/1000
    dex = artist.dexterity/1000
    con = artist.constitution/1000
    intt = artist.intelligence/1000
    wis = artist.wisdom/1000
    cha = artist.charisma/1000
    
    
    
    return np.array([           #IDs
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
        cha                     #12
    ], dtype=np.float32)

_STATE_SIZE = 13