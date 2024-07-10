import pytest
import os
import json
from game.main import Room, Player, Creature, GameObject, save_game, load_game, create_game_world, serialize_rooms, serialize_creature

def test_save_and_load_game(tmpdir):
    # Setup
    starting_room = create_game_world()
    player = Player("Hero", starting_room)
    player.create_object("Key", "A small rusty key.")
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

def test_movement():
    # Setup
    starting_room = create_game_world()
    player = Player("Hero", starting_room)

    # Initial room should be Hall
    assert player.current_room.name == "Hall"

    # Move to another room
    player.move("north")
    assert player.current_room.name == "Kitchen"

    # Move back to Hall
    player.move("south")
    assert player.current_room.name == "Hall"

def test_pick_up_and_drop_items():
    # Setup
    starting_room = create_game_world()
    player = Player("Hero", starting_room)
    player.create_object("Key", "A small rusty key.")

def test_interaction_with_non_existent_objects():
    # Setup
    starting_room = create_game_world()
    player = Player("Hero", starting_room)

    # Attempt to pick up a non-existent item and check the message
    initial_inventory = player.inventory.copy()
    player.pick_up_item("NonExistentItem")
    assert player.inventory == initial_inventory  # Inventory should remain unchanged

    # Attempt to drop a non-existent item and check the message
    player.drop_item("NonExistentItem")
    assert player.inventory == initial_inventory  # Inventory should remain unchanged

def test_interaction_with_non_existent_creatures():
    # Setup
    starting_room = create_game_world()
    player = Player("Hero", starting_room)

    # Attempt to remove a non-existent creature and check the message
    initial_creatures = player.current_room.creatures.copy()
    player.remove_creature("NonExistentCreature")
    assert player.current_room.creatures == initial_creatures  # Creatures should remain unchanged
