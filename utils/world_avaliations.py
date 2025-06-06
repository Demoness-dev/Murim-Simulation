from core.globals import MARTIAL_WORLD_LIST
from collections import defaultdict

def global_average(attribute_paths):
    """
    Calculates averages of multiple attributes for all artists in MARTIAL_WORLD_LIST.

    Params:
        attribute_paths (list): list of strings with paths, e.g.:
            ["qi", "vitality", "stats.str", "stats.dex"]

    Returns:
        dict: keys are the attributes, values are the averages.
    """
    
    sums = defaultdict(float)
    counts = defaultdict(int)
    
    for artist in MARTIAL_WORLD_LIST.values():
        for path in attribute_paths:
            value = get_nested_attr(artist, path)
            if value is not None:
                sums[path] += value
                counts[path] += 1
    
    averages = {}
    for path in attribute_paths:
        if counts[path] > 0:
            averages[path] = sums[path] / counts[path]
        else:
            averages[path] = 0.0
    return averages


def get_nested_attr(obj, path):
    try:
        parts = path.split(".")
        for part in parts:
            if isinstance(obj, dict):
                obj = obj.get(part)
            else:
                obj = getattr(obj, part, None)
        return obj
    except Exception:
        return None