from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import tcod.event
from actions import (
    Action,
    BumpAction,
    WaitAction,
    pickupAction,
    DropItem
    
)
import color
import actions
import exceptions
MoveKeys = {
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    tcod.event.K_W: (0, -1),
    tcod.event.K_S: (0, 1),
    tcod.event.K_D: (1, 0),
    tcod.event.K_A: (-1, 0),
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

WaitKeys = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_6,
    tcod.event.K_CLEAR,
}

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

class EventHandler(tcod.event.EventDispatch[action]):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> None:
        self.handle_action(self.dispatch(event))

    def handle_action(self, action: Optional[Action]) -> None:
        if action is None:
            return
        try:
            action.perform()
        except exceptions.Impossible as e:
            self.engine.message_log.add_message(e.args[0], color.impossible)
            return False

        self.engine.handle_enemy_turns()
        self.engine.update_fov()
        return True
        
    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = (event.tile_x, event.tile_y)

    def ev_quit(self, event: tcod.event.Quit) -> Optional[action]:
        raise SystemExit()
    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)
    
class MainGameEventHandler(EventHandler):

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[action]:
        action: Optional[action] = None
        key = event.sym
        player = self.engine.player

        if key in MoveKeys:
            dx, dy = MoveKeys[key]
            action = BumpAction(player, dx=dx, dy=dy)
        elif key in WaitKeys:
            action = WaitAction(player)
        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        elif key == tcod.event.K_v:
            self.engine.event_handler = HistoryViewer(self.engine)
        elif key == tcod.event.K_g:
            action = pickupAction(player)
        elif key == tcod.event.K_i:
            self.engine


        return action
class GameOverEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()
CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}
class HistoryViewer(EventHandler):
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        log_console = tcod.Console(console.width - 6, console.height - 6)
        log_console.draw_frame(0, 0, log_console.width, log_console.height,)
        log_console.print_box(0, 0, log_console.width, 1, "<History Viewer>", alignment = tcod.CENTER)

        self.engine.message_log.render_messages(log_console, 1, 1, log_console.width - 2, log_console.height - 2, self.engine.message_log.messages [: self.cursor + 1],)
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                self.cursor = 0 
            else:
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.K_HOME:
            self.cursor = 0
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_length - 1
        else:
            self.engine.event_handler = MainGameEventHandler(self.engine)
class askUserEventHanlder(EventHandler):
    def handle_action(self, action: Optional[Action]) -> bool:
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
        return self.on_exit()
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym in {
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None
        return self.on_exit()
    def on_exit(self) -> Optional[Action]:
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None
    

class InventoryEventHandler(askUserEventHanlder):
    TITLE = "<Missing title>"
    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)
        height = number_of_items_in_inventory + 2 

        if height <= 3:
            height = 3
        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0
        y = 0

        width = len(self.TITLE) + 4
        console.draw_frame(x, y, width, height, title=self.TITLE, clear=True, fg=tcod.white, bg=tcod.black)

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + 1 + i, f"({item_key}) {item.name}")
            else:
                console.print(x + 1, y + 1, "(Inventory is empty)")
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a
        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid inventory selection.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)
    def on_item_selected(self, item: Item) -> Optional[Action]:

        raise NotImplementedError("on_item_selected must be implemented by a subclass.")

class InventoryActionHandler(InventoryEventHandler):
    TITLE = "Select an item to use"
    def on_item_selected(self, item: Item) -> Optional[Action]:
        return item.consumable.get_action(self.engine.player)

class InventoryDropHandler(InventoryEventHandler):
    TITLE = "Select an item to drop"
    def on_item_selected(self, item: Item) -> Optional[Action]:
        return DropItem(self.engine.player, item)