from __future__ import annotations

import random
from typing import TYPE_CHECKING, Dict, Iterator, List, Tuple

import tcod
import tile_types
import entity_factory
from game_map import Gamemap

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

max_items_by_floor = [
    (1, 1),
    (4, 2),
]
max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5),
]
item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factory.potion, 35)],
    2: [(entity_factory.confusion_scroll, 10)],
    4: [(entity_factory.fireball, 25), (entity_factory.sword, 5)],
    6: [(entity_factory.explosion_scroll, 25), (entity_factory.chainmail_armor, 15)]
}
enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factory.orc, 80)],
    3: [(entity_factory.goblin, 15)],
    5: [(entity_factory.goblin, 30)],
    7: [(entity_factory.goblin, 60)],

}
def get_max_value_for_floor(
        max_value_by_floor: List[Tuple[int, int]],
        floor: int
) -> int:
    current_value = 0
    for floor_minimum, value in sorted(max_value_by_floor):
        if floor_minimum > floor:
            break
        current_value = value
    return current_value

def get_entities_at_random(
        weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
        number_of_entites: int,
        floor: int,

) -> List[Entity]:
    if number_of_entites <= 0:
        return []

    entity_weighted_chances: Dict[Entity, int] = {}
    for key, values in sorted(weighted_chances_by_floor.items()):
        if key > floor:
            break
        for entity, weighted_chance in values:
            entity_weighted_chances[entity] = weighted_chance

    if not entity_weighted_chances:
        return []

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())
    return random.choices(
        entities,
        weights=entity_weighted_chance_values,
        k=number_of_entites,
    )

class RectangualrRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: "RectangualrRoom") -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def place_entities(room: RectangualrRoom, dungeon: Gamemap, floor_number: int) -> None:
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )
    monsters: List[Entity] = get_entities_at_random(enemy_chances, number_of_monsters, floor_number)
    items: List[Entity] = get_entities_at_random(item_chances, number_of_items, floor_number)

    available_positions = [
        (x, y)
        for x in range(room.x1 + 1, room.x2)
        for y in range(room.y1 + 1, room.y2)
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities)
    ]
    for entity in monsters + items:
        if not available_positions:
            break
        position = available_positions.pop(random.randrange(len(available_positions)))
        entity.spawn(dungeon, *position)


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
) -> Gamemap:
    player = engine.player
    dungeon = Gamemap(
        engine=engine,
        width=map_width,
        height=map_height,
        entities=[player],
    )
    rooms: List[RectangualrRoom] = []

    for _ in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)
        x = random.randint(0, map_width - room_width - 1)
        y = random.randint(0, map_height - room_height - 1)
        new_room = RectangualrRoom(x, y, room_width, room_height)
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue
        dungeon.tiles[new_room.inner] = tile_types.Floor
        if len(rooms) == 0:
            if player is not None:
                player.place(*new_room.center, gamemap=dungeon)
        else:
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.Floor
        place_entities(new_room, dungeon, engine.game_world.current_floor)

        rooms.append(new_room)

    if not rooms:
        raise RuntimeError("Dungeon generation did not produce any rooms.")

    dungeon.downstairs_location = rooms[-1].center
    dungeon.tiles[dungeon.downstairs_location] = tile_types.down_stairs

    return dungeon


def tunnel_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:
        corner_x = x2
        corner_y = y1
    else:
        corner_x = x1
        corner_y = y2

    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y