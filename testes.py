from martial_artist_definition import MartialArtist
from node_map import NodeMap
from battle_manager import *
from initializer import *
from sect import Sect
from city import City
from globals import regions
from evaluations import resource_evaluation

full_load()

test_trading_system = 1
test_map = NodeMap("Test Map", test_trading_system)
test_city = City(test_map, test_trading_system)

resource_evaluation(test_city)
