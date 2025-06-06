from globals import search_id
class Radar:
    def __init__(self, map, artist, detection_range):
        self.map = map
        self.artist = artist
        self.nodes = self.detect_nearby_cities()
        self.objects = {}
        self.detection_range = detection_range
    
    def scan(self):
        for obj_id in self.map.objects.keys():
            if self.map.manhattan_distance(search_id(obj_id), self.artist) <= self.detection_range:
                self.objects[obj_id] = self.map.objects[obj_id]

    def remove_scan(self):
        for obj_id in self.objects.keys():
            if self.map.manhattan_distance(search_id(obj_id), self.artist) >= self.detection_range + 1:
                self.objects.pop(obj_id)
    
    def detect_nearby_cities(self):
        return self.map.check_nearby_nodes(self.artist)
    
    def purge_nodes(self):
        return self.nodes.clear()