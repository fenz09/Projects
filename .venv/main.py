import setup_game as se
import tcod
import copy
from entity import Entity
import color
import traceback
import exceptions
import input_handlers

def save_game(handler: input_handlers.EventHandler, filename: str) -> None:
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print(f"Game saved to {filename}")
def main() -> None:
    screen_width = 80
    screen_height = 50
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD)
    handler: input_handlers.BaseEventHandler = se.MainMenu()

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="My Game",
        vsync=True,
        ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)
                for event in tcod.event.wait():
                    context.convert_event(event)
                    handler = handler.handle_events(event)
        except Exception:
            traceback.print_exc()
            if isinstance(handler, input_handlers.EventHandler):
                handler.engine.message_log.add_message(traceback.format_exc(), color.error)
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:
            save_game(handler, "savefile.sav")
            raise
        except BaseException:
            save_game(handler, "savefile.sav")
            raise
       
if __name__ == "__main__":
    main()
