from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Entity
    from engine import Engine
    from game_map import Gamemap

class baseComponent:
    parent: Entity

    def __init__(self, parent: Entity) -> None:
        self.parent = parent

    @property
    def gamemap(self) -> Gamemap:
        return self.parent.gamemap

    @property
    def engine(self) -> Engine:
        return self.gamemap.engine