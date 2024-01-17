from uac.config import Config
from uac.log import Logger
from uac.gameio import IOEnvironment
from uac.gameio.skill_registry import register_skill, post_skill_wait

config = Config()
logger = Logger()
io_env = IOEnvironment()

@register_skill("open_map")
def open_map():
    """
    Opens the in-game map.
    """

    logger.write("Running open_map()")

    io_env.key_press('m')

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("add_mark")
def add_mark():
    """
    Marks the current mouse position on the map by pressing "z".
    A red message indicating the mark will appear on the map.
    Clicks the Cancel message if it appears.
    """
    io_env.key_press('z')


@register_skill("add_waypoint")
def add_waypoint():
    """
    Creates a waypoint at the item selected in the opened map index, by pressing "enter".
    Waypoint creation displays the path to the target location.
    """

    logger.write("Running add_waypoint()")

    io_env.key_press('enter')


@register_skill("close_map")
def close_map():
    """
    Closes the in-game map by pressing "esc".
    """
    io_env.key_press('esc')

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


#@register_skill("zoom_in_map")
def zoom_in_map():
    """
    Zooms in on the in-game map by scrolling the mouse wheel up.
    """
    io_env.mouse_click_button('WU')


#@register_skill("zoom_out_map")
def zoom_out_map():
    """
    Zooms out on the in-game map by scrolling the mouse wheel down.
    """
    io_env.mouse_click_button('WD')


@register_skill("open_index")
def open_index():
    """
    Opens the map index by pressing the "space" key, after the map is open.
    """

    logger.write("Running open_index()")

    io_env.key_press('space')

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("close_index")
def close_index():
    """
    Closes the game index by pressing the "space" key.
    """
    io_env.key_press('space')

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


#@register_skill("switch_to_next_index_object")
def switch_to_next_index_object():
    """
    Switches to the next index object type after opening the index by pressing "q".
    """
    io_env.key_press('q')


#@register_skill("switch_to_previous_index_object")
def switch_to_previous_index_object():
    """
    Switches to the previous index object type after opening the index by pressing "e".
    """
    io_env.key_press('e')


#@register_skill("select_mouse_index_object")
def select_mouse_index_object():
    """
    Selects the index object at the current mouse position by clicking the left mouse button once.
    """
    io_env.mouse_click_button_and_hold('left', duration=0.2)


#@register_skill("adjust_map_position")
def adjust_map_position(width, height):
    """
    Drags the in-game map by using the mouse drag function, adjusting the map position based on
    the provided horizontal and vertical offsets.

    Parameters:
    - width: The offset in pixels to move the mouse horizontally on the map.
    - height: The offset in pixels to move the mouse vertically on the map.
    """
    io_env.ahk.mouse_drag(width, height, relative=True)


#@register_skill("move_mouse_on_map")
def move_mouse_on_map(width, height, speed=100, relative=True):
    """
    Moves the mouse to a specific position on the in-game map based on the provided width and height offsets.

    Parameters:
    - width: The offset in pixels to move the mouse horizontally on the map.
    - height: The offset in pixels to move the mouse vertically on the map.
    - speed: The speed of the mouse movement (default is 100).
    - relative: If True, the offsets are relative to the current mouse position (default is True). If False, Move the mouse to the pixel position of (width, height).
    """
    io_env.ahk.mouse_move(width, height, speed=speed, relative=relative)


@register_skill("select_previous_index_object")
def select_previous_index_object():
    """
    When the index is opened, moves to the previous index selection by pressing the "up" arrow key.
    Items of interest may be out of view, so this skill is useful for scrolling through the index.
    """
    io_env.key_press('up')


@register_skill("select_next_index_object")
def select_next_index_object():
    """
    When the index is opened, moves to the next index selection by pressing the "down" arrow key.
    Items of interest may be out of view, so this skill is useful for scrolling through the index.
    """
    io_env.key_press('down')


__all__ = [
    "open_map",
    #"add_mark",
    "add_waypoint",
    "close_map",
    #"zoom_in_map",
    #"zoom_out_map",
    "open_index",
    "close_index",
    #"switch_to_next_index_object",
    #"switch_to_previous_index_object",
    #"select_mouse_index_object",
    #"adjust_map_position",
    #"move_mouse_on_map",
    "select_previous_index_object",
    "select_next_index_object",
]
