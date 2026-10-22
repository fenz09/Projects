from __future__ import annotations
import copy
from typing import Optional,Tuple, TypeVar, TYPE_CHECKING
from render_order import renderOrder
if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
    from game_map import Gamemap


T = TypeVar("T", bound="Entity")

class Entity:
    parent: Gamemap
    def __init__(
        self,
        parent: Optional[Gamemap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<unnamed>",
        blocks_movement: bool = False,
        render_order: renderOrder = renderOrder.actor,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> Gamemap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: Gamemap, x: int, y: int) -> T:
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone
    def move(self, dx: int, dy:int) -> None:
        self.x +=dx
        self.y += dy
    def place(self, x:int, y:int, gamemap: Optional[Gamemap] = None) -> None:
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)
class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<unnamed>",
        ai_cls: Type[BaseAI],
        fighter: Fighter,
    ):
        super().__init__(x= x, y= y, char= char, color= color, name= name, blocks_movement= True)
        self.ai = ai_cls(self)
        self.fighter = fighter
        self.fighter.parent = self
        self.render_order = renderOrder.actor

    @property
    def is_alive(self) -> bool:
        return bool(self.ai)

