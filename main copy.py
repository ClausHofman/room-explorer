import time
import random
import threading
from prompt_toolkit import prompt
import json


game_rooms = []
current_player_room = None  # Initialize the global variable

# Function to update the current player's room
def update_current_player_room(new_room):
    global current_player_room
    current_player_room = new_room

def save_game(player, filename):
    if not filename.endswith('.json'):
        filename += '.json'

    backup_filename = filename + '.bak'

    global game_rooms

    serialized_rooms = serialize_rooms(game_rooms)

    player_state = {
        'player': {
            'name': player.name,
            'current_room': player.current_room.name,
            'inventory': player.inventory if player.inventory else {}  # Serialize empty inventory as {}
        }
    }

    # Serialize all creatures in all rooms
    all_creatures_state = []
    for room in game_rooms:
        for creature in room.creatures:
            all_creatures_state.append(serialize_creature(creature))

    game_state = {
        'player': player_state,
        'rooms': serialized_rooms
    }

    # Attempt to save to the backup file first
    try:
        with open(backup_filename, 'w') as backup_file:
            json.dump(game_state, backup_file, indent=4)
        print(f"Game state saved to backup file '{backup_filename}'.")
    except Exception as e:
        print(f"Error occurred while saving to backup file '{backup_filename}': {e}")
        return False

    try:
        with open(filename, 'w') as f:
            json.dump(game_state, f, indent=4)
        print(f"Game state saved to '{filename}'.")
        return True
    except Exception as e:
        print(f"Error occurred while saving to main file '{filename}': {e}")
        return False

def load_game(filename):
    global game_rooms

    if not filename.endswith('.json'):
        filename += '.json'

    with open(filename, 'r') as f:
        game_state = json.load(f)

    # Create a dictionary to hold the rooms by name
    room_dict = {}

    # First pass: Create all rooms and add them to the dictionary
    for room_data in game_state.get('rooms', []):
        room = Room(room_data['name'], room_data['description'])
        room.objects = [GameObject(obj['name'], obj['description']) for obj in room_data.get('objects', [])]
        room.inventory = room_data.get('inventory', {})
        room.creatures = []  # Initialize creatures list
        room_dict[room.name] = room

    # Second pass: Set the exits for each room using the room dictionary
    for room_data in game_state.get('rooms', []):
        room = room_dict[room_data['name']]
        room.exits = {direction: room_dict[room_name] for direction, room_name in room_data['exits'].items()}
    
    # Load creatures into rooms
    for room_data in game_state.get('rooms', []):
        room = room_dict[room_data['name']]
        for creature_data in room_data.get('creatures', []):
            current_room_name = creature_data.get('current_room')
            current_room = room_dict.get(current_room_name, None)
            creature = Creature(creature_data['name'], creature_data['description'], current_room, creature_data['move_interval'])
            creature.wandering = creature_data.get('wandering', False)  # Set wandering state from saved data

            if creature.wandering:
                creature.start_wandering()

            room.creatures.append(creature)

    # Load player
    player_data = game_state.get('player', {}).get('player', {})
    current_room_name = player_data.get('current_room')
    current_room = room_dict.get(current_room_name, None)
    player = Player(player_data['name'], current_room)
    player.inventory = player_data.get('inventory', {})

    # Update global game_rooms with loaded rooms
    game_rooms = list(room_dict.values())

    return player, game_rooms


def serialize_rooms(rooms):
    serialized_rooms = []
    for room in rooms:
        # Serialize exits to contain only the names of the neighboring rooms
        exits = {direction: neighbor.name for direction, neighbor in room.exits.items()}
        serialized_room = {
            'name': room.name,
            'description': room.description,
            'exits': exits,
            'objects': [obj.__dict__ for obj in room.objects],
            'creatures': [serialize_creature(creature) for creature in room.creatures],
            'inventory': room.inventory if room.inventory else {}  # Ensure empty inventory is {}
        }
        serialized_rooms.append(serialized_room)
    return serialized_rooms

def serialize_creature(creature):
    serialized_creature = {
        'name': creature.name,
        'description': creature.description,
        'current_room': creature.current_room.name,  # Serialize room name
        'move_interval': creature.move_interval,
        'wandering': creature.wandering
        # Add more attributes as needed
    }
    return serialized_creature

def deserialize_rooms(serialized_rooms):
    rooms = {}
    for serialized_room in serialized_rooms:
        room = Room(serialized_room['name'], serialized_room['description'])
        room.objects = [GameObject(obj['name'], obj['description']) for obj in serialized_room['objects']]
        room.creatures = [Creature(creature['name'], creature['description'], room) for creature in serialized_room['creatures']]
        room.inventory = serialized_room['inventory']
        rooms[room.name] = room

    for serialized_room in serialized_rooms:
        room = rooms[serialized_room['name']]
        # room.exits = serialized_room['exits']
        room.exits = {direction: rooms[neighbor_room_name] for direction, neighbor_room_name in serialized_room['exits'].items()}

    return rooms

class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.objects = []
        self.creatures = []
        self.inventory = {}

    def connect(self, direction, neighbor_room):
        self.exits[direction] = neighbor_room

    def available_directions(self):
        # print(list(self.exits.keys()))
        return list(self.exits.keys())

    def create_object(self, object_name, object_description):
        new_object = GameObject(object_name, object_description)
        self.objects.append(new_object)
        print(f"{new_object.name} created in {self.name}.")
    

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

    def add_to_inventory(self, item_name, description):
        self.inventory[item_name] = description
        print(f"{item_name} added to {self.name} inventory.")

    def remove_from_inventory(self, item_name):
        if item_name in self.inventory:
            del self.inventory[item_name]
            print(f"{item_name} removed from {self.name} inventory.")
        else:
            print(f"No item named '{item_name}' found in {self.name} inventory.")

    def display_inventory(self):
        if self.inventory:
            print(f"Inventory of {self.name}:")
            for item_name, description in self.inventory.items():
                print(f"{item_name}: {description}")
        else:
            print(f"{self.name} has no items in inventory.")

    def object_descriptions(self):
        if self.objects:
            for obj in self.objects:
                print(f"{obj.description}")
        if self.creatures:
            for creature in self.creatures:
                print(f"{creature.description}")
        # else:
        #     print(f"\nNo objects in {self.name}.")

    def display_object_names(self):
        if self.objects:
            for obj in self.objects:
                print(f"{obj.name}")
        if self.creatures:
            for creature in self.creatures:
                print(f"{creature.name}")

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


class Player:
    def __init__(self, name, current_room):
        self.name = name
        self.current_room = current_room
        self.inventory = {}

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

    def add_to_inventory(self, item_name, description):
        self.inventory[item_name] = description
        print(f"{item_name} added to your inventory.")

    def remove_from_inventory(self, item_name):
        if item_name in self.inventory:
            del self.inventory[item_name]
            print(f"{item_name} removed from your inventory.")
        else:
            print(f"No item named '{item_name}' found in your inventory.")

    def display_inventory(self):
        if self.inventory:
            print("Your inventory:")
            for item_name, description in self.inventory.items():
                print(f"{item_name}: {description}")
        else:
            print("Your inventory is empty.")

    def pick_up_item(self, item_name):
        if item_name in self.current_room.inventory:
            self.add_to_inventory(item_name, self.current_room.inventory[item_name])
            self.current_room.remove_from_inventory(item_name)
        else:
            print(f"No item named '{item_name}' found in the room.")

    def drop_item(self, item_name):
        if item_name in self.inventory:
            self.current_room.add_to_inventory(item_name, self.inventory[item_name])
            self.remove_from_inventory(item_name)
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

    # Connect rooms
    room1.connect('north', room2)
    room2.connect('south', room1)
    room2.connect('east', room3)
    room3.connect('west', room2)

    global game_rooms
    game_rooms = [room1, room2, room3]

    return room1  # Starting room


def user_input_thread(player, quit_flag):
    custom_entrance = set(['enter', 'hut', 'out', 'leave'])
    while not quit_flag.is_set():
        try:
            user_input = prompt("Enter a command n, e, s, w, look, create, remove, object_names, create_creature, move_creature, remove_creature, create_item, pick_up, drop, inventory, save, load, quit): ")
            # Check if the input is empty or contains only whitespace
            if not user_input.strip():
                print("Error, please try again. Available commands: n, e, s, w, look, create, remove, object_names, create_creature, move_creature, pick_up, create_item, drop, inventory, save, load, quit.")
                continue # Skip to the next iteration of the loop

            command, *args = user_input.lower().split()
            if user_input.lower() == 'quit':
                quit_flag.set()
                break
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
            elif command == 'look':
                    print("\nAvailable directions:", player.current_room.available_directions())
                    print(f"You are in {player.current_room.name}.")
                    print(player.current_room.description)
                    player.look()
            elif command == 'create':
                object_name = prompt("Enter the name of the object to create: ")
                object_description = prompt("Enter a description for the object: ")
                player.create_object(object_name, object_description)
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
            else:
                print("Invalid command. Try again.")
        except EOFError:
            break



def main():
    quit_flag = threading.Event()
    starting_room = create_game_world()
    player = Player("Hero", starting_room)

    # Start the user input thread
    user_thread = threading.Thread(target=user_input_thread, args=(player, quit_flag))
    user_thread.start()

    # creature1 = Creature("Goblin", starting_room)
    # creature1.start_wandering()

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