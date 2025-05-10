from martial_artist_definition import MartialArtist
from node_map import Map
from battle_manager import *
from initializer import *
from trade_system import CityTradeSystem
from sect import Sect
full_load()


test_map = Map(regions["Heavenly Jade Plains"])
test_trade_system = CityTradeSystem(test_map)
sect = Sect(test_map, test_trade_system)


