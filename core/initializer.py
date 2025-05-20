from core.techniques import *
from core.globals import *
from core.build import Building
def load_techniques():
    logger.execute("Loading Techniques", "aviso", "Loading the technique interpreter.")
    technique_interpreter()
    time.sleep(0.2)
    logger.execute("Techniques Loaded Successfully", "sucesso", "The Techniques JSON was fully loaded and interpreted.")

def build_dict_unloader(build_dict:dict = BUILD_SLOTS_DICT):
    logger.execute("Unloading build dictionary", "aviso", "Unloading all builds into objects.")
    for build_name, build_values in build_dict.items():
        name = build_name
        possible_levels = build_values["Building Levels"]
        income_type = build_values["Income"]
        income_qty = build_values["Income Quantity"]
        build_type_function = build_values["Specific Function"]
        region_needs = build_values["Region Needs"]
        build_needs = build_values["Build Needs"]
        Settle_Type = build_values["Settlement Type"]
        cost = build_values["Build Cost"]
        current_level = build_values["Current Level"]
        effect = build_values["Build Effects"]
        new_build = Building(name, possible_levels, income_type, income_qty, build_type_function, region_needs, build_needs, Settle_Type, cost, current_level, effect)
        time.sleep(0.2)
    logger.execute("Unloaded build dictionary", "sucesso", "All buildings were unloaded. (Check GLOBAL_BUILD_OBJECTS for more informations.)")

loading_recs = {
    "techniques": load_techniques,
    "buildings": build_dict_unloader
}

def full_load():
    for loading_keys, loading_values in loading_recs.items():
        loading_recs[loading_keys]()
        time.sleep(0.2)