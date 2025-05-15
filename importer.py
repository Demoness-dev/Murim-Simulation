import importlib
from logger import logger
class Importer:
    def import_module(self, module):
        try:
            module = importlib.import_module(module)
            return module
        except ImportError as e:
            logger.execute("Importer Error", "erro", f"Error importing module {module} / {e}")
            return None
    
    def class_importer(self, module, class_name):
        try:
            module = self.import_module(module)
            cls = getattr(module, class_name)
            return cls
        except (ImportError, AttributeError) as e:
            logger.execute("Importer Error", "erro", f"Error importing a Class {class_name} / {e}")
            return None