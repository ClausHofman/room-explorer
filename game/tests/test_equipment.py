import pytest
from main_copy_2 import Player, Equipment

@pytest.fixture
def setup_player():
    # You can create a setup function for Player with a mock current_room
    return Player("Hero", current_room=None)

@pytest.fixture
def setup_equipment():
    # You can create a setup function for Equipment
    return Equipment("Sword", "weapon", "wield", attack=10)

def test_equip_item(setup_player, setup_equipment):
    player = setup_player
    sword = setup_equipment

    # Equip an item
    player.equip_item(sword)

    # Assert the item is in the equipment dictionary
    assert 'wield' in player.equipment
    assert player.equipment['wield'] == sword
    assert sword not in player.inventory

def test_unequip_item(setup_player, setup_equipment):
    player = setup_player
    sword = setup_equipment

    # Equip an item first
    player.equip_item(sword)

    # Unequip the item
    player.unequip_item('wield')

    # Assert the item is back in the inventory
    assert 'wield' not in player.equipment
    assert sword in player.inventory

def test_list_equipment(capsys, setup_player, setup_equipment):
    player = setup_player
    sword = setup_equipment

    player.equip_item(sword)
    player.equip_item(sword)
    player.list_equipment()

    captured = capsys.readouterr()
    captured_output = captured.out.strip()

    expected_output = "You wield Sword.\nYou are already wielding Sword.\nCurrently equipped items:\n- wield: Sword (weapon): Attack 10, Defense 0"
    assert captured_output == expected_output