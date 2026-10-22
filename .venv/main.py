import entity_factory
import tcod 
from engine import Engine
from entity import Entity
import color
import copy
from procgen import generate_dungeon  

def main() -> None:
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 43
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30 
    max_monsters_per_room = 3
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD)
    player = copy.deepcopy(entity_factory.player)
    engine = Engine(player = player)
    engine.game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        engine=engine,
        max_monsters_per_room=max_monsters_per_room,
    )
    engine.update_fov()
    engine.message_log.add_message("Hello traveler! Welcome to the dungeon!", color.welcome_text)

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="My Game",
        vsync=True,
        ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")

        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)
            engine.event_handler.handle_events(context)
if __name__ == "__main__":
    main()
