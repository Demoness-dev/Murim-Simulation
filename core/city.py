from core.globals import cities, random, MARTIAL_WORLD_LIST, uuid, GLOBAL_BUILD_OBJECTS, pairwise, resources_weight, find_entry
from utils.console_writer import log
from utils.logger import logger
from core.build import Building
from copy import deepcopy
from core.trade_system import TradeSystem
class City:
    def __init__(self, region, trade_system:TradeSystem, city_name = None):
        self.city_id = uuid.uuid4()
        self.trade_system = trade_system
        self.nearby_nodes = {}
        self.nearby_artists = {}
        self.region = region
        self.coords = None
        self.name = city_name if city_name else self.generate_city_name()
        self.resources = {"Spirit Stones": min(30000, random.randint(10000, 30000)), "Cultivation Supply": min(2000, random.randint(1500, 2500)), "Building Supply": min(28000, random.randint(12000, 30000))}
        self.resources_limit = {"Spirit Stones": 30000, "Cultivation Supply": 2000, "Building Supply": 30000}
        self.resource_trigger = {}
        self.prices = {"Spirit Stones": 1, "Cultivation Supply": 3, "Building Supply": 1}
        self.build_slot = {}
        self.prosperity_rate = random.uniform(1,2)
        self.incomes = {"Spirit Stones": 500, "Cultivation Supply": 150, "Building Supply": 1000}
        self.market_inventory = []
        cities[self.city_id] = {"city": self, "region": self.region}
        self.generate_hall()

    def set_coords(self, x, y):
        return setattr(self, "coords", (x, y))
    
    def assimilate_build(self, build:Building):
        self.build_slot[build.name] = build
    
    def remove_build(self, build:Building):
        del self.build_slot[build.name]
    
    def remove_resources(self, amount, resource):
        self.resources[resource] = max(0, (self.resources[resource] - amount))

    def add_resource(self, resource, amount):
        self.add_new_resource(resource, amount)
        self.resources[resource] = min(self.resources_limit[resource], (self.resources[resource] + amount))
    
    def add_new_resource(self, resource, amount=1000):
        if resource not in self.resources.keys():
            self.resources[resource] = amount
            self.resources_limit[resource] = amount * 3
            self.prices[resource] = 1
        else:
            return

    def generate_hall(self):
        burner_copy = deepcopy(GLOBAL_BUILD_OBJECTS["Town Hall"])
        self.assimilate_build(burner_copy)
    
    def add_income(self, build:Building):
        self.incomes.setdefault(build.income_t, 0)
        self.incomes[build.income_t] += build.income_q
        
    def remove_income(self, build:Building):
        if build.income_t in self.incomes:
            self.incomes[build.income_t] -= build.income_q
             
    def resource_trigger_check(self, resource):
        return True if self.resources[resource] <= self.resources_limit[resource] * 0.10 else False
    
    def decide_needed_amount(self, desired_resource, offered_resource):
        current = self.resources.get(desired_resource, 0)
        cap = self.resources_limit.get(desired_resource, 1)
        offered_amount_available = self.resources.get(offered_resource, 0)

        ratio = current / cap
        if ratio >= 0.95:
            return 0, 0

        needed = cap - current

        wR = find_entry(desired_resource, resources_weight) or 1
        wO = find_entry(offered_resource, resources_weight) or 1

        qR = needed
        qO_required = int((qR * wR) / wO)

        if qO_required <= offered_amount_available:
            return qR, qO_required
        else:
            max_qR = int((offered_amount_available * wO) / wR)
            return max_qR, offered_amount_available
    
    def resource_trigger_manager(self, resource):
        highest_resource = max(self.resources, key=lambda x: self.resources[x])
        if resource == highest_resource:
            return
        desired_amount, offered_amount = self.decide_needed_amount(resource, highest_resource)
        if desired_amount <= 0:
            return
        self.trade_system.register_trade(self, highest_resource, offered_amount, desired_amount, resource)

    def resource_manager(self):
        for income_type, income_values in self.incomes.items():
            self.add_resource(income_type, income_values)
            if self.check_cap(income_type):
                self.resources[income_type] = self.resources_limit[income_type]
            if self.resource_trigger_check(income_type):
                self.resource_trigger_manager(income_type)
    
    def check_cap(self, resource):
        self.resources.setdefault(resource, 0)
        self.resources_limit.setdefault(resource, 3000)
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
    
    def check_enough_resource(self, build:Building):
        return all(self.resources.get(res, 0) >= amount for res, amount in build.cost.items())
    
    def update_prices(self):
        for resource, price in self.prices.items():
            demand_factor = 1 - (self.resources[resource] / self.resources_limit[resource])
            self.prices[resource] = round(self.prices[resource] * (1 + demand_factor * 0.5), 2)
    
    def unbuild(self, build:Building):
        if build.name not in self.build_slot.keys():
            log.error(f"{self.city_id}({self.name}) tried to delete a object that they don't have. {build}({build.name})")
            return
        self.remove_build(build)
        self.add_resource(build.income_t, build.income_q * 0.30)
        self.remove_income(build)
        
    def build(self, build:Building):
        if build.settle_type != "City":
            log.error(f"{build}({build.name}) is not a Settlement of the same type as the original object.")
            return
        if self.check_enough_resource(build):
            self.assimilate_build(build)
            self.add_income(build)
            for resource, amount in build.cost.items():
                self.remove_resources(amount, resource)
            log.info(f"{build.name} successfully constructed in {self.name}")
        else:
            log.warning(f"Insufficient resources to construct {build.name} in {self.name}.")
    
    def zero_resources(self):
        """Intentionally sets all resources to 0 for testing purposes."""
        for resource in self.resources:
            self.resources[resource] = 0
        logger.execute("Zero Resources", "aviso", f"All resources in {self.name} were set to 0.")
    def max_resources(self):
        """Intentionally sets all resources to their maximum for testing purposes."""
        for resource in self.resources:
            self.resources[resource] = self.resources_limit[resource]
        logger.execute("Max Resources", "aviso", f"All resources in {self.name} were set to their maximum.")



