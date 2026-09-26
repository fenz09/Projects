from typing import Optional
import tcod.event
from actions import action, escape_action, bump_action

class EventHandler(tcod.event.EventDispatch[action]):
    def ev_quit(self, event: tcod.event.Quit) -> Optional[action]:
        raise SystemExit()
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[action]:
        action: Optional[action] = None
        key = event.sym

        if key == tcod.event.K_W:
            action = bump_action(dx=0, dy=-1)
        elif key == tcod.event.K_S:
            action = bump_action(dx=0, dy=1)
        elif key == tcod.event.K_D:
            action = bump_action(dx=1, dy=0)
        elif key == tcod.event.K_A:
            action = bump_action(dx=-1, dy=0)
        elif key == tcod.event.K_ESCAPE:
            action = escape_action()

        return action
