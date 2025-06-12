import random
from rich.console import Console
console = Console()
class PointOfInterest:
    def __init__(self, name, poi_type, depth):
        self.name = name
        self.type = poi_type  
        self.depth = depth
        self.visited = False
class Zone:
    def __init__(self, name, start_depth, end_depth):
        self.name = name
        self.start_depth = start_depth
        self.end_depth = end_depth
        self.points_of_interest = []
    def add_poi(self, poi):
        self.points_of_interest.append(poi)
class Map:
    def __init__(self, max_depth=2000):
        self.max_depth = max_depth
        self.zones = []
        self.generate_map()
    def generate_map(self):
        zone_names = ["Sunlight Zone", "Twilight Zone", "Midnight Zone", "Abyssal Zone", "Hadal Zone"]
        poi_types = ['wreck', 'cave', 'hydrothermal_vents', 'outpost', 'monster_lair']
        current_depth = 0
        zone_depth_range = self.max_depth // len(zone_names)
        for i, name in enumerate(zone_names):
            start_depth = current_depth
            end_depth = current_depth + zone_depth_range
            zone = Zone(name, start_depth, end_depth)
            num_pois = random.randint(1, 3)
            for _ in range(num_pois):
                poi_depth = random.randint(start_depth + 50, end_depth - 50)
                poi_type = random.choice(poi_types)
                poi_name = f"Unidentified {poi_type.replace('_', ' ').title()}"
                poi = PointOfInterest(poi_name, poi_type, poi_depth)
                zone.add_poi(poi)
            self.zones.append(zone)
            current_depth = end_depth
    def get_zone_at_depth(self, depth):
        for zone in self.zones:
            if zone.start_depth <= depth < zone.end_depth:
                return zone
        return None
    def get_pois_near_depth(self, depth, range=50):
        current_zone = self.get_zone_at_depth(depth)
        if not current_zone:
            return []
        nearby_pois = []
        for poi in current_zone.points_of_interest:
            if abs(poi.depth - depth) <= range:
                nearby_pois.append(poi)
        return nearby_pois
    def print_map(self, player_depth):
        console.print("\n[bold]Submarine Cartography[/bold]")
        for zone in self.zones:
            player_marker = ""
            if zone.start_depth <= player_depth < zone.end_depth:
                player_marker = " < (You are here)"
            console.print(f"\n[cyan] - {zone.name} ({zone.start_depth}m - {zone.end_depth}m){player_marker}[/cyan]")
            if not zone.points_of_interest:
                console.print("    [italic]No points of interest detected.[/italic]")
            else:
                for poi in sorted(zone.points_of_interest, key=lambda p: p.depth):
                    visited_marker = "[green](Visited)[/green]" if poi.visited else ""
                    console.print(f"    - {poi.name} at {poi.depth}m {visited_marker}")