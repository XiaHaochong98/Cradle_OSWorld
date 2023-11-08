import pyautogui
import pydirectinput


def open_map():
    """
    Open the map or close map()
    """
    pydirectinput.press("m")


def add_marker():
    """
    Place your mouse over the map location you want to mark
    and click "z" to mark it.
    The mark will be followed by a red message on the map.
    Click Cancel message again
    """
    pydirectinput.press("z")


def add_waypoint():
    """
    Place the mouse over the target location
    and click "enter" to display the waypoint,
    the path to the target location
    Click Cancel message again
    """
    pydirectinput.press("enter")


def close_map():
    """
    click "esc" can close the map
    """
    pydirectinput.press("esc")


def zoom_map(ahk):
    ahk.click(button="WU")


def reduce_map(ahk):
    ahk.click(button="WD")


def open_index():
    """
    click "space" to open index
    """
    pydirectinput.press("space")


def close_index():
    """
    click "space" to close index
    """
    pydirectinput.press("space")


def next_index_object():
    """
     change the index type after opening the index
    """
    pydirectinput.press("q")


def previous_index_object():
    """
     change the index type after opening the index
    """
    pydirectinput.press("e")


def confirm_selection():
    """
    click mouse left once
    """
    pyautogui.mouseDown()
    pyautogui.mouseUp()


def move_map(ahk, width, height):
    """
    Moves the mouse on the screen based on the provided width and height offsets from its current position.
    """
    ahk.mouse_drag(width, height, relative=True)


def move_mouse_on_map(ahk, width, height, speed=100, relative=True):
    ahk.mouse_move(width, height, speed=speed, relative=relative)


def select_up_index_object():
    pydirectinput.press("up")


def select_down_index_object():
    pydirectinput.press("down")
