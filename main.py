from core.martial_artist_definition import MartialArtist
from core.node_map import NodeMap, Detector
from battle_src.battle_manager import *
from core.initializer import *
from core.sect import Sect
from core.city import City
from core.globals import regions

full_load()

test_trading_system = 1
test_map = NodeMap("Test Map", test_trading_system)

test_map.create_martial_artist()

test_map.create_martial_artist()


