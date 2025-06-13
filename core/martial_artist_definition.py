from core.globals import MARTIAL_WORLD_LIST, techniques, techniques_objects, logger, log, gc, random, is_empty_dict, WORLD_MAP, realms_JSON, _USED_IDS
from battle_src.evaluations import tech_evaluator, tech_picker
from core.techniques import DefenseTechnique, AttackTechnique, SupportTechnique
from radar import Radar
from uuid import uuid4
from utils.max_values import TALENT_MAX_VALUE


class MartialArtist:
    def __init__(self, map = WORLD_MAP, name = None, gender = None, father = None, mother = None, sect = None, starter_techniques = None, cultivation_realm = "Qi Condensation", talent = None):
        self.father = father if father else None
        self.mother = mother if mother else None
        self.first_name, self.last_name, self.name  = name if name else self.generate_names()
        self.sect = sect if sect else None
        self.techniques = starter_techniques if starter_techniques else {techniques["Palm Strike"]["name"]: techniques["Palm Strike"], techniques["Ironwall Shoulder"]["name"]: techniques["Ironwall Shoulder"]}
        self.talent = talent if talent else self._set_talent()
        self.cultivation_realm = cultivation_realm
        self.realm = self._get_cultivation_realm()
        self.gender = self.sort_gender()
        self.type = "artist"
        self.id = self.generate_id()
        
        self.radar = Radar(map, self, 2)
        
        self.strength = 10
        self.charisma = 10
        self.wisdom = 10
        self.dexterity = 10
        self.intelligence = 10
        self.constitution = 10
        self.stats_average = self.get_stat_avg()
        self._age = 18
        
        self.base_qi = 100
        self.base_vitality = 100
        
        if isinstance(self.realm, dict) and 'Multiplier' in self.realm:
            self.qi = self.base_qi * (self.wisdom + self.constitution) * self.realm['Multiplier']
            self.vitality = self.base_vitality * self.constitution * self.realm['Multiplier']
        else:
            logger.execute("Dictionary Error", "erro", "'Realm' dict doens't have any data.")
            self.qi = 100
            self.vitality = 100

        self.max_qi = self.qi
        self.max_vitality = self.vitality

        self.operational_qi = self.qi * 0.01
        self.operational_vitality = self.vitality * 0.01

        self.alive = True
        self.injured = False
        self.cultivation_blocked = False
        self.relative_time_passed = 0

        self.relations = {}
        self.append_thyself()
        
        self.map = map
        self.coords = self._spawn_random_location()
        
        self.wins = 0
        self.losses = 0
        
        self.battle_record = {}
        
        #Battle Oriented Stats
        self.stun = False
        self.burn = False
        self.poison = False
        self.base_defense = (self.constitution + round(self.qi * 0.05)) * self.realm['Multiplier']
        self.defense_element = None
        
        #Decision-Making Stats / Fame Stats
        self.aggression = random.randrange(1, 20)
        self.strategy = random.randrange(1, 20)
        self.honor = random.randrange(1, 20)
        self.ruthlessness = random.randrange(1, 20)
        self.mercy = random.randrange(1, 20)
        self.personality = self.personality_create()
        
        self.avg_technique = self.get_avg_tier()
        
        
    def generate_id(self):
        while True:
            new_id = str(uuid4())
            if new_id not in _USED_IDS and new_id not in MARTIAL_WORLD_LIST:
                _USED_IDS.add(new_id)
                return new_id
    
    def get_stat_avg(self):
        atts = [
            self.strength,
            self.constitution,
            self.wisdom,
            self.dexterity,
            self.intelligence,
            self.charisma
        ]
        return sum(atts) / len(atts)
    
    def is_leader(self):
        return True if self.sect.sect_leader == self else False
    
    def get_avg_tier(self):
        total_value = 0
        for x, z in self.techniques.items():
            total_value += self.techniques[x]["tier"]
        return round(total_value / len(self.techniques))
    
    def personality_create(self):
        personality = {
            "aggression": self.aggression,
            "strategy": self.strategy,
            "honor": self.honor,
            "ruthlessness": self.ruthlessness,
            "mercy": self.mercy
        }
        return personality
    
    def generate_names(self):
        first_names = [
    "Xiao", "Feng", "Lei", "Long", "Tian", "Bai", "Zhao", "Wei", "Hua", "Shen",  
    "Jiang", "Yu", "Yun", "Lian", "Zhen", "Qing", "Rong", "Hao", "Jun", "Ling",  
    "Chen", "Kai", "Yan", "Ming", "Shu", "Chao", "Guang", "Zhi", "Ru", "Qiu",  
    "Xun", "Zhi", "Bo", "Heng", "Han", "Mo", "Wen", "Jing", "Ran", "Yi", "Yue"
]

        middle_names = [
    "Shan", "Mu", "Zhi", "Hai", "Fei", "Ying", "Lan", "Jian", "Huo", "Feng",  
    "Chen", "Rui", "Xue", "Hua", "Tao", "Sheng", "Yun", "Tian", "Lei", "Xiang",  
    "Xun", "Rou", "Wei", "He", "Lian", "Kong", "Hong", "Xia", "Cheng", "Yao",  
    "Rong", "Zhi", "Gu", "Jie", "Bing", "Yu", "Chao", "Yan", "Lin", "Xin", "Kun"
]
        first_name = getattr(self.father, "first_name", random.choice(first_names))
        last_name = random.choice(middle_names)
        full_name = f"{first_name} {last_name}"
        return first_name, last_name, full_name 

    def _spawn_random_location(self):
        x = random.randint(0, self.map.grid_size["x"] - 1)
        y = random.randint(0, self.map.grid_size["y"] - 1)
        return (x, y) 

    def health_status(self):
        vitality_percent = int((self.max_vitality / self.vitality) * 100)
        qi_percent = int((self.max_qi / self.qi) * 100)
        return vitality_percent, qi_percent

    def sort_gender(self):
        sorted_gender = random.randint(1,2)
        return "Male" if sorted_gender == 1 else "Female"
    def append_thyself(self):
        MARTIAL_WORLD_LIST[self.id] = self
    def update_qi(self):
        self.qi = self.base_qi * (self.wisdom + self.constitution) * self.realm['Multiplier']
        self.check_cap()
    def update_vitality(self):
        self.vitality = self.base_vitality * (self.constitution + self.strength) * self.realm['Multiplier']
    def change_realm(self, new_realm, name_new_realm):
        self.realm = new_realm
        self.cultivation_realm = name_new_realm
        self.update_qi()
        self.update_vitality()
    def do_damage(self, damage):
        self.set_stat("max_vitality", max(0, round(self.max_vitality - damage)))
        self.check_for_wounds(damage)
    def check_for_wounds(self, damage):
        if damage >= (self.max_vitality * 0.40):
            self.injured = True
    def check_cap(self):
        next_realm, realm_name = self._get_next_cultivation_realm()
        if next_realm:
            if self.talent < next_realm['Talent Treshold']:
                if self.qi > next_realm['Qi Requirement'] - 1:
                    self.qi = next_realm['Qi Requirement'] - 1
        else:
            return
    @property
    def main_battle_stat(self):
        return self.strength if self.strength >= self.dexterity else self.dexterity
    @property
    def age(self):
        if self._age >= self.realm['Age Limit']:
            log.info(f"{self}({self.name}) died of old age.")
            self.delete()
        return 18 + self.relative_time_passed // 100
    
    def delete(self):
        if self.id in MARTIAL_WORLD_LIST:
            del MARTIAL_WORLD_LIST[self.id]
            if self.sect is not None:
                if self.name in self.sect.members:
                    del self.sect.members[self.name]
            for mu in MARTIAL_WORLD_LIST.values():
                mu.relations.pop(self.name, None)
            del self
            gc.collect()
        else:
            log.warning(f"Attempted to delete {self}({self.name}), but they were not found.")
            logger.execute("object not found", "erro", f"{self}({self.name}) tried to delete itself but this object don't exist in the World List.")
    def get_stat(self, stat):
        return getattr(self, stat)

    def set_stat(self, stat, value):
        if hasattr(self, stat):
            setattr(self, stat, value)
        else:
            logger.execute("Attribute error", "erro", f"the object {self}({self.name}) tried to define a non existent attribute.")
            
    def _get_cultivation_realm(self):
        realms = realms_JSON
        return realms.get(self.cultivation_realm, None)

    def _get_next_cultivation_realm(self):
        realms = realms_JSON
        realm_names = list(realms.keys())
        if self.cultivation_realm in realm_names:
            index = realm_names.index(self.cultivation_realm)
            if index + 1 < len(realm_names):
                return realms[realm_names[index + 1]], realm_names[index + 1]
        return None, None
    
    def _set_talent(self):
        
        talent = random.randint(1, 3)
        father_talent = self.father.talent if self.father else 1
        mother_talent = self.mother.talent if self.mother else 1

        talent += father_talent + mother_talent // 2

        return round(min(TALENT_MAX_VALUE, talent))

    def recover(self, facility_quality = None, duration = 1):
        fc_level = facility_quality if facility_quality else 1
        if self.max_qi < self.qi:
            self.max_qi = min(self.qi, (((self.max_qi + 200) + (fc_level)) + (self.wisdom * self.constitution)) * duration)
            log.info(f"{self}({self.name}) was successfuly healed.")
            self.pass_time(duration)
        elif self.max_vitality < self.vitality:
            self.max_vitality = min(self.vitality, ((self.max_vitality * fc_level/10) + self.constitution * self.strength) * duration)
            log.info(f"{self}({self.name}) was successfuly healed.")
        else:
            log.info(f"{self}({self.name}) tried to heal when they is already at full health.")
            return
        
    def train(self, stat, facility_quality = None, duration = 1):
        fc_level = facility_quality if facility_quality else 1
        training_supress = 1
        if self.max_qi <= self.operational_qi:
            log.info(f"{self}({self.name}) doens't have enough Qi to train.")
            return
        elif self.injured == True:
            training_supress = 0.8
        progress_gain = (max(1, round(self.talent/2)) + fc_level) * training_supress
        progress_gain += max(1, duration/2)
        previous_value = self.get_stat(stat)
        self.set_stat(stat, int(previous_value) + round(progress_gain))
        self.update_qi()
        self.update_vitality()
        self.pass_time(duration*5)
        log.info(f"{self}({self.name}) successfully trained and advanced them stats {stat.upper()}: {previous_value} to {stat.upper()}: {self.get_stat(stat)} in {duration} unit of time")

    def cultivate(self, facility_quality = None, duration = 1, cultivation_supplies = None):
        fc_level = facility_quality if facility_quality else 1
        quantity_cultivation = cultivation_supplies if cultivation_supplies else 1
        if self.max_qi <= self.operational_qi:
            log.info(f"{self}({self.name}) doens't have enough Qi to cultivate.")
            return
        elif self.cultivation_blocked == True:
            log.info(f"{self}({self.name}) can't cultivated because is blocked.")
            return
        progress_gain = self.talent * (self.wisdom + self.intelligence) / 2 * fc_level * quantity_cultivation
        progress_gain += max(1, duration/2)
        self.set_stat("base_qi", int(self.get_stat("base_qi")) + round(progress_gain))
        self.update_vitality()
        self.update_qi()
        log.info(f"{self}({self.name}) has cultivated successfully. (New Value: {self.qi})")
        self.check_for_breakthrough()
        self.pass_time(duration)

    def learn_technique(self, technique): #REPARAR E MELHORAR ESTE CODIGO
        learn_rate = max(1, self.talent * self.wisdom / 100)
        duration_prediction = technique["Learn Difficulty"] / learn_rate
        if duration_prediction > 100:
            log.info(f"{self}({self.name}) tried to learn a technique that they have not good aptitude.")
            return
        else:
            self.pass_time(duration_prediction)
            self.set_stat("max_qi", min(1000, self.max_qi / (duration_prediction/2)))
            self.techniques[technique["Name"]] = technique 
            log.info(f"{self}({self.name}) learned a new tech. take it at all {duration_prediction} units of time.")

    def pass_time(self, duration):
        self.relative_time_passed += duration
        
    def check_for_breakthrough(self):
        next_realm, realm_name = self._get_next_cultivation_realm() 
        if next_realm:
            if self.qi >= next_realm['Qi Requirement']:
                if self.talent >= next_realm['Talent Treshold']:
                    self.breakthrough(next_realm, realm_name)
            else:
                return
        else:
            return
    
    def breakthrough(self, next_realm, realm_name):
        log.info(f"{self}({self.name}) successfully advanced to the next realm ({self.cultivation_realm} - {realm_name})")
        self.change_realm(next_realm, realm_name)

    def full_Qi(self):
        """Intended to be used as test feature."""
        self.qi = 50000000
        
    def die(self, cause="Unknown"):
        log.info(f"{self}({self.name}) died. [Cause of Death: {cause}]")
        self.delete()
        
    def has_lover(self):
        return any(rel["deepness"] == "lover" for rel in self.relations.values())
    def has_relations(self, target):
        return target.name in self.relations
    def get_relation(self, target):
        if self.has_relations(target):
            return self.relations[target.name]
        return None
    def relation(self, target):
        relation_table = {
            -500: "archenemy",
            -400: "sworn enemy",
            -200: "rival",
            -100: "enemy",
            0: "stranger",
            100: "friend",
            200: "good friend",
            400: "best friend",
            500: "sworn brother",
            1000: "lover",
        }
        relation_id = self.get_relation(target)
        relation_id_other = target.get_relation(self)
        if relation_id:
            if relation_id["intensity"] < 1000 and relation_id_other["intensity"] < 1000:
                relation_id["intensity"] += round((self.charisma + 10) / 5) * 5
                relation_id_other["intensity"] += round((self.charisma + 10) / 5) * 5
            else:
                return
        else:
            self.relations[target.name] = {"deepness": "stranger", "intensity": self.charisma, "object": target}
            target.relations[self.name] = {"deepness": "stranger", "intensity": self.charisma, "object": self}
            log.info(f"{self}({self.name}) and {target}({target.name}) were made {self.relations[target.name]['deepness']}s.")
            return
        
        intensity = relation_id['intensity']
        new_deepness = "stranger"

        for treshold, status in sorted(relation_table.items()):
            if intensity >= treshold:
                new_deepness = status
        
        lover_flag = self.has_lover()
        other_lover_flag = target.has_lover()

        if new_deepness == "lover":
            if lover_flag and other_lover_flag:
                new_deepness = "best friend"
            else:
                log.info(f"{self}({self.name}) now is in love with {target}({target.name})")

        relation_id['deepness'] = new_deepness
        relation_id_other["deepness"] = new_deepness
        
        log.info(f"{self}({self.name}) and {target}({target.name}) are {new_deepness}s (Intensity: {intensity})")
    
    def get_lover(self):
        for name, relation in self.relations.items():
            if relation["deepness"] == "lover":
                return relation["object"]
        return None   
    def give_birth(self, debug_mode = False, debug_father = None):
        if debug_mode == True:
            self.map.create_martial_artist(father=debug_father, mother=self)
            return
        partner = self.get_lover()
        self.pass_time(100)
        child = self.map.create_martial_artist(father=partner, mother=self)
        log.info(f"{self}({self.name}) and {partner}({partner.name}) successfully gave birth to a child! {child}({child.name})")
        return
        
    def get_tech_group(self, orientation):
        possible_techs = {}
        for t, i in self.techniques.items():
            if self.techniques[t]["type"] == orientation:
                possible_techs[t] = self.techniques[t]
        if is_empty_dict(possible_techs):
            return None
        else:
            return possible_techs
    
    def reaction(self, attack_data:dict, battle):
        defense_tech_group = self.get_tech_group("defense")
        origin = attack_data['origin']
        best_tech, best_weight = tech_picker(defense_tech_group, "defense", self)
        
        if best_tech in techniques_objects.keys():
            choosenObject = techniques_objects[best_tech]
            if isinstance(choosenObject, DefenseTechnique):
                data_block = choosenObject.use(self, origin)
                real_damage = attack_data["damage"]
                damage = choosenObject.reaction(attack_data, data_block)
                damage = round(max(0, damage))
                damage_threshold, course_action = battle.safe_zone_damage(self, attack_data["origin"])
                if course_action == "disobey" or course_action == "killing":
                    self.do_damage(damage)
                if course_action == "obey" or course_action == "training" or course_action == "mock":
                    self.do_damage(damage_threshold)
                    damage = damage_threshold
                logger.execute(f"Debug Battle Log {self}({self.name}) vs {origin}{origin.name}", "sucesso", f"A Hit with a power of {damage} (Real Damage: {real_damage}) hits {self}({self.name}) ({self.talent}), (technique: {attack_data["technique_origin"].name} origin: {origin}{origin.name}) ({origin.talent})")
            else:
                log.error(f"Object {self}(Name: {self.name}) tried to use a technique with the wrong orientation in reaction.")
                logger.execute("wrong instance", "erro", f"Object {self} with the name of {self.name} used a wrong technique instance when in reaction.")

    def obey_krule(self, battle):
        if not battle.battle_regulations["Killing"]:
            krule_factor = self.disobey_factor()
            if krule_factor == "cruel":
                return "disobey"
            elif krule_factor == "merciul":
                return "obey"
            elif krule_factor == "neutral":
                if random.randrange(1, 100) < 70:
                    return "obey"
                else:
                    return "disobey"
            elif battle.battle_regulations["Training"]:
                return "obey"
        else:
            return "obey"
    
    def disobey_factor(self):
        factors = {
            "cruel": self.aggression * 0.5 + self.ruthlessness * 0.5,
            "merciful": self.mercy * 0.5 + self.honor * 0.5,
            "neutral": self.mercy * 0.5 + self.ruthlessness * 0.5
        }
        
        total_factors = sum(factors.values())
        
        if total_factors > 0:
            for factor in factors:
                factors[factor] += random.uniform(0, total_factors * 0.1)
            
            total_factors = sum(factors.values())
            
            for factor in factors:
                factors[factor] /= total_factors
        
        chosen_factor = random.choices(list(factors.keys()), weights=list(factors.values()), k=1)[0]
        return chosen_factor
