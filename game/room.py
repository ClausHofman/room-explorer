from creature import Creature
from items_and_equipment import Item, GameObject, Equipment

current_player_room = None
room_count = 0
game_rooms = []

class Room:
    @staticmethod
    def available_directions():
        # TODO: update so that it correctly returns the directions that are available for the current room
        return ['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest', 'up', 'down']
    
    def __init__(self, name, description):
        global room_count
        self.name = name
        self.description = description
        self.exits = {}
        self.objects = []
        self.creatures = []
        self.inventory = []
        # Increment room count
        room_count += 1

    # def get_equipment_by_name(self, equipment_name):
    #     # Normalize input to lowercase for case-insensitive comparison
    #     normalized_name = equipment_name.lower()
    #     for equipment in self.inventory:
    #         if equipment.name.lower() == normalized_name:
    #             return equipment
    #     return None  # Return None if equipment is not found

    def add_equipment(self, equipment):
        self.inventory.append(equipment)

    def connect(self, direction, neighbor_room):
        if direction in self.available_directions():
            self.exits[direction] = neighbor_room
        else:
            raise ValueError(f"Invalid direction '{direction}' for room '{self.name}'")

    # def available_directions(self):
    #     # print(list(self.exits.keys()))
    #     return list(self.exits.keys())

    def create_object(self, object_name, object_description):
        new_object = GameObject(object_name, object_description)
        self.objects.append(new_object)
        print(f"{new_object.name} created in {self.name}.")

    def create_item(self, item_name, item_description):
        new_item = Item(item_name, item_description)
        self.inventory.append(new_item)
        print(f"{new_item.name} created in {self.name}.")
    

    def remove_object(self, object_name):
        for obj in self.objects:
            if obj.name == object_name:
                self.objects.remove(obj)
                print(f"{object_name} removed from {self.name}.")
                return
        print(f"No object named '{object_name}' found in {self.name}.")

    def create_creature(self, creature_name, creature_description, move_interval):
        new_creature = Creature(creature_name, creature_description, self, move_interval)
        self.creatures.append(new_creature)
        print(f"{new_creature.name} created.")
        return new_creature

    def remove_creature(self, creature_name):
        for creature in self.creatures:
            if creature.name == creature_name:
                creature.stop_wandering()  # Stop the creature's thread if it's wandering
                self.creatures.remove(creature)
                print(f"{creature_name} suddenly disappears from existence, *POOF*")
                return
        print(f"No creature named '{creature_name}' found in {self.name}.")

    def move_creature(self, creature_name):
        for creature in self.creatures:
            if creature.name == creature_name:
                creature.start_wandering()
                return True
        print(f"No creature named '{creature_name}' found.")
        return False
    
    def stop_creature(self, creature_name):
        for creature in self.creatures:
            if creature.name == creature_name:
                creature.stop_wandering()
                return True
        print(f"No creature named {creature_name} found.")
        return False

    def add_to_inventory(self, item):
        self.inventory.append(item)
        print(f"{item} added to {self.name} inventory.")

    def remove_from_inventory(self, item_name):
        if item_name in self.inventory:
            del self.inventory[item_name]
            print(f"{item_name} removed from {self.name} inventory.")
        else:
            print(f"No item named '{item_name}' found in {self.name} inventory.")

    # def display_inventory(self):
    #     if self.inventory:
    #         print(f"Inventory of {self.name}:")
    #         for item_name, description in self.inventory.items():
    #             print(f"{item_name}: {description}")
    #     else:
    #         print(f"{self.name} has no items in inventory.")

    def object_descriptions(self):
        if self.objects:
            for obj in self.objects:
                print(f"{obj.description}")
        if self.creatures:
            for creature in self.creatures:
                print(f"{creature.description}")
        if len(self.inventory) > 0:
            inventory_str = ""
            for item in self.inventory:
                inventory_str += f"{item.name}, "
            if inventory_str.endswith(", "):
                inventory_str = inventory_str[:-2]
            print(inventory_str)
        else:
            pass

    def display_object_names(self):
        if self.objects:
            for obj in self.objects:
                print(f"{obj.name}")
        if self.creatures:
            for creature in self.creatures:
                print(f"{creature.name}")
        if len(self.inventory) > 0:
            inventory_str = ""
            for item in self.inventory:
                inventory_str += f"{item.name}, "
            if inventory_str.endswith(", "):
                inventory_str = inventory_str[:-2]
            print(inventory_str)
        else:
            pass

    def __repr__(self):
        return f"Room(name='{self.name}', description='{self.description}')"

# Function to update the current player's room
def update_current_player_room(new_room):
    global current_player_room
    current_player_room = new_room

def create_game_world():

    # Create rooms
    room1 = Room("Hall", "You are in a grand hall with a doorway leading to north.")
    room2 = Room("Kitchen", "You are in a cozy kitchen with a stove and a table.")
    room3 = Room("Garden", "You are in a beautiful garden with flowers and a fountain.")
    room4 = Room("Test1", "A generic room")
    room5 = Room("Test1", "A generic room")
    room6 = Room("Test1", "A generic room")
    room7 = Room("Test1", "A generic room")
    room8 = Room("Test1", "A generic room")
    room9 = Room("Test1", "A generic room")
    room10 = Room("Test1", "A generic room")
    room11 = Room("Test1", "A generic room")

    # Connect rooms
    room1.connect('north', room2)
    room2.connect('south', room1)
    room1.connect('northeast', room3)
    room3.connect('southwest', room1)
    room1.connect('east', room4)
    room4.connect('west', room1)
    room1.connect('southeast', room5)
    room5.connect('northwest', room1)
    room1.connect('south', room6)
    room6.connect('north', room1)
    room1.connect('southwest', room7)
    room7.connect('northeast', room1)
    room1.connect('west', room8)
    room8.connect('east', room1)
    room1.connect('northwest', room9)
    room9.connect('southeast', room1)
    room1.connect('up', room10)
    room10.connect('down', room1)
    room1.connect('down', room11)
    room11.connect('up', room1)

    sword = Equipment("Sword", "weapon", "wield", attack=10)

    # Add the equipment to the room
    room1.add_equipment(sword)

    # found_equipment = room1.get_equipment_by_name("sword")
    # if found_equipment:
    #     print(f"Found equipment: {found_equipment.name}")
    # else:
    #     print("Equipment not found.")
    
    global game_rooms
    game_rooms = [room1, room2, room3, room4, room5, room6, room7, room8, room9, room10, room11]

    return room1  # Starting room