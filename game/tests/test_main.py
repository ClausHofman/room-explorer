from game.main import save_game, load_game, create_game_world, serialize_creature, serialize_rooms, Room, Player, GameObject, Item, Equipment
import json
import pytest

def test_create_equipment_for_player():
    starting_room = create_game_world()
    player = Player("Hero", starting_room)
    player.create_equipment("Shield", "Armor", "Hand", attack=0, defense=5)

    assert len(player.inventory) == 1
    assert player.inventory[0].name == "Shield"
    assert player.inventory[0].type == "Armor"
    assert player.inventory[0].slot == "Hand"
    assert player.inventory[0].attack == 0
    assert player.inventory[0].defense == 5

def test_create_equipment_in_room():
    room = Room("Test Room", "A room for testing.")
    room.create_equipment("Sword", "Weapon", "Wield", attack=10, defense=0)

    assert len(room.inventory) == 1
    assert room.inventory[0].name == "Sword"
    assert room.inventory[0].type == "Weapon"
    assert room.inventory[0].slot == "Wield"
    assert room.inventory[0].attack == 10
    assert room.inventory[0].defense == 0

def test_equipment_attributes():
    equipment = Equipment("Armor", "Armor", "Torso", attack=0, defense=15)

    assert equipment.name == "Armor"
    assert equipment.type == "Armor"
    assert equipment.slot == "Torso"
    assert equipment.attack == 0
    assert equipment.defense == 15

def test_save_game():
    starting_room = create_game_world()
    player = Player("Hero", starting_room)
    player.create_object("Key", "A small rusty key.")
    filename = "test_save_game.json"

    player.save_game(filename)
    with open(filename, "r") as f:
        data = json.load(f)

    assert data["player"]["name"] == "Hero"
    assert data["player"]["current_room"] == "Hall"
    assert data["player"]["inventory"] == ["Key"]
    assert data["rooms"] == serialize_rooms(starting_room)