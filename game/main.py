from game.room import create_game_world
from game.items_and_equipment import Equipment
from game.player import Player
from game.input_handler import user_input_thread
import time
import threading
from prompt_toolkit import prompt

current_player_room = None
room_count = 0
game_rooms = []


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
