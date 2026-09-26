from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class action:
    def preform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()

class action_with_direction(action):
    def __init__(self, dx: int, dy: int):
        super().__init__()
        self.dx = dx
        self.dy = dy
    def preform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()
class escape_action(action):
    def preform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit()
class movement_action(action_with_direction):
    def __init__(self, dx:int, dy:int):
        super().__init__(dx, dy)
    def preform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        if not engine.game_map.in_bounds(dest_x, dest_y):
            return
        if not engine.game_map.tiles["walkable"][dest_x][dest_y]:
            return
        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return
        entity.move(dx=self.dx, dy=self.dy)
class MeleeAction(action_with_direction):
    def preform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        target = engine.game_map.get_blocking_entity_at_location(dest_x, dest_y)
        if not target:
            return
        print(f"{entity.name} attacks {target.name}!")
class bump_action(action_with_direction):
    def preform(self, engine: Engine, entity: Entity) -> None:
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        if engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return
        movement_action(self.dx, self.dy).preform(engine, entity)
