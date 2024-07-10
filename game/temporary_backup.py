import time
import random
import threading
from prompt_toolkit import prompt
import json
from pprint import pprint

room_count = 0
game_rooms = []
current_player_room = None  # Initialize the global variable

# Function to update the current player's room
def update_current_player_room(new_room):
    global current_player_room
    current_player_room = new_room

def save_game(player, filename):
    filename = str(filename)

    if not filename.endswith('.json'):
        filename += '.json'

    backup_filename = filename + '.bak'

    global game_rooms, room_count

    # serialized_rooms = serialize_rooms(game_rooms)

    # player_state = {
    #     'name': player.name,
    #     'current_room': player.current_room.name,
    #     'inventory': serialize_inventory(player.inventory)
    # }

    # game_state = {
    #     'player': player_state,
    #     'rooms': serialized_rooms,
    #     'room_count': room_count
    # }

    # Assuming rooms is a list of Room objects
    serialized_game_state = {
        'rooms': serialize_rooms(game_rooms),
        'player': {
            'name': player.name,
            'current_room': player.current_room.name,
            'inventory': player.inventory if player.inventory else {}  # Serialize empty inventory as {}
        },
        'room_count': room_count
    }

    # Save serialized_game_state to a file using JSON, for example
    try:
        with open(filename, 'w') as f:
            json.dump(serialized_game_state, f, indent=4)
        print(f"Game state saved to '{filename}'.")
    except Exception as e:
            print(f"Error occurred while saving to main file '{filename}': {e}")

    # try:
    #     with open(backup_filename, 'w') as backup_file:
    #         json.dump(game_state, backup_file, indent=4)
    #     print(f"Game state saved to backup file '{backup_filename}'.")
    # except Exception as e:
    #     print(f"Error occurred while saving to backup file '{backup_filename}': {e}")
    #     return False

    # try:
    #     with open(filename, 'w') as f:
    #         json.dump(game_state, f, indent=4)
    #     print(f"Game state saved to '{filename}'.")
    #     return True
    # except Exception as e:
    #     print(f"Error occurred while saving to main file '{filename}': {e}")
    #     return False

def load_game(filename):
    filename = str(filename)

    global game_rooms, room_count

    if not filename.endswith('.json'):
        filename += '.json'

    with open(filename, 'r') as f:
        game_state = json.load(f)

    room_dict = {}

    for room_data in game_state.get('rooms', []):
        room = Room(room_data['name'], room_data['description'])
        room.objects = [GameObject(obj['name'], obj['description']) for obj in room_data.get('objects', [])]
        room.inventory = deserialize_inventory(room_data.get('inventory', {}))
        room.creatures = [Creature.from_dict(creature_data, room_dict) for creature_data in room_data.get('creatures', [])]
        room_dict[room.name] = room

    valid_directions = Room.available_directions()

    for room_data in game_state.get('rooms', []):
        room = room_dict[room_data['name']]
        exits = room_data.get('exits', {})
        for direction, room_name in exits.items():
            if direction in valid_directions:
                if room_name in room_dict:
                    neighbor_room = room_dict[room_name]
                    room.connect(direction, neighbor_room)
                else:
                    print(f"Warning: Neighbor room '{room_name}' not found for direction '{direction}' in room '{room.name}'.")
            else:
                print(f"Warning: Direction '{direction}' not recognized in room '{room.name}'.")

    for room_data in game_state.get('rooms', []):
        room = room_dict[room_data['name']]
        for creature_data in room_data.get('creatures', []):
            current_room_name = creature_data.get('current_room')
            current_room = room_dict.get(current_room_name, None)
            creature = Creature.from_dict(creature_data, room_dict)
            room.creatures.append(creature)

    player_data = game_state.get('player', {})
    current_room_name = player_data.get('current_room')
    current_room = room_dict.get(current_room_name, None)
    if current_room is None:
        print(f"Error: Current room '{current_room_name}' for player not found.")
    player = Player(player_data['name'], current_room)
    player.inventory = deserialize_inventory(player_data.get('inventory', {}))

    room_count = game_state.get('room_count', 0)
    game_rooms = list(room_dict.values())

    return player, game_rooms

def serialize_inventory(inventory):
    serialized_inventory = {}
    for key, value in inventory.items():
        serialized_inventory[key.__name__] = value.to_dict()
    return serialized_inventory

def deserialize_inventory(serialized_inventory):
    inventory = {}
    for key, value in serialized_inventory.items():
        class_name = globals().get(key, None)
        if class_name:
            inventory[class_name] = class_name.from_dict(value)
    return inventory

# Updated serialization function
def serialize_rooms(rooms):
    serialized_rooms = []
    for room in rooms:
        # Serialize exits to contain only the names of the neighboring rooms
        exits = {direction: neighbor.name for direction, neighbor in room.exits.items()}
        serialized_creatures = [serialize_creature(creature) for creature in room.creatures]
        serialized_room = {
            'name': room.name,
            'description': room.description,
            'exits': exits,
            'objects': [obj.__dict__ for obj in room.objects],
            'creatures': serialized_creatures,  # Serialize creatures as objects
            'inventory': room.inventory if room.inventory else {}  # Ensure empty inventory is {}
        }
        serialized_rooms.append(serialized_room)
    return serialized_rooms

# def serialize_rooms(rooms):
#     serialized_rooms = []
#     for room in rooms:
#         # Serialize exits to contain only the names of the neighboring rooms
#         exits = {direction: neighbor.name for direction, neighbor in room.exits.items()}
#         serialized_room = {
#             'name': room.name,
#             'description': room.description,
#             'exits': exits,
#             'objects': [{'name': obj.name, 'description': obj.description} for obj in room.objects],
#             'creatures': [serialize_creature(creature) for creature in room.creatures],
#             'inventory': serialize_inventory(room.inventory) if room.inventory else {}  # Ensure empty inventory is {}
#         }
#         serialized_rooms.append(serialized_room)
#     return serialized_rooms


def serialize_creature(creature):
    if isinstance(creature, Creature):
        serialized_creature = {
            'name': creature.name,
            'description': creature.description,
            'current_room': creature.current_room.name,  # Serialize room name
            'move_interval': creature.move_interval,
            'wandering': creature.wandering
            # Add more attributes as needed
        }
        return serialized_creature
    else:
        raise TypeError(f"Expected instance of Creature, got {type(creature)}")

def deserialize_creature(self, serialized_creature):
    # Simulate deserialization process (creating a new Creature instance)
    name = serialized_creature['name']
    description = serialized_creature['description']
    move_interval = serialized_creature['move_interval']
    # Create a new Creature instance and return it
    return Creature(name, description, self, move_interval)

def serialize_equipment(equipment):
    return {
        'name': equipment.name,
        'type': equipment.type,
        'slot': equipment.slot,
        'attack': equipment.attack,
        'defense': equipment.defense
    }

# def serialize_creature(creature):
#     serialized_creature = {
#         'name': creature.name,
#         'description': creature.description,
#         'current_room': creature.current_room.name,  # Serialize room name
#         'move_interval': creature.move_interval,
#         'wandering': creature.wandering
#         # Add more attributes as needed
#     }
#     return serialized_creature

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

        def __str__(self):
            return f"{self.name}"

class Room:
    @staticmethod
    def available_directions():
        return ['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest', 'up', 'down']
    
    def __init__(self, name, description):
        global room_count
        self.name = name
        self.description = description
        self.exits = {}
        self.objects = {}
        self.creatures = {}
        self.inventory = {}
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
        pass
        # self.inventory.append(equipment)

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
        self.creatures[new_creature.name] = new_creature  # Store creature in the dictionary
        
        # Serialize and print the room after adding the creature
        serialized_room = self.serialize()
        print("Serialized Room:")
        print(json.dumps(serialized_room, indent=2))

        return new_creature

    def serialize(self):
        # Serialize the room, replacing 'creatures' key with the Creature class object
        serialized_creatures = {creature_name: self.serialize_creature(creature) for creature_name, creature in self.creatures.items()}
        
        serialized_room = {
            'name': self.name,
            'description': self.description,
            str(Creature): serialized_creatures,  # Convert Creature class to string
            # Add other attributes as needed
        }
        return serialized_room

    # def serialize(self):
    #     serialized_creatures = [self.serialize_creature(creature) for creature in self.creatures.values()]
        
    #     serialized_room = {
    #         'name': self.name,
    #         'description': self.description,
    #         'creatures': serialized_creatures,
    #         # Add other attributes as needed
    #     }
    #     return serialized_room

    def serialize_creature(self, creature):
        serialized_creature = {
            'name': creature.name,
            'description': creature.description,
            'current_room': creature.current_room.name,  # Serialize room name
            'move_interval': creature.move_interval,
            'wandering': creature.wandering
            # Add more attributes as needed
        }
        # print(f"Printing serialized creature {serialized_creature}")
        return serialized_creature

    @staticmethod
    def deserialize(serialized_room):
        room = Room(serialized_room['name'], serialized_room['description'])
        creatures_data = serialized_room.get(str(Creature), {})
        for creature_name, creature_data in creatures_data.items():
            creature = Creature(
                creature_data['name'],
                creature_data['description'],
                room,  # Pass the room instance to the creature's current_room
                creature_data['move_interval']
            )
            creature.wandering = creature_data['wandering']
            room.creatures[creature_name] = creature
        
        return room

    # def create_creature(self, creature_name, creature_description, move_interval):
    #     new_creature = Creature(creature_name, creature_description, self, move_interval)
    #     self.creatures[new_creature.name] = new_creature  # Add creature to room's creatures dictionary
    #     print(f"{new_creature.name} created and added to the room.")
    #     return new_creature

    # def create_creature(self, creature_name, creature_description, move_interval):
    #     new_creature = Creature(creature_name, creature_description, self, move_interval)
    #     self.creatures.append(new_creature)
    #     print(f"{new_creature.name} created.")
    #     return new_creature

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
            for creature_name, creature in self.creatures.items():
                print(f"{creature.description}")
        
        if self.inventory:
            inventory_str = ", ".join(item.name for item in self.inventory.values())
            print(inventory_str)

    # def object_descriptions(self):
    #     if self.objects:
    #         for obj in self.objects:
    #             print(f"{obj.description}")
    #     if self.creatures:
    #         for creature in self.creatures:
    #             print(f"{creature.description}")
    #     if len(self.inventory) > 0:
    #         inventory_str = ""
    #         for item in self.inventory:
    #             inventory_str += f"{item.name}, "
    #         if inventory_str.endswith(", "):
    #             inventory_str = inventory_str[:-2]
    #         print(inventory_str)
    #     else:
    #         pass

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
    
class GameObject:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Creature:
    def __init__(self, name, description, current_room, move_interval=10):
        self.name = name
        self.description = description
        self.current_room = current_room
        self.move_interval = move_interval
        self.thread = None
        self.quit_flag = threading.Event()
        self.condition = threading.Condition()
        self.wandering = False  # Initialize wandering state to False

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "current_room": self.current_room.name,  # Assuming room has a 'name' attribute
            "move_interval": self.move_interval,
            "wandering": self.wandering
            # Add more attributes as needed
        }

    @classmethod
    def from_dict(cls, data, room_dict):
        name = data['name']
        description = data['description']
        current_room_name = data['current_room']
        current_room = room_dict.get(current_room_name, None)
        if current_room is None:
            raise ValueError(f"Room '{current_room_name}' not found for creature '{name}'")
        move_interval = data.get('move_interval', 10)  # Default move_interval to 10 if not provided
        wandering = data.get('wandering', False)  # Default wandering to False if not provided
        return cls(name, description, current_room, move_interval)

    # Other methods as needed

    def start_wandering(self):
        self.wandering = True
        if self.thread is None:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def move_randomly(self):
        global current_player_room

        while not self.quit_flag.is_set():
            available_directions = self.current_room.available_directions()
            if available_directions:
                direction = random.choice(available_directions)
                next_room = self.current_room.exits[direction]

                if self.current_room == current_player_room:
                    print(f"{self.name} leaves to the {direction}.")
                self.change_room(next_room)

                # Check if the creature is moving into the player's current room
                if next_room == current_player_room:
                    print(f"{self.name} arrives from the {direction}.")
                
            with self.condition:
                if not self.quit_flag.is_set():
                    self.condition.wait(self.move_interval)

    def run(self):
        self.move_randomly()

    def stop_wandering(self):
        self.wandering = False
        if self.thread is not None:
            with self.condition:
                self.quit_flag.set()
                self.condition.notify_all()
            self.thread.join()

    def change_room(self, new_room):
        # Remove creature from the current room
        self.current_room.creatures.remove(self)
        # Update the current room to the new room
        self.current_room = new_room
        # Add creature to the new room
        new_room.creatures.append(self)

    def __str__(self):
        return f"Creature: {self.name}, Description: {self.description}, Current Room: {self.current_room.name}"
    
class Equipment:
    def __init__(self, name, type, slot, attack=0, defense=0):
        self.name = name
        self.type = type  # Type of equipment: weapon, armor, accessory, etc.
        self.slot = slot
        self.attack = attack
        self.defense = defense

    def __str__(self):
        return f"{self.name} ({self.type}): Attack {self.attack}, Defense {self.defense}"

class Player:
    def __init__(self, name, current_room):
        self.name = name
        self.current_room = current_room
        self.inventory = {}
        self.equipment = {}

    EQUIPMENT_SLOTS = ['torso', 'wield']  # Example equipment slots

    def equip_item(self, item):
        if isinstance(item, Equipment):
            slot = item.slot  # Assuming Equipment has a 'slot' attribute
            if slot in self.equipment:
                print(f"You are already wielding {self.equipment[slot].name}.")
                return False
            else:
                # Remove item from inventory and equip it
                if item in self.inventory:
                    self.inventory.remove(item)
                self.equipment[slot] = item
                print(f"You wield {item.name}.")
                return True
        else:
            print("You can only wield equipment.")
            return False

    def unequip_item(self, slot_name):
        if slot_name in self.equipment:
            item = self.equipment.pop(slot_name)
            self.inventory.append(item)  # Add item back to inventory
            print(f"You unequipped {item.name}.")
            return item
        else:
            print(f"No item equipped in {slot_name} slot.")
            return None

    def list_equipment(self):
        print("Currently equipped items:")
        for slot_name, item in self.equipment.items():
            print(f"- {slot_name}: {item}")

    def move(self, direction):
        global current_player_room  # Access the global variable
        if direction in self.current_room.exits:
            self.current_room = self.current_room.exits[direction]
            update_current_player_room(self.current_room)
            print("\nAvailable directions:", self.current_room.available_directions())
            print(f"You moved {direction} to {self.current_room.name}.")
            print(self.current_room.description)
            if self.current_room.objects:
                for obj in self.current_room.objects:
                    print(f"{obj.description}")
            if self.current_room.creatures:
                for creature in self.current_room.creatures:
                    print(f"{creature.description}")
        else:
            print("You can't go that way.")

    def create_object(self, object_name, object_description):
        self.current_room.create_object(object_name, object_description)

    def create_item(self, item_name, item_description):
        self.current_room.create_item(item_name, item_description)

    def remove_object(self, object_name):
        self.current_room.remove_object(object_name)       

    def look(self):
        self.current_room.object_descriptions()
    
    def object_names(self):
        self.current_room.display_object_names()
    
    # def show_exits(self):
    #     self.current_room.available_directions()
    
    def create_creature(self, creature_name, creature_description, move_interval):
        return self.current_room.create_creature(creature_name, creature_description, move_interval)
    
    def remove_creature(self, creature_name):
        self.current_room.remove_creature(creature_name)

    def enable_wandering(self, creature_name):
        for creature in self.current_room.creatures:
            if creature.name == creature_name:
                creature.start_wandering()
                print(f"{creature_name} starts wandering around.")
                return
        print(f"Creature named {creature_name} not found.")
    
    def disable_wandering(self, creature_name):
        if self.current_room.stop_creature(creature_name):
            print(f"{creature_name} stops wandering around.")
        else:
            print(f"Failed to stop wandering for {creature_name}.")

    # def add_to_inventory(self, item):
    #     self.inventory.append(item)
    #     print(f"{item.name} added to your inventory.")

    def add_to_inventory(self, item):
        if isinstance(item, Item):
            self.inventory.append(item)
            print(f"{item.name} added to your inventory.")
        elif isinstance(item, Equipment):
            self.inventory.append(item)
            print(f"{item.name} (Equipment) added to your inventory.")
        else:
            print("Error: Invalid item type")

    def remove_from_inventory(self, item_name):
        if item_name in self.inventory:
            del self.inventory[item_name]
            print(f"{item_name} removed from your inventory.")
        else:
            print(f"No item named '{item_name}' found in your inventory.")

    def display_inventory(self):
        if self.inventory:
            print("Your inventory:")
            for item_name in self.inventory:
                print(item_name.name)
        else:
            print("Your inventory is empty.")

    def pick_up_item(self, item_name):
        item_to_pick = None
        for item in self.current_room.objects:
            if item.name == item_name:
                item_to_pick = item
                break

        normalized_name = item_name.lower()
        for item in self.current_room.inventory:
            if item.name.lower() == normalized_name:
                item_to_pick = item
                break

        if item_to_pick in self.current_room.objects:
            self.inventory.append(item_to_pick)  # Add item_to_pick directly to self.inventory
            self.current_room.objects.remove(item_to_pick)
        elif item_to_pick in self.current_room.inventory:
            self.inventory.append(item_to_pick)  # Add item_to_pick directly to self.inventory
            self.current_room.inventory.remove(item_to_pick)
            print(f"You picked up {item_name}.")
        else:
            print(f"No item named '{item_name}' found in the room.")


    # TODO: Normalized names for dropping items
    def drop_item(self, item_name):
        # Check if item_name is in self.inventory
        item_to_drop = None
        for item in self.inventory:
            if item.name == item_name:
                item_to_drop = item
                break
        
        if item_to_drop:
            self.current_room.inventory.append(item_to_drop)
            print(f"Dropped {item_to_drop.name}.")
            self.inventory.remove(item_to_drop)
        else:
            print(f"No item named '{item_name}' found in your inventory.")

        
    def save_game(self, filename):
        save_game(self, filename)

    def load_game(self, filename):
        global game_rooms
        new_player, game_rooms = load_game(filename)
        self.name = new_player.name
        self.current_room = new_player.current_room
        self.inventory = new_player.inventory

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

    # TODO: Create add_equipment method for testing etc
    # sword = Equipment("Sword", "weapon", "wield", attack=10)
    # room1.add_equipment(sword)

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


def user_input_thread(player, quit_flag):
    custom_entrance = set(['enter', 'hut', 'out', 'leave'])
    while not quit_flag.is_set():
        try:
            user_input = prompt("Enter a command: look, create, remove, object_names, create_creature, move_creature, remove_creature, create_item, pick_up, drop, inventory, save, load, quit): ").lower().strip()
            # Check if the input is empty or contains only whitespace
            if not user_input.strip():
                print("Error, please try again. Available commands: look, create_object, create_item, remove, object_names, create_creature, move_creature, pick_up, create_item, drop, inventory, save, load, quit.")
                continue # Skip to the next iteration of the loop

            # Split user input into command and parameters
            parts = user_input.split()
            command = parts[0]
            parameters = parts[1:]

            if command == 'quit':
                quit_flag.set()
                break
            elif command == 'get':
                if parameters:
                    item_name = ' '.join(parameters)
                    player.pick_up_item(item_name)
                else:
                    print("Please specify an item to pick up.")            
            elif command in custom_entrance:
                player.move(command)
            elif command == 'n':               
                    direction = 'north'
                    player.move(direction)
            elif command == 'e':               
                    direction = 'east'
                    player.move(direction)
            elif command == 's':               
                    direction = 'south'
                    player.move(direction)
            elif command == 'w':               
                    direction = 'west'
                    player.move(direction)
            elif command == 'ne':               
                    direction = 'northeast'
                    player.move(direction)
            elif command == 'se':               
                    direction = 'southeast'
                    player.move(direction) 
            elif command == 'sw':               
                    direction = 'southwest'
                    player.move(direction)
            elif command == 'nw':               
                    direction = 'northwest'
                    player.move(direction)
            elif command == 'u':               
                    direction = 'up'
                    player.move(direction)
            elif command == 'd':               
                    direction = 'down'
                    player.move(direction)                                                   
            elif command == 'look':
                    print("\nAvailable directions:", player.current_room.available_directions())
                    print(f"You are in {player.current_room.name}.")
                    print(player.current_room.description)
                    player.look()
            elif command == 'create_object':
                object_name = prompt("Enter the name of the object to create: ")
                object_description = prompt("Enter a description for the object: ")
                player.create_object(object_name, object_description)
            elif command == 'create_item':
                item_name = prompt("Enter the name of the item to create: ")
                item_description = prompt("Enter a description for the item: ")
                player.create_item(item_name, item_description)                
            elif command == 'remove':
                object_name = prompt("Enter the name of the object to remove: ")
                player.remove_object(object_name)
            elif command == 'object_names':
                player.object_names()
            elif command == 'create_creature':
                move_interval = 10
                creature_name = prompt("Enter creature name: ")
                creature_description = prompt("Enter creature description: ")
                player.create_creature(creature_name, creature_description, move_interval)
            elif command == 'move_creature':
                creature_name = prompt("Enter creature name: ")
                player.enable_wandering(creature_name)
            elif command == 'stop_creature':
                creature_name = prompt("Enter creature name: ")
                player.disable_wandering(creature_name)
            elif command == 'remove_creature':
                creature_name = prompt("Enter the name of the creature to remove: ")
                player.remove_creature(creature_name)
            elif command == 'create_item':
                item_name = prompt("Item name:")
                item_description = prompt("Item description:")
                player.add_to_inventory(item_name, item_description)
            elif command == 'pick_up':
                item_name = prompt("Enter the name of the item to pick up: ")
                player.pick_up_item(item_name)
            # elif command == 'dirs':
            #     player.show_exits()
            elif command == 'drop':
                item_name = prompt("Enter the name of the item to drop: ")
                player.drop_item(item_name)
            elif command == 'inventory':
                player.display_inventory()
            elif user_input.lower() == 'save':
                filename = prompt("Enter the filename to save the game: ")
                player.save_game(filename)
            elif user_input.lower() == 'load':
                filename = prompt("Enter the filename to load the game: ")
                player.load_game(filename)
                print(f"Game loaded from '{filename}'.")
            # Handle unrecognized commands
            else:
                print(f"Unrecognized command: {command}.")
        except EOFError:
            break

def main():
    quit_flag = threading.Event()
    starting_room = create_game_world()
    player = Player("Hero", starting_room)

    ############## TEST START ##############
    # Create a room and a creature
    print(f"THERE IS SOMEKIND OF TEST GOING ON HERE")
    # Create a room and a creature
    room = Room("Hall", "You are in a grand hall with a doorway leading to north.")
    new_creature = room.create_creature("test creature", "test creature", 10)

    # Serialize the room
    serialized_room = room.serialize()
    print("Serialized Room:")
    print(json.dumps(serialized_room, indent=2))

    # Deserialize the room
    deserialized_room = Room.deserialize(serialized_room)
    print("Deserialized Room:")
    print(f"Room name: {deserialized_room.name}, description: {deserialized_room.description}")
    print("Creatures in the room:")
    for creature_name, creature in deserialized_room.creatures.items():
        print(f"Creature name: {creature.name}, description: {creature.description}")
    print(f"TESTING HAS CONCLUDED HERE")
    ############## TEST END ##############

    # Start the user input thread
    user_thread = threading.Thread(target=user_input_thread, args=(player, quit_flag))
    user_thread.start()

    try:
        while not quit_flag.is_set():
            # No need for a game loop here, just wait for user input
            time.sleep(1)  # Sleep briefly to avoid busy waiting
    except KeyboardInterrupt:
        quit_flag.set()
    finally:
        user_thread.join()
        print("Game over.")


if __name__ == "__main__":
    main()
