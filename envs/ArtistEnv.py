from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
from random import uniform
from envs.settings.possible_actions import ACTIONS
from core.globals import search_id
from settings.env_generic_functions import _STATE_SIZE, get_artist_vector
from utils.logger import logger
from core.martial_artist_definition import MartialArtist

class ArtistEnv(Env):
    def __init__(self, artist_id):
        super().__init__()
        self.artist : MartialArtist = search_id(artist_id)
        self.action_space = Discrete(len(ACTIONS))
        self.observation_space = Box(low=0, high=1, shape=(_STATE_SIZE,), dtype=np.float32)
    
    def reset(self):
        return get_artist_vector(self.artist)

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
            current_state = get_artist_vector(self.artist)
            reward = 0.0
            done = False
            
            match action_name:
                case "cultivate":
                    self.artist.cultivate()
                    reward = 0.8
                    if current_state[1] <= 0.4: #Check energy to give more necessity when low.
                        reward += 0.2
                    
                    if current_state[2] >= 0.5: #Check total cultivation level to give more necessity when near bottleneck
                        reward += 0.1
                    elif current_state[2] >= 0.7:
                        reward += 0.2
                case "train_str" | "train_dex" | "train_con" | "train_int" | "train_wis" | "train_cha":
                    stat_idx = {
                        "train_str": {"ID": 7, "stat": "str"},
                        "train_dex": {"ID": 8, "stat": "dex"},
                        "train_con": {"ID": 9, "stat": "con"},
                        "train_int": {"ID": 10, "stat": "int"},
                        "train_wis": {"ID": 11, "stat": "wis"},
                        "train_cha": {"ID": 12, "stat": "cha"},
                    }
                    reward = 0.6
                    stat = stat_idx[action_name]
                    self.artist.train(stat["stat"])
                    
                    new_vector = get_artist_vector(self.artist)
                    stat_gain = new_vector[stat["ID"]] - current_state[stat["ID"]]
                    
                    if stat_gain > 0:
                        reward += stat_gain * 3 + 0.1
                    else:
                        reward -= 0.2 
                    #AS AVERAGES JA ESTÃO PRONTAS APENAS FAÇA O SISTEMA DE REWARD COMPARANDO AS MÉDIAS GLOBAIS.
                case "rest":
                    pass
                case "learn_technique":
                    pass
                case "move":
                    pass
                case "relation":
                    pass
                
        except Exception as e:
            logger.execute(f"Action Error on Env", "erro", "The Enviroment choose a non-existent action. Or another uncommon error happened. {e}")
    