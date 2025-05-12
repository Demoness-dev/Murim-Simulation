from globals import GLOBAL_BUILD_OBJECTS


class Building:
    def __init__(self, name, p_levels, income_type, income_qty, build_function, region_needs, build_needs, settle_type, cost, current_level, effect):
        self.name = name
        self.p_levels = p_levels
        self.income_t = income_type
        self.income_q = income_qty
        self.build_function = build_function
        self.region_needs = region_needs
        self.build_needs = build_needs
        self.settle_type = settle_type
        self.cost = cost
        self.current_level = current_level
        self.effect = effect
        self.append_to_dict()
        
    def append_to_dict(self):
        GLOBAL_BUILD_OBJECTS[self.name] = self
    
    def call_function(self):
        pass