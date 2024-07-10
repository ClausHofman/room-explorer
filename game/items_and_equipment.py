class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

        def __str__(self):
            return f"{self.name}"

    
class GameObject:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class Equipment:
    def __init__(self, name, type, slot, attack=0, defense=0):
        self.name = name
        self.type = type  # Type of equipment: weapon, armor, accessory, etc.
        self.slot = slot
        self.attack = attack
        self.defense = defense

    def __str__(self):
        return f"{self.name} ({self.type}): Attack {self.attack}, Defense {self.defense}"