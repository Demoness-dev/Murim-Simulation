from globals import *
from techniques import DefenseTechnique, AttackTechnique, SupportTechnique
def tech_evaluator(params:dict, orientation:str, caster, attack_data:dict = None):
    
    def attack_eval(params:dict, weight):
        weight += params.get("power", 0) * 1.5
        weight -= params.get("cost") * 0.5
        if params.get("effect") != "None":
            weight *= 1.1
        if params.get("cost") >= caster.max_qi:
            weight -= 99999999
        return weight
    def defense_eval(params:dict, weight):
        weight += params.get("power", 0) * 2.0
        weight -= params.get("cost") * 0.5
        return weight
    def support_eval(params:dict, weight):
        weight += params.get("power", 0) * 1.5
        weight -= params.get("cost") * 0.5
        if params.get("effect") != "None":
            weight *= 1.2
        return weight
    
    orientations = {
        "attack": lambda params: attack_eval(params, 0),
        "defense": lambda params: defense_eval(params, 0),
        "support": lambda params: support_eval(params, 0)
    }
    
    weight = orientations[orientation](params)
    
    return round(weight, 2)
    

def tech_picker(tech_group, orientation, caster):
    if not tech_group:
        return None, None
    
    best_tech, best_weight = max(((name, tech_evaluator(values, orientation, caster)) for name, values in tech_group.items()), key=lambda x: x[1], default=(None, None))
    
    return best_tech, best_weight


def decide_battle_rules(battle):
    def get_cultivator_preference(martial):
        weights = {
            "Killing": martial.aggression * 0.5 + martial.ruthlessness * 0.3,
            "Incapacitating": martial.strategy * 0.6 + martial.mercy,
            "Injuring": martial.honor * 0.5 + martial.strategy * 0.3 + martial.aggression * 0.2
        }
    
        total_weight = sum(weights.values())
        if total_weight > 0:
            for rule in weights:
                weights[rule] /= total_weight
        
        chosen_rule = random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]
        return chosen_rule, weights[chosen_rule]
    
    if not battle.battle_regulations["Training"]:
        decision1, weight1 = get_cultivator_preference(battle.martial_first)
        decision2, weight2 = get_cultivator_preference(battle.martial_second)

        final_decision = decision1 if weight1 >= weight2 else decision2
    
        battle.battle_regulations[final_decision] = True

        return battle.battle_regulations
    else:
        return battle.battle_regulations