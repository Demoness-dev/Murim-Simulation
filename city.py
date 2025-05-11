from globals import cities, random, MARTIAL_WORLD_LIST, uuid, GLOBAL_BUILD_OBJECTS
from console_writer import log
from logger import logger
from build import Building
from copy import deepcopy
class City:
    def __init__(self, region, trade_system, city_name = None):
        self.city_id = uuid.uuid4()
        self.trade_system = trade_system
        self.nearby_nodes = {}
        self.nearby_artists = {}
        self.region = region
        self.coords = None
        self.city_name = city_name if city_name else self.generate_city_name()
        self.resources = {"Spirit Stones": min(30000, random.randint(10000, 30000)), "Cultivation Supply": min(2000, random.randint(1500, 2500)), "Normal Supply": min(28000, random.randint(12000, 30000))}
        self.resources_limit = {"Spirit Stones": 30000, "Cultivation Supply": 2000, "Normal Supply": 30000}
        self.resource_trigger = {}
        self.resource_per_unit = {"Spirit Stones": 1, "Cultivation Supply": 3, "Normal Supply": 1}
        self.build_slot = {}
        self.prosperity_rate = random.uniform(1,2)
        self.incomes = {"Spirit Stones": 500, "Cultivation Supply": 150, "Normal Supply": 1000}
        self.market_inventory = []
        cities[self.city_id] = {"city": self, "region": self.region}
        self.generate_hall()

    def set_coords(self, x, y):
        self.coords = (x, y)
        return 
    
    def assimilate_build(self, build:Building):
        self.build_slot[build.name] = build
        return
    
    def generate_hall(self):
        burner_copy = deepcopy(GLOBAL_BUILD_OBJECTS["Town Hall"])
        self.assimilate_build(burner_copy)
        return
    
    def add_income(self, build:Building):
        self.incomes.setdefault(build.income_t, 0)
        self.incomes[build.income_t] += build.income_q
        return
    
    def remove_income(self, build:Building):
        if build.income_t in self.incomes:
            self.incomes[build.income_t] -= build.income_q
            return
        return    
    
    def resource_manager(self):
        for income_type, income_values in self.incomes.items():
            self.resources[income_type] += income_values
            if self.check_cap(income_type):
                self.resources[income_type] = self.resources_limit[income_type]
                return
        return
    
    def check_cap(self, resource):
        return True if self.resources[resource] >= self.resources_limit[resource] else False
    
    def generate_city_name(self):
        prefixes = ["Stone", "Iron", "Silver", "Gold", "Dark", "White", "Black", "Dragon",
                "Eagle", "Wolf", "Moon", "Sun", "Shadow", "Storm", "Fire", "Raven",
                "Frost", "Azure", "Crimson", "Emerald", "Silent", "Mystic", "Thunder",
                "Ghost", "Ancient", "Sacred", "Frozen", "Deep", "Sky", "Wind"]
    
        suffixes = ["haven", "port", "dale", "ville", "holm", "hold", "watch", "fall", 
                "borough", "ridge", "ford", "stead", "spire", "shade", "reach", 
                "brook", "keep", "gate", "peak", "mark", "hill", "valley", "wood", 
                "bay", "field", "hall"]
        while True:
            name = random.choice(prefixes) + random.choice(suffixes)
            if name not in cities:
                return name
            
    def has_built(self, build_name:str) -> bool:
        return True if build_name in self.build_slot.keys() else False
    
    def construct(self, build:dict):
        pass
            
    def zero_resources(self):
        """Intentionally sets all resources to 0 for testing purposes."""
        for resource in self.resources:
            self.resources[resource] = 0
        logger.execute("Zero Resources", "aviso", f"All resources in {self.city_name} were set to 0.")
    def max_resources(self):
        """Intentionally sets all resources to their maximum for testing purposes."""
        for resource in self.resources:
            self.resources[resource] = self.resources_limit[resource]
        logger.execute("Max Resources", "aviso", f"All resources in {self.city_name} were set to their maximum.")

class Detector:
    def __init__(self, map, radius = 5):
        self.map = map
        self.radius = radius
        self.artists = MARTIAL_WORLD_LIST
        
    def detect_nearby_martial_artists(self, city_name):
        if city_name not in self.map.cities:
            logger.execute("Detector Error", "erro", f"The action (detect_nearby_martial_artists) tried to use a city that is not connected on the map dictionary.")
            return {}
        
        city_position = self.map.objects[city_name]
        nearby_artists = {}
        
        for artist in self.artists.values():
            distance = ((artist.position[0] - city_position[0]) ** 2 + (artist.position[1] - city_position[1]) ** 2) ** 0.5
            if distance <= self.radius:
                nearby_artists[artist.name] = {"distance": distance, "realm": artist.cultivation_realm, "object": artist}
            
        return nearby_artists

