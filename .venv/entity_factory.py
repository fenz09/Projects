from components.ai import HostileEnemy
from components.fighter import fighter as Fighter
from entity import Actor 



player = Actor(char = "P", color = (255, 255, 255), name = "Player", ai_cls=HostileEnemy, fighter = Fighter(hp=30, defense=2, power=5))
orc = Actor(char = "O", color = (0, 255, 0), name = "Orc",ai_cls=HostileEnemy, fighter = Fighter(hp=10, defense=0, power=3))
goblin = Actor(char = "G", color = (0, 128, 0), name = "Goblin", ai_cls=HostileEnemy, fighter = Fighter(hp=16, defense=1, power=4))

