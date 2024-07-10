from room import Room  # Local import to avoid circular dependency
from player import Player  # Local import to avoid circular dependency
from creature import Creature
from items_and_equipment import Item, GameObject
from room import current_player_room, room_count, game_rooms
import json

def save_game(player, filename):
    
    filename = str(filename)

    if not filename.endswith('.json'):
        filename += '.json'

    backup_filename = filename + '.bak'

    global game_rooms, room_count

    serialized_rooms = serialize_rooms(game_rooms)

    player_state = {
            'name': player.name,
            'current_room': player.current_room.name,
            'inventory': player.inventory if player.inventory else {}  # Serialize empty inventory as {}
    }

    game_state = {
        'player': player_state,
        'rooms': serialized_rooms,
        'room_count': room_count
    }

    # TODO: Update saving and loading to handle equipment

    # print(f"Printing game state: {game_state}")
    # print(f"Printing game rooms: {serialized_rooms}")

    # print(f"Serialized Rooms: {json.dumps(serialized_rooms, indent=2)}")
    # print(f"Player State: {json.dumps(player_state, indent=2)}")
    # print(f"Room Count: {room_count}")

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
    
    filename = str(filename)

    global game_rooms, room_count

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
        print(f"Room created: {room.name}")

    # Get all valid directions from the Room class
    valid_directions = Room.available_directions()

    # Second pass: Set the exits for each room using the room dictionary
    for room_data in game_state.get('rooms', []):
        room = room_dict[room_data['name']]
        exits = room_data.get('exits', {})
    
        # Update exits based on current game's exit directions
        for direction, room_name in exits.items():
            if direction in valid_directions:
                if room_name in room_dict:
                    neighbor_room = room_dict[room_name]
                    room.connect(direction, neighbor_room)
                else:
                    print(f"Warning: Neighbor room '{room_name}' not found for direction '{direction}' in room '{room.name}'.")
            else:
                print(f"Warning: Direction '{direction}' not recognized in room '{room.name}'.")


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
    player_data = game_state.get('player', {})
    current_room_name = player_data.get('current_room')
    current_room = room_dict.get(current_room_name, None)
    if current_room is None:
        print(f"Error: Current room '{current_room_name}' for player not found.")
        print(f"Room dictionary keys: {list(room_dict.keys())}")        
    player = Player(player_data['name'], current_room)
    player.inventory = player_data.get('inventory', {})

    # Load room count
    room_count = game_state.get('room_count', 0)

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
    print(f"Printing serialized creature {serialized_creature}")
    return serialized_creature
