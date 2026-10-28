from __future__ import annotations
import tcod
import color
from components import exceptions
from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union
from actions import (
    Action,
    BumpAction,
    DropItem,
    EquipAction,
    TakeStairsAction,
    WaitAction,
    pickupAction,
)
import os

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
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}

ConfirmKeys = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
}
ActionOrHandler = Union[Action, "BaseEventHandler"]

class BaseEventHandler:
    def dispatch(self, event: tcod.event.Event) -> Optional[ActionOrHandler]:
        if isinstance(event, tcod.event.Quit):
            return self.ev_quit(event)
        if isinstance(event, tcod.event.KeyDown):
            handler = getattr(self, "ev_keydown", None)
            if handler is not None:
                return handler(event)
        elif isinstance(event, tcod.event.MouseMotion):
            handler = getattr(self, "ev_mousemotion", None)
            if handler is not None:
                return handler(event)
        elif isinstance(event, tcod.event.MouseButtonDown):
            handler = getattr(self, "ev_mousebuttondown", None)
            if handler is not None:
                return handler(event)
        return None

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} cannot handle Action directly"
        return self
    def on_render(self, console: tcod.Console) -> None:
        raise NotImplementedError()
    def ev_quit(self, event: tcod.event.Quit) -> None:
        raise SystemExit()


if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            if not self.engine.player.is_alive:
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpHandler(self.engine)
            return MainGameEventHandler(self.engine)
        return self
    

    def handle_action(self, action: Optional[Action]) -> bool:
        if action is None:
            return False
        try:
            action.perform()
        except exceptions.Impossible as e:
            self.engine.message_log.add_message(e.args[0], color.impossible)
            return False

        self.engine.handle_enemy_turns()
        self.engine.update_fov()
        return True
        
    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        tile = event.integer_position
        if self.engine.game_map.in_bounds(tile.x, tile.y):
            self.engine.mouse_location = (tile.x, tile.y)

    def ev_quit(self, event: tcod.event.Quit) -> None:
        raise SystemExit()
    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)
    
class MainGameEventHandler(EventHandler):

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None
        key = event.sym
        modifier = event.mod
        player = self.engine.player
        if key == tcod.event.K_PERIOD and modifier & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
            return TakeStairsAction(player)

        if key in MoveKeys:
            dx, dy = MoveKeys[key]
            action = BumpAction(player, dx=dx, dy=dy)
        elif key in WaitKeys:
            action = WaitAction(player)
        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        elif key == tcod.event.K_v:
            return HistoryViewer(self.engine)
        elif key == tcod.event.K_g:
            action = pickupAction(player)
        elif key == tcod.event.K_i:
            return InventoryActionHandler(self.engine)
        elif key == tcod.event.K_SLASH:
            return LookHandler(self.engine)
        elif key == tcod.event.K_c:
            return CharacterScreenEventHandler(self.engine)


        return action
class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")
        raise exceptions.QuitWithoutSaving()

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()
    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_ESCAPE:
            self.on_quit()
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

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        if self.log_length == 0:
            return MainGameEventHandler(self.engine) if event.sym not in CURSOR_Y_KEYS else None
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
            return MainGameEventHandler(self.engine)
        return None
class AskUserEventHandler(EventHandler):
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        return self.on_exit()
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
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
    def on_exit(self) -> Optional[ActionOrHandler]:
        
        return MainGameEventHandler(self.engine)
    

class InventoryEventHandler(AskUserEventHandler):
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
                is_equipped = self.engine.player.equipment.item_is_equipped(item)
                item_string = f"({item_key}) {item.name}"
                if is_equipped:
                    item_string = f"{item_string} (E)"
                console.print(x + 1, y + 1 + i, item_string)
        else:
            console.print(x + 1, y + 1, "(Inventory is empty)")
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a
        if 0 <= index < 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid inventory selection.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)
    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            return item.consumable.get_action(self.engine.player)
        elif item.equipable:
            return EquipAction(self.engine.player, item)
        else:
            return None

class InventoryActionHandler(InventoryEventHandler):
    TITLE = "Select an item to use"

class InventoryDropHandler(InventoryEventHandler):
    TITLE = "Select an item to drop"
    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        return DropItem(self.engine.player, item)
class SelectIndexHandler(AskUserEventHandler):
    TITLE = "Select an index"
    def __init__(self, engine: Engine):
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = (player.x, player.y)

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.rgb[x, y]["bg"] = color.white
        console.rgb[x, y]["fg"] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        key = event.sym
        if key in MoveKeys:
            modifier = 1
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20
            x, y = self.engine.mouse_location
            dx, dy = MoveKeys[key]
            x += dx * modifier
            y += dy * modifier
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in ConfirmKeys:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        tile = event.integer_position
        if self.engine.game_map.in_bounds(tile.x, tile.y):
            if event.button == 1:
                return self.on_index_selected(tile.x, tile.y)
            return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        raise NotImplementedError("on_index_selected must be implemented by a subclass.")

class LookHandler(SelectIndexHandler):
    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        return MainGameEventHandler(self.engine)

class SingleRangedAttackHandler(SelectIndexHandler):
    def __init__(self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[ActionOrHandler]]):
        super().__init__(engine)
        self.callback = callback
    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        return self.callback((x, y))

class AreaRangedAttackHandler(SelectIndexHandler):
    def __init__(self, engine: Engine, radius: int, callback: Callable[[Tuple[int, int]], Optional[ActionOrHandler]]):
        super().__init__(engine)
        self.radius = radius
        self.callback = callback
    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.draw_frame(
            x=x - self.radius,
            y=y - self.radius,
            width=2 * self.radius + 1,
            height=2 * self.radius + 1,
            fg = color.red,
            clear = False,
        )
    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        return self.callback((x, y))
class PopupMessage(BaseEventHandler):
    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.Console) -> None:
        self.parent.on_render(console)
        console.rgb["fg"] //= 8
        console.rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg = color.white,
            bg = color.black,
            alignment = tcod.CENTER

        )
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        return self.parent

    
class LevelUpHandler(AskUserEventHandler):
    TITLE = "Level Up!"
    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0
        console.draw_frame(
            x=x,
            y=0,
            width=35,
            height = 8,
            title = self.TITLE,
            clear = True,
            fg = (255, 255, 255),
            bg=(0, 0, 0),
        )
        console.print(x=x + 1, y =1, string="congratulations!")
        console.print(x=x + 1, y =2, string="You have leveled up!")
        console.print(x=x + 1, y =3, string="Choose an attribute to increase.")
        console.print(
            x=x + 1,
            y=4,
            string = f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
        )
        console.print(
            x=x + 1,
            y=5,
            string = f"b) Strength (+1 Attack, from {self.engine.player.fighter.power})",
        )
        console.print(
            x=x + 1,
            y=6,
            string = f"c) Agility (+1 defense, from {self.engine.player.fighter.defense})",
        )
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 2:
            if index == 0:
                player.level.increase_max_hp()
            elif index == 1:
                player.level.increase_power()
            elif index == 2:
                player.level.increase_defense()
            return None
        return super().ev_keydown(event)
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        return None
class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=7,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(
            x=x + 1, y=y + 1, string=f"Level: {self.engine.player.level.current_level}"
        )
        console.print(
            x=x + 1, y=y + 2, string=f"XP: {self.engine.player.level.current_xp}"
        )
        console.print(
            x=x + 1,
            y=y + 3,
            string=f"XP for next Level: {self.engine.player.level.experience_to_next_level}",
        )

        console.print(
            x=x + 1, y=y + 4, string=f"Attack: {self.engine.player.fighter.power}"
        )
        console.print(
            x=x + 1, y=y + 5, string=f"Defense: {self.engine.player.fighter.defense}"
        )
        
