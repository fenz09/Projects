from components.ai import HostileEnemy
from components.fighter import fighter as Fighter
from components.consumable import HealingConsumable
from components.inventory import inventory
from entity import Actor, Item



player = Actor(char = "P", color = (255, 255, 255), name = "Player", ai_cls=HostileEnemy, fighter = Fighter(hp=30, defense=2, power=5), inventory=inventory(capacity=26))
orc = Actor(char = "O", color = (0, 255, 0), name = "Orc",ai_cls=HostileEnemy, fighter = Fighter(hp=10, defense=0, power=3), inventory=inventory(capacity=0))
goblin = Actor(char = "G", color = (0, 128, 0), name = "Goblin", ai_cls=HostileEnemy, fighter = Fighter(hp=16, defense=1, power=4), inventory=inventory(capacity=0))
potion = Item(char = "!", color = (255, 0, 0), name = "Healing Potion", consumable = HealingConsumable(amount=4))
