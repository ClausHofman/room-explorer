import pytest
from game.main_copy import Room, Player, Equipment  # Adjust import as necessary

# Test Equipment creation and addition to Room
def test_create_equipment_in_room():
    room = Room("Test Room", "A room for testing.")
    room.create_equipment("Sword", "Weapon", "Wield", attack=10, defense=0)

    assert len(room.inventory) == 1
    assert room.inventory[0].name == "Sword"
    assert room.inventory[0].type == "Weapon"
    assert room.inventory[0].slot == "Wield"
    assert room.inventory[0].attack == 10
    assert room.inventory[0].defense == 0

# Test Equipment creation and addition to Player
def test_create_equipment_for_player():
    room1 = Room("Test Room 1", "A room for testing.")

    player = Player("Test Player", room1)
    player.create_equipment("Shield", "Armor", "Hand", attack=0, defense=5)

    assert len(player.inventory) == 1
    assert player.inventory[0].name == "Shield"
    assert player.inventory[0].type == "Armor"
    assert player.inventory[0].slot == "Hand"
    assert player.inventory[0].attack == 0
    assert player.inventory[0].defense == 5

# Ensure Equipment attributes are correct
def test_equipment_attributes():
    equipment = Equipment("Armor", "Armor", "Torso", attack=0, defense=15)

    assert equipment.name == "Armor"
    assert equipment.type == "Armor"
    assert equipment.slot == "Torso"
    assert equipment.attack == 0
    assert equipment.defense == 15
