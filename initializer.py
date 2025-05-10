from techniques import *
from globals import *

def load_techniques():
    logger.execute("Loading Techniques", "aviso", "Loading the technique interpreter.")
    technique_interpreter()
    time.sleep(0.2)
    logger.execute("Techniques Loaded Successfully", "sucesso", "The Techniques JSON was fully loaded and interpreted.")

loading_recs = {
    "techniques": load_techniques
}


def full_load():
    for loading_keys, loading_values in loading_recs.items():
        loading_recs[loading_keys]()
        time.sleep(0.2)