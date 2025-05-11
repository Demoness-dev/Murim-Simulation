import random
from console_writer import log
from logger import logger
from martial_artist_definition import MARTIAL_WORLD_LIST, MartialArtist
from battle_manager import manage_brackets, create_battle_instance
from globals import SECT_WORLD_LIST, load_json, GLOBAL_BUILD_OBJECTS

class Sect:
    def __init__(self, map, trade_system, sect_leader:MartialArtist = None, sect_members:dict = None):
        self.map = map
        self.coords = None
        self.nearby_nodes = {}
        self.nearby_artists = {}
        self.city_name = self.generate_city_name()
        self.sect_leader = sect_leader if sect_leader else self.generate_random_sect_leader()
        self.trade_system = trade_system
        self.sect_members = sect_members if sect_members else {}
        if sect_leader and sect_leader.name not in self.sect_members:
            self.sect_members[sect_leader.name] = {"object": sect_leader, "rank": "Sect Leader"}
        self.resources = {"Spirit Stones": 2000, "Cultivation Supply": 500, "Normal Supply": 2000}
        self.resources_limit = {"Spirit Stones": 2000, "Cultivation Supply": 500, "Normal Supply": 2000}
        self.resource_trigger = {}
        self.resource_per_unit = {"Spirit Stones": 1, "Cultivation Supply": 3, "Normal Supply": 1}
        self.incomes = {"Spirit Stones": 500, "Cultivation Supply": 1200, "Normal Supply": 300}
        self.build_slot = ["Sect Hall", "Training Hall"]
        self.build_buffs = {"train_facility_quality": 1}
        self.relations = {}
        self.add_to_worldlist()    
    
    def generate_random_sect_leader(self):
        return MartialArtist(self.map, cultivation_realm="Nascent Soul", sect=self)
    
    def set_coords(self, x, y):
        self.coords = (x, y)
        return
    
    def add_to_worldlist(self):
        if self.city_name not in SECT_WORLD_LIST:
            SECT_WORLD_LIST[self.city_name] = self
        return
    def generate_city_name(self):
        prefixes = ["Celestial", "Crimson", "Shadow", "Thunder", "Eternal", "Silent", "Iron", "Golden", "Emerald", "Storm", "Azure", "Sacred", "Ghost", "Frozen", "Ancient"]
        middles = ["Dragon", "Phoenix", "Tiger", "Serpent", "Lotus", "Moon", "Sun", "Wolf", "Flame", "Spirit", "Demon", "Wind", "Lightning", "Blade", "Raven"]
        suffixes = ["Sect", "Clan", "Temple", "Order", "Hall", "Palace", "School", "Sanctuary", "Alliance", "Brotherhood", "Pavilion", "Dynasty", "Academy", "Domain", "Monastery"]

        return f"{random.choice(prefixes)} {random.choice(middles)} {random.choice(suffixes)}"
    
    def choose_new_leader(self):
        if not self.sect_members:
            logger.execute("Sect Error", "erro", f"Attempted to choose a new leader for {self.city_name}, but there are no members in the sect.")
            return None
        contenders = {name: entry["object"] for name, entry in self.sect_members.items() if entry["rank"] == "Sect Elder"}
        if not contenders:
            logger.execute("Sect Error", "erro", f"Attempted to choose a new leader for {self.city_name}, but there are no Sect Elders in the sect.")
            return None
        winner = manage_brackets(contenders, "Mock")
        log.info(f"{winner.name} has been chosen as the new leader of {self.city_name}.")
        self.sect_leader = winner
        self.sect_members[winner.name]["rank"] = "Sect Leader"
        
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
        
    def sect_recruit(self, new_member):
        if new_member.name in self.sect_members:
            logger.execute("Sect Error", "erro", f"Attempted to add {new_member.name} to the sect, but the member is already in the sect.")
            return
        self.sect_members[new_member.name] = {"object": new_member, "rank": "Outer Disciple"}
        log.info(f"{new_member.name} joined the sect {self.city_name} as an Outer Disciple.")
        
    def sect_promote(self, member_name, new_rank):
        if member_name not in self.sect_members:
            logger.execute("Sect Error", "erro", f"Attempted to promote {member_name} in the sect, but the member is not in the sect.")
            return
        self.sect_members[member_name]["rank"] = new_rank
        log.info(f"{member_name} was promoted to {new_rank} in the sect {self.city_name}.")
        
    def has_relation(self, target):
        return target.sect.name in self.relations
    
    def get_relation(self, target):
        if self.has_relation(target):
            return self.relations[target.sect.name]
        return None
    
    def custom_add_member(self, member, rank):
        if member.name in self.sect_members:
            logger.execute("Sect Error", "erro", f"Attempted to add {member.name} to the sect, but the member is already in the sect.")
            return
        self.sect_members[member.name] = {"object": member, "rank": rank}
        log.info(f"{member.name} joined the sect {self.city_name} as a {rank}.")
    
    def interact(self, target, action):
        relation_table = {
            -500: "archenemy",
            -400: "sworn enemy",
            -200: "rival",
            -100: "enemy",
            0: "neutral",
            100: "ally",
            200: "good ally",
            400: "close ally",
            500: "permanent ally",
            1000: "sworn ally",
        }

        # Initialize relation if it doesn't exist
        if target.city_name not in self.relations:
            self.relations[target.city_name] = {"value": 0, "status": "neutral", "object": target}
            target.relations[self.city_name] = {"value": 0, "status": "neutral", "object": self}
            log.info(f"{self.city_name} and {target.city_name} are now neutral.")

        self_relation = self.relations[target.city_name]
        target_relation = target.relations[self.city_name]

        # Skip interaction if max/min relationship has been reached
        if not (-500 < self_relation["value"] < 1000 and -500 < target_relation["value"] < 1000):
            return

        # Apply change based on interaction type
        delta = {"offense": -50, "amicable": 50}.get(action, 0)
        self_relation["value"] += delta
        target_relation["value"] += delta

        # Determine new status using relation table
        current_value = self_relation["value"]
        new_status = max(
            (status for threshold, status in relation_table.items() if current_value >= threshold),
            key=lambda s: list(relation_table.values()).index(s),
            default="neutral"
        )

        # Update statuses
        self_relation["status"] = new_status
        target_relation["status"] = new_status

        log.info(f"{self.city_name} and {target.city_name} are now {new_status}. [Value: {current_value}]")
    
    def declare_war(self, target):
        
        self.interact(target, "offense")

        self.relations[target.city_name]["status"] = "in War"
        target.relations[self.city_name]["status"] = "in War"
        
        log.info(f"{self.city_name} declared war on {target.city_name}.")

    def make_peace(self, target):
       
        self.interact(target, "amicable")

        self.relations[target.city_name]["status"] = "neutral"
        target.relations[self.city_name]["status"] = "neutral"
        
        log.info(f"{self.city_name} made peace with {target.city_name}.")