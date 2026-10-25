from components.ai import HostileEnemy
from components.fighter import fighter as Fighter
from components.inventory import inventory
import components.consumable as consumable
from entity import Actor, Item



player = Actor(char = "P", color = (255, 255, 255), name = "Player", ai_cls=HostileEnemy, fighter = Fighter(hp=30, defense=2, power=5), inventory=inventory(capacity=26))
orc = Actor(char = "O", color = (0, 255, 0), name = "Orc",ai_cls=HostileEnemy, fighter = Fighter(hp=10, defense=0, power=3), inventory=inventory(capacity=0))
goblin = Actor(char = "G", color = (0, 128, 0), name = "Goblin", ai_cls=HostileEnemy, fighter = Fighter(hp=16, defense=1, power=4), inventory=inventory(capacity=0))
potion = Item(char = "!", color = (255, 0, 0), name = "Healing Potion", consumable = consumable.HealingConsumable(amount=4))
fireball = Item(char = "/", color = (255, 165, 0), name = "Fireball Scroll", consumable = consumable.fireball_spell(damage=10, radius=3))
confusion_scroll = Item(char = "?", color = (0, 0, 255), name = "Confusion Scroll", consumable = consumable.ConfusionConsumable(number_of_turns = 10))
explosion_scroll = Item(char = "*", color = (255, 0, 255), name = "Explosion Scroll", consumable = consumable.explosionSpellConsumable(damage=12, radius=3))
