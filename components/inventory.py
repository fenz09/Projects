from __future__ import annotations
from typing import List, TYPE_CHECKING
from components.base_components import BaseComponent
if TYPE_CHECKING:
    from entity import Actor, Item

class inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []
    def drop(self, item: Item) -> None:
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.parent.gamemap)
        self.engine.message_log.add_message(f"{self.parent.name} dropped {item.name}.")
        