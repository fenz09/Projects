from typing import Set, Iterable, Any
from tcod.context import Context
from tcod.console import Console
from game_map import Gamemap
from tcod.map import compute_fov
from typing import Iterable, Any
from entity import Entity
from actions import escape_action, movement_action
from input_handlers import EventHandler

class Engine:
    def __init__(self, event_handler: EventHandler, game_map: Gamemap, player: Entity) -> None: 
        self.event_handler = event_handler
        self.player = player
        self.game_map = game_map
        self.update_fov()

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)
            if action is None:
                continue
            action.preform(self, self.player)
            self.update_fov()
            self.handle_enemy_turns()
    def update_fov(self) -> None:
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        self.game_map.explored |= self.game_map.visible

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)
        context.present(console)
        console.clear()
    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:
            print(f"{entity.name} takes its turn.")


