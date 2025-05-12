from sect import Sect
from city import City
from globals import regions
import random
from console_writer import log
from martial_artist_definition import MartialArtist
class NodeMap:
    def __init__(self, name, trade_system, x=10, y=10):
        self.map_name = name
        self.nodes = {}
        self.nodes_region_type = {} #Each node will have a region modifier anexed with its coord.
        self.nodes_routes = {}
        self.grid_size = {"x": x, "y": y}
        self.trade_system = trade_system
        self.objects = {}
        self.regions = regions

    def add_node_coord(self, node: object, x=None, y=None) -> None:
        if len(self.nodes) >= self.grid_size["x"] * self.grid_size["y"]:
            log.error("Map is full. Cannot add more nodes.")
        
        x_coords = random.randint(0, self.grid_size["x"] - 1) if x is None else x
        y_coords = random.randint(0, self.grid_size["y"] - 1) if y is None else y

        coords = self.find_unique_coord(self.nodes, x_coords, y_coords)

        self.nodes[(coords[0], coords[1])] = node
        node.set_coords(x_coords, y_coords)

    def time_node_check(self) -> None:
        for node in self.nodes.values():
            node.nearby_nodes = self.check_nearby_nodes(node)

    def create_region_object(self, region_object:dict) -> None:
        if len(self.nodes_region_type) >= self.grid_size["x"] * self.grid_size["y"]:
            log.error("Map is full. Cannot add more region objects.")
            
        x_coords = random.randint(0, self.grid_size["x"] - 1)
        y_coords = random.randint(0, self.grid_size["y"] - 1)
        
        coords = self.find_unique_coord(self.nodes_region_type, x_coords, y_coords)
        
        self.nodes_region_type[(coords[0], coords[1])] = self.regions[region_object["Region Name"]]

    def create_city(self) -> None:
        new_city = City(self, self.trade_system)
        self.add_node_coord(new_city)
        new_city.nearby_nodes = self.check_nearby_nodes(new_city)
        log.info(f"City {new_city.city_name} created at coordinates ({new_city.coords[0]}, {new_city.coords[1]})")

    def create_sect(self, leader=None) -> None:
        new_sect = Sect(self, self.trade_system, leader if leader else None)
        self.add_node_coord(new_sect)
        new_sect.nearby_nodes = self.check_nearby_nodes(new_sect)
        log.info(f"Sect {new_sect.sect_name} created at coordinates ({new_sect.coords[0]}, {new_sect.coords[1]})")

    def create_martial_artist(self, sect=None, coords:tuple = None) -> None:
        new_artist = MartialArtist(self, self.trade_system, sect)
        new_artist.position = coords if coords else self.generate_martial_coords()
        log.info(f"Custom martial artist {new_artist}({new_artist.name}) created at {new_artist.position}")
        
    def generate_martial_coords(self, sect:Sect = None) -> tuple:
        if sect and sect in self.nodes.values():
            return sect.coords
        if sect not in self.nodes.values():
            log.error(f"Sect {sect.city_name} is not on the map and is trying to generate a martial artist.")
        if sect == None:
            x_coords = random.randint(0, self.grid_size["x"] - 1)
            y_coords = random.randint(0, self.grid_size["y"] - 1)
            return (x_coords, y_coords)
        
    def manhattan_distance(self, node1, node2) -> int:
        return abs(node1.coords[0] - node2.coords[0]) + abs(node1.coords[1] - node2.coords[1])

    def create_node_route(self, node) -> None:
        if node not in self.nodes.values():
            log.error("Node does not exist in the map.")
            return
        for other_node in self.nodes.values():
            if other_node != node:
                if other_node.city_name not in self.nodes_routes.get(node, {}).get("Connected Nodes", {}):
                    self.create_route(node, other_node)
        log.info(f"Routes attempted for node {getattr(node, 'city_name', repr(node))}.")

    def check_nearby_nodes(self, node) -> dict:
        nearby_nodes = {}
        for other_node in self.nodes.values():
            if other_node != node:
                distance = self.manhattan_distance(node, other_node)
                if distance <= 2:
                    nearby_nodes[other_node] = {
                        "Distance": distance,
                        "Coords": other_node.coords,
                        "object": other_node
                    }
        return nearby_nodes

    def check_distance(self, node1, node2) -> bool:
        if node1 == node2:
            log.error("Cannot compute distance between the same node.")
            return False
        if node1 not in self.nodes.values() or node2 not in self.nodes.values():
            log.error("One of the nodes is not in the map.")
            return False

        distance = self.manhattan_distance(node1, node2)
        max_possible_distance = (self.grid_size["x"] + self.grid_size["y"]) * 2

        if distance > max_possible_distance * 0.66:
            log.warning(f"Distance between {node1.city_name} and {node2.city_name} is too large: {distance}.")
            return False
        return True

    def create_route(self, node1, node2) -> None:
        if node1 not in self.nodes.values() or node2 not in self.nodes.values():
            log.error("One of the nodes is not in the map.")
        if not self.check_distance(node1, node2):
            log.error("Distance between nodes is too large.")

        if node1 not in self.nodes_routes:
            self.nodes_routes[node1] = {"Connected Nodes": {}, "Coords": {}}
        if node2 not in self.nodes_routes:
            self.nodes_routes[node2] = {"Connected Nodes": {}, "Coords": {}}

        if node2.city_name not in self.nodes_routes[node1]["Connected Nodes"]:
            self.nodes_routes[node1]["Connected Nodes"][node2.city_name] = node2
            self.nodes_routes[node1]["Coords"][node2.coords] = node2.city_name

            self.nodes_routes[node2]["Connected Nodes"][node1.city_name] = node1
            self.nodes_routes[node2]["Coords"][node1.coords] = node1.city_name

            log.info(f"Route created between {node1.city_name} and {node2.city_name}.")
        else:
            log.info(f"Route already exists between {node1.city_name} and {node2.city_name}.")

    def get_node(self, coords: tuple) -> tuple:
        if coords in self.nodes:
            return self.nodes[coords]
        else:
            log.error(f"Node at coordinates {coords} does not exist.")
            return None

    def move_artist(self, artist: MartialArtist, new_coords: tuple) -> None:
        if artist not in self.objects.values():
            log.error("Artist not found in the map.")
            
        if artist.position == new_coords:
            log.error("Artist is already at the target coordinates.")
            
        distance = self.manhattan_distance(artist, self.get_node(new_coords))
        if distance <= 2:
            artist.position = new_coords
            log.info(f"Artist {artist.name} moved to coordinates {new_coords}.")
    
    def find_unique_coord(self, node_dict:dict, x_coords, y_coords) -> tuple :
        while (x_coords, y_coords) in node_dict:
            x_coords = random.randint(0, self.grid_size["x"] - 1)
            y_coords = random.randint(0, self.grid_size["y"] - 1)
        return (x_coords, y_coords)