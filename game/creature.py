import threading
import random

class Creature:
    def __init__(self, name, description, current_room, move_interval=10):
        self.name = name
        self.description = description
        self.current_room = current_room
        self.move_interval = move_interval
        self.thread = None
        self.quit_flag = threading.Event()
        self.condition = threading.Condition()
        self.wandering = False  # Initialize wandering state to False

    def start_wandering(self):
        self.wandering = True
        if self.thread is None:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def move_randomly(self):
        global current_player_room

        while not self.quit_flag.is_set():
            available_directions = self.current_room.available_directions()
            if available_directions:
                # TODO: Available directions should be based on actual available exits
                direction = random.choice(available_directions)
                next_room = self.current_room.exits[direction]

                if self.current_room == current_player_room:
                    print(f"{self.name} leaves to the {direction}.")
                self.change_room(next_room)

                # Check if the creature is moving into the player's current room
                if next_room == current_player_room:
                    print(f"{self.name} arrives from the {direction}.")
                
            with self.condition:
                if not self.quit_flag.is_set():
                    self.condition.wait(self.move_interval)

    def run(self):
        self.move_randomly()

    def stop_wandering(self):
        self.wandering = False
        if self.thread is not None:
            with self.condition:
                self.quit_flag.set()
                self.condition.notify_all()
            self.thread.join()

    def change_room(self, new_room):
        # Remove creature from the current room
        self.current_room.creatures.remove(self)
        # Update the current room to the new room
        self.current_room = new_room
        # Add creature to the new room
        new_room.creatures.append(self)




# Dataclass
# from pprint import pprint
# import inspect
# import random
# import string
# from dataclasses import dataclass, field

# def skill_level(skill):
#     for i in range(11):
#         if skill == i:
#             return {'skill1': i*10, 'skill2': i*10, 'skill3': i*10, 'skill4': i*10, 'skill5': i*10}

# @dataclass(frozen=False, slots=False, order=True)
# class CreatureProperties:
#     name: str
#     description: str
#     aggressive: bool = False # Default value
#     skills: dict = field(default_factory=lambda:skill_level(0))
#     _test: str = field(init=False, repr=False)
#     _id_counter: int = 0

#     def __post_init__(self) -> None:
#         # Creature ID
#         type(self)._id_counter += 1
#         self.id = f"creature{type(self)._id_counter}"
#         # Test
#         self._test = f""
    
#     @classmethod
#     def get_counter(cls):
#         return cls._id_counter

# class Creature(CreatureProperties):
#     def use_skill(self):
#         skill = input('What skill do you want to use?')
#         if str(skill) in self.skills:
#             print(f"{self.name} starts concentrating on {skill}.")
#         else:
#             print("Unknown skill.")

#     def show_info(self):
#         print(f"ID: {self.id}")
#         print(f"Name: {self.name}")
#         print(f"Description: {self.description}")
#         print(f"Aggressive: {self.aggressive}")
#         print(f"Skills: {self.skills}")
#         print(f"Search string: {self._test}")
    

# def main():
#     creature = Creature("Test Creature", "A featureless creature", False, skill_level(0))
#     creature2 = Creature("Test Creature", "A featureless creature", False, skill_level(1))
#     creature.show_info()
#     creature2.show_info()
#     print(creature2.get_counter())

#     # creature.use_skill()
#     # pprint(inspect.getmembers(Creature, inspect.isfunction))
#     # pprint(inspect.getmembers(CreatureProperties, inspect.isfunction))

#     # print(creature.__dict__)
#     # print(creature2.__dict__)
#     # print(creature.__dict__['skills'])

# if __name__ == "__main__":
#     main()