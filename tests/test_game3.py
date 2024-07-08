from main_copy_2 import create_game_world, Player, Room
def test_save_and_load_complex_state(tmpdir):
    starting_room = create_game_world()
    player = Player("Hero", starting_room)
    player.create_object("Key", "A small rusty key.")
    player.current_room.add_to_inventory("Torch", "A wooden torch.")
    player.create_creature("Goblin", "A fierce goblin.", 5)
    filename = tmpdir.join("test_save_load_complex_state.json")

    # Save the game
    player.save_game(str(filename))
    assert filename.exists()

    # Modify the game state
    player.pick_up_item("Torch")
    player.move("north")
    player.create_object("Shield", "A sturdy shield.")
    player.create_creature("Orc", "A dangerous orc.", 8)

    # Load the game
    player.load_game(str(filename))

    # Extract the names of objects and creatures in the current room
    current_room_object_names = [obj.name for obj in player.current_room.objects]
    current_room_creature_names = [creature.name for creature in player.current_room.creatures]

    # Assertions to verify game state
    assert player.current_room.name == "Hall"  # Player should be back in the starting room
    assert "Torch" not in player.inventory  # Torch should be back in the room's inventory
    assert "Goblin" in current_room_creature_names  # Goblin should be in the room
    assert "Shield" not in current_room_object_names  # Shield should not exist
    assert "Orc" not in current_room_creature_names  # Orc should not exist

import pytest
from main_copy_2 import Creature, serialize_creature

@pytest.fixture
def setup_creature_and_room():
    # Create a Room object
    cave = Room("Cave", "A dark cave.")

    # Create a Creature object
    dragon = Creature("Dragon", "A mighty dragon.", "Cave", 5)
    dragon.current_room = cave  # Assign the Room object to current_room

    return dragon

def test_serialize_creature(setup_creature_and_room):
    creature = setup_creature_and_room

    # Serialize the creature
    serialized = serialize_creature(creature)

    # Assertions to verify the serialized output
    assert serialized['name'] == "Dragon"
    assert serialized['description'] == "A mighty dragon."
    assert serialized['current_room'] == "Cave"  # Assuming serialize_creature returns room.name as string
    assert serialized['move_interval'] == 5
    assert serialized['wandering'] is False  # Alternatively, use assert serialized['wandering'] == False

    # Optionally, you can assert that all expected keys are present
    expected_keys = ['name', 'description', 'current_room', 'move_interval', 'wandering']
    assert all(key in serialized for key in expected_keys)
