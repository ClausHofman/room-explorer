import pytest
import os
import json
from main_copy_2 import Room, Player, Creature, GameObject, create_game_world, serialize_rooms, serialize_creature
import pytest

def test_save_and_load_game(tmpdir):
    # Setup
    starting_room = create_game_world()
    player = Player("Hero", starting_room)
    player.create_object("Key", "A small rusty key.")
    player.current_room.add_to_inventory("Torch", "A wooden torch.")
    filename = tmpdir.join("test_save_load_game.json")

    # Test saving the game
    player.save_game(str(filename))
    assert filename.exists()

    # Modify game state
    player.pick_up_item("Torch")
    player.move("north")
    player.move("south")
    player.create_creature("Goblin", "A fierce goblin.", 5)

    # Test loading the game
    player.load_game(str(filename))

    # Extract the names of objects in the current room's inventory
    current_room_object_names = [obj.name for obj in player.current_room.objects]

    # Assertions to verify game state
    assert player.current_room.name == "Hall"  # Player should be back in the starting room
    assert "Torch" not in player.inventory  # Torch should be back in the room's inventory
    assert "Goblin" not in [creature.name for creature in player.current_room.creatures]  # Goblin should not exist
    assert "Key" in current_room_object_names, "Key should be in the starting room's objects."

def test_create_and_remove_objects():
    # Setup
    room = Room("Test Room", "A room for testing.")
    assert room.objects == []
    
    # Test creating an object
    room.create_object("Sword", "A sharp blade.")
    assert len(room.objects) == 1
    assert room.objects[0].name == "Sword"

    # Test removing an object
    room.remove_object("Sword")
    assert len(room.objects) == 0

def test_inventory_management():
    # Setup
    starting_room = create_game_world()
    player = Player("Hero", starting_room)

    # Test adding to inventory
    player.add_to_inventory("Map", "A map of the dungeon.")
    assert "Map" in player.inventory

    # Test removing from inventory
    player.remove_from_inventory("Map")
    assert "Map" not in player.inventory

def test_creature_management():
    # Setup
    starting_room = create_game_world()
    player = Player("Hero", starting_room)
    
    # Test creating a creature
    creature = player.create_creature("Dragon", "A mighty dragon.", 10)
    assert creature.name == "Dragon"
    assert creature.current_room == player.current_room

    # Test removing a creature
    player.remove_creature("Dragon")
    assert len(player.current_room.creatures) == 0

def test_serialize_creature():
    # Create a Room object
    room = Room("Cave", "A dark cave.")

    # Create a Creature object with known attributes
    creature = Creature("Dragon", "A mighty dragon.", "asdf")
    creature.current_room = room  # Assign the Room object to current_room
    creature.move_interval = 5
    creature.wandering = True

    # Serialize the creature
    serialized = serialize_creature(creature)

    # Assertions to verify the serialized output
    assert serialized['name'] == "Dragon"
    assert serialized['description'] == "A mighty dragon."
    assert serialized['current_room'] == "Cave"  # Now 'current_room' is expected to be a string 'Cave'
    assert serialized['move_interval'] == 5
    assert serialized['wandering'] == True  # Alternatively, you can use assert serialized['wandering'] is True

    # Optionally, you can assert that all expected keys are present
    expected_keys = ['name', 'description', 'current_room', 'move_interval', 'wandering']
    assert all(key in serialized for key in expected_keys)