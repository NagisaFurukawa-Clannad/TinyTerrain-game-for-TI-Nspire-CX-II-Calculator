import random
import time


WORLD_WIDTH = 48
WORLD_HEIGHT = 16
VIEW_WIDTH = 23
VIEW_HEIGHT = 14
TILE_SIZE = 14
TILE_WIDTH = 319.0 / VIEW_WIDTH
EMPTY = " "


def make_world():
    world = []
    surface = 5
    for x in range(WORLD_WIDTH):
        surface += random.randint(-1, 1)
        surface = max(3, min(7, surface))
        column = []
        for y in range(WORLD_HEIGHT):
            if y < surface:
                tile = EMPTY
            elif y == surface:
                tile = "D"
            elif y < surface + 3:
                tile = "D"
            else:
                tile = "S"
                if random.randint(1, 12) == 1:
                    tile = "O"
            column.append(tile)
        world.append(column)
    return world


def is_solid(world, x, y):
    if x < 0 or x >= WORLD_WIDTH or y >= WORLD_HEIGHT:
        return True
    if y < 0:
        return False
    return world[x][y] != EMPTY


def is_grounded(world, player_x, player_y):
    return is_solid(world, player_x, player_y + 1)


def get_target(player_x, player_y, aim_x, aim_y):
    return player_x + aim_x, player_y + aim_y


def get_tile_color(world, x, y):
    tile = world[x][y]
    if tile == "D":
        if y == 0 or world[x][y - 1] == EMPTY:
            return 70, 165, 65
        return 145, 95, 55
    if tile == "S":
        return 115, 120, 130
    if tile == "O":
        return 175, 130, 75
    return None


def screen_column_x(column):
    return int(round(column * TILE_WIDTH))


def draw(world, player_x, player_y, aim_x, aim_y, inventory, ti_draw,
         message):
    camera_x = player_x - VIEW_WIDTH // 2
    camera_x = max(0, min(WORLD_WIDTH - VIEW_WIDTH, camera_x))
    camera_y = max(0, min(WORLD_HEIGHT - VIEW_HEIGHT, player_y - 4))
    target_x, target_y = get_target(player_x, player_y, aim_x, aim_y)
    ti_draw.clear()
    ti_draw.set_color(130, 195, 245)
    ti_draw.fill_rect(0, 0, 319, 209)
    last_color = (130, 195, 245)
    for y in range(camera_y, camera_y + VIEW_HEIGHT):
        run_start = None
        run_color = None
        for x in range(camera_x, camera_x + VIEW_WIDTH):
            if x == player_x and y == player_y:
                color = None
            else:
                color = get_tile_color(world, x, y)
            if color != run_color:
                if run_color is not None:
                    if run_color != last_color:
                        ti_draw.set_color(*run_color)
                        last_color = run_color
                    left = screen_column_x(run_start - camera_x)
                    right = screen_column_x(x - camera_x)
                    ti_draw.fill_rect(
                        left,
                        7 + (y - camera_y) * TILE_SIZE,
                        right - left,
                        TILE_SIZE)
                if color is None:
                    run_start = None
                else:
                    run_start = x
                run_color = color
        if run_color is not None:
            if run_color != last_color:
                ti_draw.set_color(*run_color)
                last_color = run_color
            left = screen_column_x(run_start - camera_x)
            right = screen_column_x(VIEW_WIDTH)
            ti_draw.fill_rect(
                left,
                7 + (y - camera_y) * TILE_SIZE,
                right - left,
                TILE_SIZE)

    if camera_x <= player_x < camera_x + VIEW_WIDTH and \
            camera_y <= player_y < camera_y + VIEW_HEIGHT:
        if last_color != (245, 210, 65):
            ti_draw.set_color(245, 210, 65)
        player_left = screen_column_x(player_x - camera_x)
        player_right = screen_column_x(player_x - camera_x + 1)
        player_screen_y = 7 + (player_y - camera_y) * TILE_SIZE
        ti_draw.fill_rect(
            player_left + 3, player_screen_y + 2,
            player_right - player_left - 6, TILE_SIZE - 3)

    if (camera_x <= target_x < camera_x + VIEW_WIDTH and
            camera_y <= target_y < camera_y + VIEW_HEIGHT):
        target_left = screen_column_x(target_x - camera_x)
        target_right = screen_column_x(target_x - camera_x + 1)
        target_screen_y = 7 + (target_y - camera_y) * TILE_SIZE
        ti_draw.set_color(255, 255, 255)
        ti_draw.draw_rect(
            target_left, target_screen_y, target_right - target_left,
            TILE_SIZE)

    if aim_x < 0:
        aim_name = "LEFT"
    elif aim_x > 0:
        aim_name = "RIGHT"
    elif aim_y < 0:
        aim_name = "UP"
    else:
        aim_name = "DOWN"
    if last_color != (25, 35, 50):
        ti_draw.set_color(25, 35, 50)
    ti_draw.draw_text(
        7, 28, "DIRT {0}  STONE {1}  ORE {2}".format(
            inventory["D"], inventory["S"], inventory["O"]))
    ti_draw.draw_text(7, 165, "AIM: " + aim_name + "  ARROWS aim")
    ti_draw.draw_text(7, 183, "4/6 move  8 jump  5 mine  2 build  0 quit")
    if message:
        ti_draw.draw_text(205, 165, message)
    ti_draw.set_color(0, 0, 0)
    ti_draw.fill_rect(0, 199, 319, 10)


def play():
    import ti_draw
    import ti_system

    world = make_world()
    player_x = 3
    player_y = 0
    while not is_solid(world, player_x, player_y + 1):
        player_y += 1

    aim_x = 1
    aim_y = 0
    inventory = {"D": 0, "S": 0, "O": 0}
    message = ""
    draw(world, player_x, player_y, aim_x, aim_y, inventory, ti_draw, message)

    while True:
        command = ti_system.get_key()
        if command != "0" and command != "esc" and command not in (
                "2", "4", "5", "6", "8", "left", "right", "up", "down"):
            time.sleep(0.05)
            continue

        if command == "0" or command == "esc":
            break

        message = ""
        jumping = False
        if command == "4" or command == "6" or command == "left" or command == "right":
            if command == "4" or command == "left":
                aim_x = -1
            else:
                aim_x = 1
            aim_y = 0
            next_x = player_x + aim_x
            if not is_solid(world, next_x, player_y):
                player_x = next_x
        elif command == "up":
            aim_x = 0
            aim_y = -1
        elif command == "down":
            aim_x = 0
            aim_y = 1
        elif command == "8":
            if is_grounded(world, player_x, player_y):
                for step in range(2):
                    if not is_solid(world, player_x, player_y - 1):
                        player_y -= 1
                jumping = True
        elif command == "5":
            target_x, target_y = get_target(
                player_x, player_y, aim_x, aim_y)
            if (0 <= target_x < WORLD_WIDTH and
                    0 <= target_y < WORLD_HEIGHT and
                    is_solid(world, target_x, target_y)):
                tile = world[target_x][target_y]
                world[target_x][target_y] = EMPTY
                inventory[tile] += 1
            else:
                message = "No block there."
        elif command == "2":
            target_x, target_y = get_target(
                player_x, player_y, aim_x, aim_y)
            if (0 <= target_x < WORLD_WIDTH and
                    0 <= target_y < WORLD_HEIGHT and
                    not is_solid(world, target_x, target_y)):
                tile = ""
                if inventory["D"] > 0:
                    tile = "D"
                elif inventory["S"] > 0:
                    tile = "S"
                elif inventory["O"] > 0:
                    tile = "O"
                if tile:
                    world[target_x][target_y] = tile
                    inventory[tile] -= 1
                else:
                    message = "No blocks to build with."
            else:
                message = "Space already occupied."

        if not jumping and not is_grounded(world, player_x, player_y):
            if not is_solid(world, player_x, player_y + 1):
                player_y += 1

        draw(world, player_x, player_y, aim_x, aim_y, inventory, ti_draw,
             message)

    ti_draw.clear()
    ti_draw.set_color(25, 35, 50)
    ti_draw.draw_text(110, 95, "Thanks for playing!")


if __name__ == "__main__" or __name__.lower() == "terrain":
    play()
