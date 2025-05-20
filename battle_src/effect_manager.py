class EffectManager:
    def __init__(self):
        self.active_effects = {}

        self.effect_actions = {
            "stat increase": lambda target, eff: setattr(target, eff["stat"], getattr(target, eff["stat"]) + eff["value"]),
            "stat decrease": lambda target, eff: setattr(target, eff["stat"], max(0, getattr(target, eff["stat"]) - eff["value"])),
            "burn": lambda target, eff: self._apply_burn(target, eff),
            "poison": lambda target, eff: setattr(target, "max_vitality", max(0, target.max_vitality - eff["value"] // 2)),
            "stun": lambda target, eff: setattr(target, "stunned", True),
            "heal_dot": lambda target, eff: self._apply_heal(target, eff)
        }
    def _apply_burn(self, target, eff):
        target.max_vitality = max(0, target.max_vitality - eff["value"])
        target.base_defense = max(0, target.base_defense - (eff["value"] // 2))  
    def _apply_heal(target, eff):
        target.max_vitality = min(target.vitality, target.max_vitality + eff["value"])
    def apply_effect(self, target, stat_name=None, value=0, duration=1, effect_type="stat increase", decay=0):
        if target.name not in self.active_effects:
            self.active_effects[target.name] = []

        effect_data = {
            "stat": stat_name,
            "value": value,
            "remaining_turns": duration,
            "effect_type": effect_type,
            "decay": decay
        }
        self.active_effects[target.name].append(effect_data)

        if effect_type in self.effect_actions:
            self.effect_actions[effect_type](target, effect_data)

    def update_effects(self, target):
        if target.name not in self.active_effects:
            return

        effects_to_remove = []
        for effect in self.active_effects[target.name]:
            if effect["remaining_turns"] > 0:
                effect["remaining_turns"] -= 1

                if effect["decay"] > 0 and effect["stat"]:
                    effect["value"] = max(0, effect["value"] - effect["decay"])

                if effect["effect_type"] in self.effect_actions:
                    self.effect_actions[effect["effect_type"]](target, effect)

            if effect["remaining_turns"] <= 0:
                effects_to_remove.append(effect)

        for effect in effects_to_remove:
            self.active_effects[target.name].remove(effect)

        if "stun" not in [e["effect_type"] for e in self.active_effects[target.name]]:
            target.stunned = False  

    def remove_all_effects(self, target):
        if target.name in self.active_effects:
            for effect in self.active_effects[target.name]:
                if effect["effect_type"] == "stat increase":
                    setattr(target, effect["stat"], getattr(target, effect["stat"]) - effect["value"])
                elif effect["effect_type"] == "stat decrease":
                    setattr(target, effect["stat"], getattr(target, effect["stat"]) + effect["value"])
            del self.active_effects[target.name]
