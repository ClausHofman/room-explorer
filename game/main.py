from room import create_game_world, current_player_room, room_count, game_rooms
from player import Player
from input_handler import user_input_thread
import time
import threading
from prompt_toolkit import prompt




def main():
    quit_flag = threading.Event()
    starting_room = create_game_world()
    player = Player("Hero", starting_room)


    # Start the user input thread
    user_thread = threading.Thread(target=user_input_thread, args=(player, quit_flag))
    user_thread.start()

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
