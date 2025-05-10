from globals import *

def technique_interpreter():
    
    global techniques_objects
    global techniques
    
    tech_type = {
        "attack": lambda tech: AttackTechnique(tech["name"], tech["cost"], tech["power"], tech["tier"], tech["effect"], tech["element"]),
        "defense": lambda tech: DefenseTechnique(tech["name"], tech["cost"], tech["power"], tech["tier"], tech["effect"], tech["element"]),
        "support": lambda tech: SupportTechnique(tech["name"], tech["cost"], tech["power"], tech["effect"], tech["tier"], tech["buff type"])
    }

    for name, t in techniques.items():
        techniques_objects[name] = tech_type[t["type"]](t)

class Technique:
    def __init__(self, name, cost, tier):
        self.name = name
        self.cost = cost
        self.tier = tier
    def use(self, user, target):
        raise NotImplementedError


class AttackTechnique(Technique):
    def __init__(self, name, cost, power, tier, effect=None, element="metal"):
        super().__init__(name, cost, tier)
        self.power = power
        self.effect = effect 
        self.element = element
    def use(self, user, target):
        if user.max_qi < self.cost:
            return
        user.max_qi -= self.cost
        total_damage = (self.power + user.main_battle_stat + (user.max_qi * 0.10)) * user.realm["Multiplier"]
        total_damage *= self.tier
        
        if self.effect != "None":
           action = self._get_effect(self.effect)
           duration = 1
           value = total_damage * (self.tier//10)
           global_effect_manager.apply_effect(target, value = value, duration = duration, effect_type=action)
        
        
        data_block = {
            "damage": total_damage,
            "element": self.element,
            "has_effect": True if self.effect != "None" else False,
            "origin": user,
            "targets": target,
            "technique_origin": self
        }
        
        return data_block
        
    def _get_effect(self, effect):
        effect_tables = {
            1: "burn",
            2: "poison",
            3: "stun"
        }
        return effect_tables.get(effect, "burn")

class DefenseTechnique(Technique):
    def __init__(self, name, cost, power, tier, effect = None, element = "metal"):
        super().__init__(name, cost, tier)
        self.power = power
        self.effect = effect
        self.element = element

    def use(self, user, target):
        if user.max_qi < self.cost:
            return

        user.max_qi -= self.cost
        
        total_value = (self.power + user.constitution) * round(max(1, (self.tier // 2)))
        
        damage_reduction = 0.05 + max(0.05, round(self.tier/10))

        data_block = {
            "defense_power": total_value,
            "damage_reduction": damage_reduction,
            "element": self.element,
            "origin": user,
            "targets": user,
            "technique_origin": self
        }
        
        return data_block
    
    def reaction(self, data_block_attack, data_block_defense):
        damage = data_block_attack["damage"]
        element2 = data_block_attack["element"]
        damage_reduction = data_block_defense["damage_reduction"]
        defense_power = data_block_defense["defense_power"]
        element1 = data_block_defense["element"]
        element_odds = get_rival_element(element2, element1)
        damage *= element_odds
        damage_reduction *= damage
        total_damage = damage - damage_reduction
        total_damage -= defense_power
        return total_damage
        
class SupportTechnique(Technique):
    def __init__(self, name, cost, power, effect, tier, buff_type):
        super().__init__(name, cost, tier)
        
        global global_effect_manager
        
        self.power = power
        self.effect = effect
        self.buff_type = buff_type
        
    def use(self, user, target, buff_type=None, debuff_type=None):
        if user.max_qi < self.cost:
            return
        multiplier = max(1, self.tier // 2)
        total_value = ((self.power + user.wisdom + (user.max_qi * 0.10)) * user.realm["Multiplier"]) * multiplier
        user.max_qi -= self.cost
        effects = {
            1: lambda: self.heal(target, total_value), #Heal
            2: lambda: self.buff(user, target, buff_type, total_value), #Buff
            3: lambda: self.debuff(user, target, debuff_type, total_value) #Debuff
        }
        effects.get(self.effect, lambda: self.buff(user, target, buff_type, total_value))()
        
    def get_buff(self, buff_type):
        buff_actions = {
            1: "main_battle_stat",
            2: "base_defense",
            3: "max_qi",
            4: "wisdom",
            5: "heal_dot"
        }
        return buff_actions.get(buff_type, "main_battle_stat")

    def heal(self, target, value):
        target.max_vitality = min(target.vitality, target.max_vitality + value)

    def buff(self, caster, target, buff_type, value):
        stat_name = self.get_buff(buff_type)
        duration = round(max(1, caster.wisdom // 2)) * max(1, self.tier // 5)
        
        if stat_name != "heal_dot":
            value = self.tier + max(1 , (caster.wisdom * 0.40))
        
        global_effect_manager.apply_effect(
            target,
            stat_name=stat_name if stat_name != "heal_dot" else None,
            effect_type="increase_stat" if stat_name != "heal_dot" else "heal_dot",
            duration=duration,
            value=value
        )

    def get_debuff(self, debuff_type):
        debuff_actions = {
            1: "stun",
            2: "poison",
            3: "burn",
            4: "stat_decrease"
        }
        return debuff_actions.get(debuff_type, "stat_decrease")

    def debuff(self, caster, target, debuff_type, value, stat_name=None):
        action = self.get_debuff(debuff_type)
        multiplier = max(1, self.tier // 2)
        duration = round(max(1, caster.wisdom // 2)) * multiplier

        if action == "stat_decrease":
            stat_name = stat_name or "main_battle_stat"
            value = self.tier * max(1 , (caster.wisdom * 0.40))

        global_effect_manager.apply_effect(
            target,
            stat_name=stat_name if action == "stat_decrease" else None,  
            effect_type=action,
            duration=duration,
            value=value
        )