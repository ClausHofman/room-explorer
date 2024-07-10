from prompt_toolkit import prompt

def user_input_thread(player, quit_flag):
    custom_entrance = set(['enter', 'hut', 'out', 'leave'])
    while not quit_flag.is_set():
        try:
            user_input = prompt("Enter a command: direction, look(l), create_object, remove, object_names, create_creature, move_creature, remove_creature, create_item, pick_up, get, drop, inventory, save, load, quit): ").lower().strip()
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
            elif command == 'n' or command == 'north':               
                    direction = 'north'
                    player.move(direction)
            elif command == 'e' or command == 'east':               
                    direction = 'east'
                    player.move(direction)
            elif command == 's' or command == 'south':               
                    direction = 'south'
                    player.move(direction)
            elif command == 'w' or command == 'west':               
                    direction = 'west'
                    player.move(direction)
            elif command == 'ne' or command == 'northeast':               
                    direction = 'northeast'
                    player.move(direction)
            elif command == 'se' or command == 'southeast':               
                    direction = 'southeast'
                    player.move(direction) 
            elif command == 'sw' or command == 'southwest':               
                    direction = 'southwest'
                    player.move(direction)
            elif command == 'nw' or command == 'northwest':               
                    direction = 'northwest'
                    player.move(direction)
            elif command == 'u' or command == 'up':               
                    direction = 'up'
                    player.move(direction)
            elif command == 'd' or command == 'down':               
                    direction = 'down'
                    player.move(direction)                                                   
            elif command == 'look' or command == 'l':
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
            elif command == 'inventory' or command == 'i':
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