from core.globals import *
from battle_src.evaluations import tech_evaluator, tech_picker, decide_battle_rules
from core.techniques import AttackTechnique, DefenseTechnique, SupportTechnique
import bisect
class Battle():
    def __init__(self, object1, object2, battle_regulations = None): #Only use battle_regulations in class-calling for pre-setting Training.
        self.battle_id = f"BATTLE-{uuid.uuid4()}"
        self.martial_first = object1
        self.martial_second = object2
        self.action_replay = {}
        self.battle_regulations = {"Killing": False, "Incapacitating": False, "Injuring": False, "Training": False, "Mock": False}
        if battle_regulations:
            self.battle_regulations[battle_regulations] = True
        self.pre_flags = {"Run": False, "pre-damage buff": False}
        self.combat_end_flag = False
        self.flag_end = False
    def _check_alive(self, martial):
        return martial.max_vitality > 0
    
    def _end_battle(self, loser, reason="battle"):
        winner = self.martial_first if loser == self.martial_second else self.martial_second
        transcribe_battle_log(winner, loser, self)
        del ONGOING_BATTLES[f"{self.martial_first.name} vs {self.martial_second.name}"]
        gbll = list(GLOBAL_BATTLE_LOG.keys())
        gbl_pick = len(gbll)
        self.flag_end = True
        kwrite = None
        if reason == "Training":
            if winner.sect:
                wbuff = winner.sect.build_buffs["train_facility_quality"]
                wresource = winner.sect.resources["Cultivation Supply"]//100 if winner.sect.resources["Cultivation Supply"]//100 >= 1 else 1
            else:
                wbuff = 1
                wresource = 1
            if loser.sect:
                lbuff = loser.sect.build_buffs["train_facility_quality"]
                lresource = loser.sect.resources["Cultivation Supply"]//100 if loser.sect.resources["Cultivation Supply"]//100 >= 1 else 1
            else:
                lbuff = 1
                lresource = 1
            wchoosen_stat = "strength" if winner.dexterity <= winner.strength else "dexterity"
            lchoosen_stat = "strength" if loser.dexterity <= loser.strength else "dexterity"
            winner.cultivate(wbuff, wresource)
            winner.train(wchoosen_stat, wbuff)
            loser.cultivate(lbuff, lresource)
            loser.train(lchoosen_stat, lbuff)
            kwrite = f"and {winner.name}, {loser.name} trained together."
        if not self._check_alive(loser):
            kwrite = f"and {loser.name} died in battle."
            del MARTIAL_WORLD_LIST[loser.id]
            if loser.sect:
                if loser.sect.sect_leader == loser:
                    loser.sect.choose_new_leader()
                del loser.sect.sect_members[loser.name]
            for martial_key, martial_value in MARTIAL_WORLD_LIST.items():
                if loser.name in martial_value.relations.keys():
                    del martial_value.relations[loser.name]
                    del loser.relations
            gc.collect()
        if kwrite == None:
            kwrite = f"and {loser.name} was defeated."
        log.info(f"A Battle has ended ID: {gbll[gbl_pick - 1]} {kwrite}")

    def _check_aptitude_battle(self):
        """Checks if the objects are apt to fight and check the odds of winning"""
        if not self.martial_first.alive or not self.martial_second.alive:
            return "One of the martial artists is already dead", "One of the martial artists is already dead"
        if ONGOING_BATTLES.get(f"{self.martial_first.name} vs {self.martial_second.name}"):
            return "Battle is already ongoing", "Battle is already ongoing"
        if (self.martial_first.max_qi <= self.martial_first.operational_qi or self.martial_first.max_vitality <= self.martial_first.operational_vitality) or (self.martial_second.max_qi <= self.martial_second.operational_qi or self.martial_second.max_vitality <= self.martial_second.operational_vitality):
            return "One of the martial artists is too weak to fight", "One of the martial artists is too weak to fight"
        
        odds_first = calculate_odds(self.martial_first)
        odds_second = calculate_odds(self.martial_second)
        
        total_odds = odds_first + odds_second
        
        if total_odds == 0:
            return "Both martial artists are too weak to fight", "Both martial artists are too weak to fight"
        
        first_win_chance = (odds_first / total_odds) * 100  
        second_win_chance = (odds_second / total_odds) * 100
        
        return {
            self.martial_first.name: first_win_chance,
            self.martial_second.name: second_win_chance,
            }
        
    def check_turn_speed(self, martial):
        p1speed = (martial.dexterity * (round(martial.max_qi * 0.15))) * martial.realm["Multiplier"]
        return p1speed
    
    def _nature_value_creator(self, martial):
        nature_value = round((martial.realm["Multiplier"] + martial.main_battle_stat + (martial.max_qi * 0.35) + martial.wisdom) * martial.talent)
        return nature_value
    
    def _nature_pick(self, martial):
        opponent = self.martial_second if self.martial_first == martial else self.martial_first
        nature_value_martial_1 = self._nature_value_creator(martial)
        nature_value_martial_2 = self._nature_value_creator(opponent)
    
        nature_diff = abs(nature_value_martial_1 - nature_value_martial_2)


        nature_thresholds = [
            (0.7, "Overwhelmly Superior"),
            (0.5, "Superior"),
            (0.3, "Stronger"),
            (0.1, "Slightly Stronger")
        ]

        if nature_value_martial_1 == nature_value_martial_2:
            return {martial: "Neutral"}

        if nature_value_martial_1 < nature_value_martial_2:
            return self._nature_value(opponent, nature_diff, nature_value_martial_2, nature_thresholds)
        else:
            return self._nature_value(martial, nature_diff, nature_value_martial_1, nature_thresholds)

    def _nature_value(self, martial, nature_diff, base_value, nature_thresholds):
        for threshold, label in nature_thresholds:
            if base_value * threshold <= nature_diff:
                return {martial: label}
        return {martial: "None"}
    def intimidation(self, martial, nature_block:dict):
        if martial in nature_block:
            intimidation_boost = 1.2 + (martial.realm["Multiplier"] if self.martial_first == martial else self.martial_second.realm["Multiplier"])
            return intimidation_boost
        intimidation_boost = 1
        return intimidation_boost
    
    def _check_for_sect_buff(self, martial):
        data_block = getattr(martial.sect, "buff_effects", {})
        return data_block
    
    def _apply_support_technique(self, technique, user):
        
        is_buff = technique.effect in {1, 2}
        target = user if is_buff else (self.martial_second if self.martial_first == user else self.martial_first)
        
        buff_type = None
        debuff_type = None
        
        if technique.effect == 2:
            buff_type = technique.get_buff(technique.buff_type)
        elif technique.effect == 3:
            debuff_type = technique.get_debuff(technique.buff_type)
        
        technique.use(user, target, buff_type, debuff_type)
    
    def _act(self, martial):
        nature = self._nature_pick(martial)
        opponent = self.martial_second if self.martial_first == martial else self.martial_first
        intimidation_boost = self.intimidation(martial, nature)

        best_tech, best_weight = tech_picker(martial.get_tech_group("attack"), "attack", martial)
        if not best_tech or best_tech not in techniques_objects:
            log.warning(f"{martial.name} tried to attack but found no valid technique.")
            return 

        choosenObject = techniques_objects[best_tech]

        if isinstance(choosenObject, AttackTechnique):
            data_block = choosenObject.use(martial, opponent)
            if data_block == None:
                return
            damage = data_block.get("damage", 0)
        
        
            weapon = martial.equipped_items.get("Weapon", {})
            weapon_damage = weapon.get("damage", 0)
            damage_buff = weapon.get("damage_buff", 1) 
            sect_buffs = self._check_for_sect_buff(martial) or {"damage": 1}
                    
            total_damage = ((damage + weapon_damage) * (intimidation_boost * damage_buff * sect_buffs["damage"])) * self.pre_flags["pre-damage buff"]
            data_block["damage"] = total_damage
            self.add_to_action_replay(martial, data_block)
            opponent.reaction(data_block, self)

        elif isinstance(choosenObject, SupportTechnique):
            self._apply_support_technique(choosenObject, martial)
            self.add_to_action_replay(object, _action = "buff" if choosenObject.effect == 1 or 2 else "debuff")
            
    def _distribute_odds(self, odds:dict):
        p1 = None
        p2 = None

        for odds_name, odds_values in odds.items():
            if p1 is None:
                p1 = odds_values
            elif p2 is None:
                p2 = odds_values 
                break 

        return p1, p2
    
    def _determine_behavior(self):
        p1, p2 = self._distribute_odds(self._check_aptitude_battle())
        
        if None in (p1, p2):
            return ("No Conclusion", "No Conclusion")
    
        p1 = p1.pop() if isinstance(p1, set) else p1
        p2 = p2.pop() if isinstance(p2, set) else p2
        difference = abs(p1 - p2)
    

        STRATEGIES = [
            (10, (self.normal_attack, self.normal_attack)),
            (30, (self.superior_attack, self.run)),
            (50, (self.agress_attack, self.run)),
            (float('inf'), (self.superior_agress_attack, self.run))
        ]
    

        thresholds = [t[0] for t in STRATEGIES]
        index = bisect.bisect_left(thresholds, difference)
        _, (strong_strat, weak_strat) = STRATEGIES[index]
    

        return (strong_strat, weak_strat) if p1 > p2 else (weak_strat, strong_strat)
    
    def start_battle(self):
        
        p1_strat, p2_strat = self._determine_behavior()
        
        ONGOING_BATTLES[f"{self.martial_first.name} vs {self.martial_second.name}"] = self
        
        p1_strat(self.martial_first)
        
        p2_strat(self.martial_second) 
        
        decide_battle_rules(self)
        
        p1speed = self.check_turn_speed(self.martial_first)
        p2speed = self.check_turn_speed(self.martial_second)
        
        if p1speed > p2speed:
            first, second = self.martial_first, self.martial_second
        elif p2speed > p1speed:
            first, second = self.martial_second, self.martial_first
        else:
            first, second = (self.martial_first, self.martial_second) if self.martial_first.dexterity >= self.martial_second.dexterity else (self.martial_second, self.martial_first)

        while not self.combat_end_flag:
            for fighter in (first, second):
                if not self._check_alive(fighter):
                    if self.battle_regulations["Killing"]:
                        self.combat_end_flag = True
                        self._end_battle(fighter, reason="battle")
                    else:
                        self.combat_end_flag = True
                        self._end_battle(fighter, reason="battle")
                        opponent.honor -= 5
                    break
                
                opponent = self.martial_second if fighter == self.martial_first else self.martial_first
                
                fighter_health, fighter_qi = fighter.health_status()
                opponent_health, opponent_qi = opponent.health_status()
                
                if self.battle_regulations["Injuring"] or self.battle_regulations["Training"]:
                    if fighter_health <= 50 or opponent_health <= 50:
                        self.combat_end_flag = True
                        self._end_battle(opponent if opponent_health <= 50 else fighter, reason="Training" if self.battle_regulations["Training"] else "battle")
                        break

                if self.battle_regulations["Incapacitating"] or self.battle_regulations["Mock"]:
                    if fighter_health <= 25 or opponent_health <= 25:
                        self.combat_end_flag = True
                        self._end_battle(opponent if opponent_health <= 25 else fighter)
                        break
                
                if not self._check_alive(opponent):
                    if self.battle_regulations["Killing"]:
                        self.combat_end_flag = True
                        self._end_battle(opponent)
                    else:
                        self.combat_end_flag = True
                        self._end_battle(opponent)
                        fighter.honor -= 5
                    break
                self._act(fighter)
                
    def check_rules(self):
        rules = {}
        for rule_name, rule_value in self.battle_regulations.items():
            if rule_value == True:
                rules[rule_name] = rule_value
        return rules
    
    def add_to_action_replay(self, object, data_block = None, _action = "attack"):
        if object.name not in self.action_replay.keys():
            self.action_replay[object.name] = {}
        
        action_id = len(self.action_replay[object.name])
        
        if _action == "attack":
            self.action_replay[object.name][action_id] = {"action": _action, "damage": data_block['damage'], "origin": object.name}
            return
        if _action == "buff" or "debuff" or "heal":
            self.action_replay[object.name][action_id] = {"action": _action, "predicted value w/o tier": ((self.power + object.wisdom + (object.max_qi * 0.10)) * object.realm["Multiplier"])}
            return
        return
    
    def check_run_flag(self, flag, object):
        if not flag:
            return
        
        self.action_replay[object.name] = {"Action 1": f"{object.name} successfully runned from {self.martial_second.name if object == self.martial_first else self.martial_first.name}"}
        self._end_battle(object, "run")
    
    def run(self, martial):
        
        opponent = self.martial_second if martial == self.martial_first else self.martial_first
        rfp = (martial.dexterity * (martial.max_qi * 0.4)) * martial.realm["Multiplier"]
        rofp = (opponent.dexterity * (opponent.max_qi * 0.25)) * opponent.realm["Multiplier"]
        
        rfp = max(0, rfp//100)
        rofp = max(0, rofp//100)
        
        if rfp >= rofp:
            self.pre_flags["Run"] = True
            self.check_run_flag(self.pre_flags["Run"], martial)
        else:
            return
        
    def normal_attack(self, martial):
        self.pre_flags["pre-damage buff"] = 1
        return
    def superior_attack(self, martial):
        self.pre_flags["pre-damage buff"] = 1.2
        return
    def agress_attack(self, martial):
        self.pre_flags["pre-damage buff"] = 1.5
        return
    def superior_agress_attack(self, martial):
        self.pre_flags["pre-damage buff"] = 2
        return
    def safe_zone_damage(self, martial, attacker):
        """Safe zones damage to don't exceed health if rules are obeyed."""
        damage_treshold = 0
        
        injures = {
            "Injuring": martial.vitality * 0.5,
            "Incapacitating": martial.vitality * 0.25,
            "Training": martial.vitality * 0.5,
            "Mock": martial.vitality * 0.25,
        }
               
        if self.battle_regulations["Killing"]:
            possible_amount_damage = martial.vitality
            return possible_amount_damage, "killing"
        else:
            for key, value in self.battle_regulations.items():
                if value and key != "Killing":
                    key_rule = key
                    break  
            if key_rule is None:
                key_rule = "Training"
                
            damage_treshold = injures[key_rule]
            
            possible_amount_damage = int(max(0, martial.max_vitality - damage_treshold))        
            
            factor_key = attacker.obey_krule(self)
            
            if key_rule == "Training":
                return possible_amount_damage, "training"
            if key_rule == "Mock":
                return possible_amount_damage, "mock"
            if factor_key == "disobey":
                possible_amount_damage = martial.vitality
                return possible_amount_damage, factor_key
        return possible_amount_damage, factor_key