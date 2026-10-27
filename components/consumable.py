from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Tuple
import actions
import color
import components.ai
from components.base_components import BaseComponent
import components.inventory
from exceptions import Impossible
from input_handlers import ActionOrHandler, SingleRangedAttackHandler, AreaRangedAttackHandler
if TYPE_CHECKING:
    from entity import Actor, Item

class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[ActionOrHandler]:
        return actions.ItemAction(consumer, self.parent)
    def activate(self, action: actions.ItemAction) -> None:
        raise NotImplementedError(
        )
    def consume(self) -> None:
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)
class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount
    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP.", color.health_recovered)
            self.consume()
        else:
            raise Impossible("You are already at full health.")
class fireball_spell(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius
    def activate(self, action:actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        radius = self.radius + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < radius:
                    target = actor
                    radius = distance
            if target:
                self.engine.message_log.add_message(f"The fireball hits {target.name} for {self.damage} damage.", color.red)
                target.fighter.take_damage(self.damage)
                self.consume()
            else:
                raise Impossible("No target in range for the fireball.")

class ConfusionConsumable(Consumable):
    def __init__(self, turns: int):
        self.number_of_turns = turns

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message("Select a target for the confusion spell.", color.info)
        return SingleRangedAttackHandler(self.engine, callback= lambda xy: actions.ItemAction(consumer, self.parent, xy),)
        
    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor
        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area you cannot see.")
        if not target:
            raise Impossible("You must select a target for the confusion spell.")
        if target is consumer:
            raise Impossible("You cannot target yourself with the confusion spell.")
        self.engine.message_log.add_message(f"{target.name} is confused for {self.number_of_turns} turns.", color.status_effect)
        target.ai = components.ai.ConfusedEnemy(entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns)
        self.consume()

    def on_index_selected(self, xy: Tuple[int, int]) -> Optional[actions.Action]:
        target_x, target_y = xy
        if not self.parent.gamemap.visible[target_x, target_y]:
            raise Impossible("You cannot target an area you cannot see.")
        return actions.ItemAction(consumer=self.parent.gamemap.player, item=self.parent, xy=xy)

class explosionSpellConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius
    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message("Select a target for the explosion spell.", color.info)
        return AreaRangedAttackHandler(self.engine, radius=self.radius, callback=lambda xy: actions.ItemAction(consumer, self.parent, xy))
    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy
        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area you cannot see.")
        target_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(f"The explosion hits {actor.name} for {self.damage} damage.", color.red)
                actor.fighter.take_damage(self.damage)
                target_hit = True
        if not target_hit:
            raise Impossible("The explosion did not hit any target.")
        self.consume()