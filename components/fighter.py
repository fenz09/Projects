from __future__ import annotations
import re
from turtle import color
from typing import TYPE_CHECKING
from components.base_components import baseComponent
from render_order import renderOrder
if TYPE_CHECKING:
    from entity import Actor

class fighter(baseComponent):
    parent: Actor
    def __init__(self, hp: int, defense:int, power:int):
        self.max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power

    @property 
    def hp(self) -> int:
        return self._hp
    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent:
            self.die()
    def die(self) -> None:
        if self.engine.player is self.parent:
            death_messege = 'you died!'
            death_messege_color = color.player_die
        else:
            death_messege = f"{self.parent.name} is dead."
            death_messege_color = color.enemy_die

        self.parent.char = 'X'  # Mark the entity as dead with an 'X' character
        self.parent.color = (255, 0, 0)  # Change the entity's color to red to indicate death
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f'{self.parent.name} (dead)'
        self.parent.render_order = renderOrder.corpse

        self.engine.message_log.add_message(death_messege, death_messege_color)
        self.engine.player.level.add_xp(self.parent.level.xp_given)
    def heal(self, amount: int ) -> int:
        if self.hp == self.max_hp:
            return 0
        new_hp = self.hp + amount
        if new_hp > self.max_hp:
            new_hp = self.max_hp
        healed_amount = new_hp - self.hp
        self.hp = new_hp
        return healed_amount
    def take_damage(self, amount: int) -> None:
        self.hp -= amount



    
