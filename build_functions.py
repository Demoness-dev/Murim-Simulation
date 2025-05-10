import json
from node_map import load_json
class Building():
    def __init__(self, name, city):
        self.name = name
        self.city = city
    
    def apply_effect(self):
        pass
    

class Marketplace(Building):
    def __init__(self, city):
        super().__init__("Marketplace", city)
    
    def apply_effect(self):
        pass
    
    def get_items(self):
        inv = self.city.market_inventory
        selling_products = {}
        all_items = load_json(filename="items.json")
        for item in inv:
            if item in all_items:
                selling_products[item] = all_items[item]
        return selling_products
    
    def buy_item(self, buyer, item, q = 1):
        if buyer.inventory["Spirit Stones"] < item["Cost"] * q:
            return
        if self.city.market_inventory[item["Name"]]["Quantity"] < q:
            return
        buyer.inventory["Spirit Stones"] -= item["Cost"] * q
        if item["Name"] in buyer.inventory:
            buyer.inventory[item["Name"]]["Quantity"] += q
        else:
            buyer.inventory[item["Name"]] = {**item, "Quantity": q}
        self.city.market_inventory[item["Name"]]["Quantity"] -= q
        if self.city.market_inventory[item["Name"]]["Quantity"] <= 0:
            del self.city.market_inventory[item["Name"]]
        self.city.resources["Spirit Stones"] += item["Cost"] * q