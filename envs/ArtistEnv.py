from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
from random import uniform
from envs.settings.possible_actions import ACTIONS, MOVE_ACTIONS
from core.globals import search_id, WORLD_MAP
from envs.settings.vectors import _STATE_SIZE, get_artist_vector, attribute_ids
from core.node_map import NodeMap
from utils.logger import logger
from core.martial_artist_definition import MartialArtist
from settings.counter import START_RADAR, END_RADAR, START_REL_POS, END_REL_POS, MAX_OBJECTS
class ArtistEnv(Env):
    def __init__(self, artist_id):
        super().__init__()
        self.artist : MartialArtist = search_id(artist_id)
        self.action_space = Discrete(len(ACTIONS))
        self.observation_space = Box(low=0, high=1, shape=(_STATE_SIZE,), dtype=np.float32)
        self.map : NodeMap = WORLD_MAP
    def reset(self):
        return get_artist_vector(self.artist, self.map)

    def step(self, action):
        reward = 0
        done = False
        
        if 0 <= action < len(ACTIONS):
            action_name = ACTIONS[action]
            reward, done = self.execute_action(action_name)
        else:
            reward = -1
            done = True
        
        obs = get_artist_vector(self.artist)
        return obs, reward, done, {}
    
    def execute_action(self, action_name):
        try:
            current_state = get_artist_vector(self.artist, self.map)
            reward = 0.0
            done = False
            radar_counts = current_state[START_RADAR:END_RADAR]
            rel_pos = current_state[START_REL_POS:END_REL_POS].reshape((MAX_OBJECTS, 3))
            
            match action_name:
                case "cultivate":
                    self.artist.cultivate()
                    reward = 0.6
                    if current_state[attribute_ids["energy"]] <= 0.4: #Check energy to give more necessity when low.
                        reward += 0.2
                    
                    if current_state[attribute_ids["cultivation"]] >= 0.5: #Check total cultivation level to give more necessity when near bottleneck
                        reward += 0.3
                    
                    elif current_state[attribute_ids["energy"]] >= 0.7:
                        reward += 0.1
                        
                    if current_state[attribute_ids["energy"]] < current_state[attribute_ids["qi"]]:
                        reward += 0.1
                    if current_state[attribute_ids["energy"]] >= current_state[attribute_ids["qi"]]:
                        reward += 0.2
                    
                case "train_str" | "train_dex" | "train_con" | "train_int" | "train_wis" | "train_cha":
                    stat_idx = {
                        "train_str": {"ID": attribute_ids["str_"], "stat": "str", "vector_id": "strength"},
                        "train_dex": {"ID": attribute_ids["dex_"], "stat": "dex", "vector_id": "dexterity"},
                        "train_con": {"ID": attribute_ids["con_"], "stat": "con", "vector_id": "constitution"},
                        "train_int": {"ID": attribute_ids["int_"], "stat": "int", "vector_id": "intelligence"},
                        "train_wis": {"ID": attribute_ids["wis_"], "stat": "wis", "vector_id": "wisdom"},
                        "train_cha": {"ID": attribute_ids["cha_"], "stat": "cha", "vector_id": "charisma"},
                    }
                    reward = 0.6
                    stat = stat_idx[action_name]
                    self.artist.train(stat["stat"])
                    
                    new_vector = get_artist_vector(self.artist, self.map)
                    stat_gain = new_vector[stat["ID"]] - current_state[stat["ID"]]
                    
                    if stat_gain > 0:
                        reward += stat_gain * 3 + 0.1
                    else:
                        reward -= 0.2 
                    attr_id = attribute_ids[stat["vector_id"]]
                    vector = current_state[stat["ID"]]
                    
                    if vector < current_state[attr_id]:
                        reward += 0.1
                    else:
                        reward += 0.2
                        
                    if action_name == "train_con" and current_state[attribute_ids["total_health"]] < current_state[attribute_ids["vitality"]]:
                        reward += 0.1
                    if action_name == "train_con" and current_state[attribute_ids["total_health"]] >= current_state[attribute_ids["vitality"]]:
                        reward += 0.2
                    if action_name == "train_wis" and current_state[attribute_ids["total_energy"]] < current_state[attribute_ids["qi"]]:
                        reward += 0.1
                    if action_name == "train_wis" and current_state[attribute_ids["total_energy"]] >= current_state[attribute_ids["qi"]]:
                        reward += 0.2
                    
                case "rest":
                    reward += 0.5
                    
                    if current_state[attribute_ids["health"]] <= 0.3:
                        reward += 0.3
                    elif current_state[attribute_ids["health"]] <= 0.5:
                        reward += 0.1

                    
                case "learn_technique":
                    pass
                case "move":
                    pass
                case "relation":
                    pass
                
        except Exception as e:
            logger.execute(f"Action Error on Env", "erro", "The Enviroment choose a non-existent action. Or another uncommon error happened. {e}")
    