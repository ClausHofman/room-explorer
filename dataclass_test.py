from pprint import pprint
import inspect
import random
import string
from dataclasses import dataclass, field

def skill_level(skill):
    for i in range(11):
        if skill == i:
            return {'skill1': i*10, 'skill2': i*10, 'skill3': i*10, 'skill4': i*10, 'skill5': i*10}

@dataclass(frozen=False, slots=False, order=True)
class CreatureProperties:
    name: str
    description: str
    aggressive: bool = False # Default value
    skills: dict = field(default_factory=lambda:skill_level(0))
    _test: str = field(init=False, repr=False)
    _id_counter: int = 0

    def __post_init__(self) -> None:
        # Creature ID
        type(self)._id_counter += 1
        self.id = f"creature{type(self)._id_counter}"
        # Test
        self._test = f""
    
    @classmethod
    def get_counter(cls):
        return cls._id_counter

class Creature(CreatureProperties):
    def use_skill(self):
        skill = input('What skill do you want to use?')
        if str(skill) in self.skills:
            print(f"{self.name} starts concentrating on {skill}.")
        else:
            print("Unknown skill.")

    def show_info(self):
        print(f"ID: {self.id}")
        print(f"Name: {self.name}")
        print(f"Description: {self.description}")
        print(f"Aggressive: {self.aggressive}")
        print(f"Skills: {self.skills}")
        print(f"Search string: {self._test}")
    



def main():
    creature = Creature("Test Creature", "A featureless creature", False, skill_level(0))
    creature2 = Creature("Test Creature", "A featureless creature", False, skill_level(1))
    creature.show_info()
    creature2.show_info()
    print(creature2.get_counter())

    # creature.use_skill()
    # pprint(inspect.getmembers(Creature, inspect.isfunction))
    # pprint(inspect.getmembers(CreatureProperties, inspect.isfunction))

    # print(creature.__dict__)
    # print(creature2.__dict__)
    # print(creature.__dict__['skills'])

if __name__ == "__main__":
    main()