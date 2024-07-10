from game.items_and_equipment import Item, Equipment
from game.serialization import save_game, load_game
from game.room import update_current_player_room

class Player:
    def __init__(self, name, current_room):
        self.name = name
        self.current_room = current_room
        self.inventory = []
        self.equipment = {}

    # EQUIPMENT_SLOTS = ['torso', 'wield']

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