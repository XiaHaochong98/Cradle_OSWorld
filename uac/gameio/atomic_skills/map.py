import pyautogui
import pydirectinput
from uac.gameio import IOEnvironment
from uac.gameio.skill_registry import register_skill

io_env = IOEnvironment()
ahk = io_env.ahk


@register_skill("open_map")
def open_map():
    """
    Opens the in-game map.
    """
    pydirectinput.press("m")


@register_skill("add_mark")
def add_mark():
    """
    Marks the current mouse position on the map by pressing "z".
    A red message indicating the mark will appear on the map.
    Clicks the Cancel message if it appears.
    """
    pydirectinput.press("z")


@register_skill("add_waypoint")
def add_waypoint():
    """
    Creates a waypoint at the item selected in the opened map index, by pressing "enter".
    Waypoint creation displays the path to the target location.

    """
    pydirectinput.press("enter")


@register_skill("close_map")
def close_map():
    """
    Closes the in-game map by pressing "esc".
    """
    pydirectinput.press("esc")


@register_skill("zoom_in_map")
def zoom_in_map():
    """
    Zooms in on the in-game map by scrolling the mouse wheel up.
    """
    ahk.click(button="WU")


@register_skill("zoom_out_map")
def zoom_out_map():
    """
    Zooms out on the in-game map by scrolling the mouse wheel down.
    """
    ahk.click(button="WD")


@register_skill("open_index")
def open_index():
    """
    Opens the game index by pressing the "space" key.
    """
    pydirectinput.press("space")


@register_skill("close_index")
def close_index():
    """
    Closes the game index by pressing the "space" key.
    """
    pydirectinput.press("space")


@register_skill("switch_to_next_index_object")
def switch_to_next_index_object():
    """
    Switches to the next index object type after opening the index by pressing "q".
    """
    pydirectinput.press("q")


@register_skill("switch_to_previous_index_object")
def switch_to_previous_index_object():
    """
    Switches to the previous index object type after opening the index by pressing "e".
    """
    pydirectinput.press("e")


@register_skill("select_mouse_index_object")
def select_mouse_index_object():
    """
    Selects the index object at the current mouse position by clicking the left mouse button once.
    """
    pyautogui.mouseDown()
    pyautogui.mouseUp()


@register_skill("adjust_map_position")
def adjust_map_position(width, height):
    """
    Drags the in-game map by using the mouse drag function, adjusting the map position based on
    the provided horizontal and vertical offsets.

    Parameters:
    - width: The offset in pixels to move the mouse horizontally on the map.
    - height: The offset in pixels to move the mouse vertically on the map.
    """
    ahk.mouse_drag(width, height, relative=True)


@register_skill("move_mouse_on_map")
def move_mouse_on_map(width, height, speed=100, relative=True):
    """
    Moves the mouse to a specific position on the in-game map based on the provided width and height offsets.

    Parameters:
    - width: The offset in pixels to move the mouse horizontally on the map.
    - height: The offset in pixels to move the mouse vertically on the map.
    - speed: The speed of the mouse movement (default is 100).
    - relative: If True, the offsets are relative to the current mouse position (default is True). If False, Move the mouse to the pixel position of (width, height).
    """
    ahk.mouse_move(width, height, speed=speed, relative=relative)


@register_skill("select_previous_index_object")
def select_previous_index_object():
    """
    When the index is opened, moves to the previous index selection by pressing the "up" arrow key.
    Items of interest may be out of view, so this skill is useful for scrolling through the index.
    """
    pydirectinput.press("up")


@register_skill("select_next_index_object")
def select_next_index_object():
    """
    When the index is opened, moves to the next index selection by pressing the "down" arrow key.
    Items of interest may be out of view, so this skill is useful for scrolling through the index.
    """
    pydirectinput.press("down")

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
