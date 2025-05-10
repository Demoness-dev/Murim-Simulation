from globals import *

class City:
    def __init__(self, region, trade_system, city_name = None):
        self.city_id = len(cities) + 1
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
        self.build_slot = ["Town Hall"]
        self.prosperity_rate = random.uniform(1,2)
        self.incomes = {"Spirit Stones": 500, "Cultivation Supply": 150, "Normal Supply": 1000}
        self.market_inventory = []
        cities[self.city_name] = {"city": self, "region": self.region}

    def set_coords(self, x, y):
        self.coords = (x, y)
        return 
    
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
            
    def _get_possible_buildings(self, build_dict = BUILD_SLOTS):
        possible_buildings = {}
        builds = build_dict
        for build_name, build_info in builds.items():
            build_needs = build_info.get("Build Needs", [])
            if build_needs == "None":
                build_needs = []
            if build_info["Region Needs"] in self.region["Availables"] and build_info["Settlement Type"] == "City":
                if all(req in self.build_slot for req in build_needs):
                    possible_buildings[build_name] = build_info
        return possible_buildings
    def search_build(self, build_dict = BUILD_SLOTS):
        found_buildings = {}
        for slot in self.build_slot:
            if slot in build_dict and build_dict[slot]["Settlement Type"] == "City":
                found_buildings[slot] = build_dict[slot]
        return found_buildings
    def _income_manager(self):
        builds = self.search_build()
        for build_keys, build_values in builds.items():
            if build_values["Income"] == "None":
                continue
            self.incomes[build_values['Income']] += build_values['Income Quantity']
        log.info(f"Monthly Income for {self.city_name}")
    def resource_manager(self):
        self._income_manager()
        for resource_t in self.resources.keys():
            if resource_t not in self.resources_limit:
                self.resources_limit[resource_t] = self.incomes[resource_t] * 5
                
            self.resources[resource_t] = min(
                self.resources[resource_t] + self.incomes[resource_t], 
                self.resources_limit[resource_t]
            )
            self.resource_trigger[resource_t] = {
                "Trigger": self.resources[resource_t] < self.resources_limit[resource_t] * 0.6,
                "Resource Margin": max(0, self.resources_limit[resource_t] - self.resources[resource_t])
            }
        self.trade_system.manage_city_trades()
    def build(self, build_slot):
        for resource_t, resource_v in build_slot['Build Cost'].items():
            if resource_t in self.resources.keys():
                self.resources[resource_t] -= resource_v
        self.build_slot.append(build_slot['Name'])
        log.info(f"The City {self.city_name} just built {build_slot['Name']}")
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

