import pyautogui
import pydirectinput

from uac.config import Config
from uac.gameio import IOEnvironment
from uac.gameio.skill_registry import register_skill, post_skill_wait

config = Config()
io_env = IOEnvironment()
ahk = io_env.ahk


@register_skill("shopkeeper_interaction")
def shopkeeper_interaction():
    """
    Initiates interaction with the shopkeeper by long-pressing the right mouse button.
    This action opens the transaction menu.
    Note: The transaction type must be determined and the interaction closed afterward.
    """
    pyautogui.mouseDown(button="right")

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("cancel_shopkeeper_interaction")
def cancel_shopkeeper_interaction():
    """
    Cancels the interaction with the shopkeeper by releasing the right mouse button.
    """
    pyautogui.mouseUp(button="right")

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("select_products_by_mouse")
def select_products_by_mouse(width, height, speed=100, relative=False):
    """
    Moves the mouse to the specified position for selecting products.

    Parameters:
     - width: The offset in pixels to move the mouse horizontally on the map.
     - height: The offset in pixels to move the mouse vertically
     - speed: The speed of the mouse movement (default is 100).
     - relative: If True, the offsets are relative to the current mouse position. If False, Move the mouse to the pixel position of (width, height)(default is False).
    """
    ahk.mouse_move(width, height, speed=speed, relative=relative)


@register_skill("mouse_select_target_object")
def mouse_select_target_object():
    """
    Confirms the selection by clicking the left mouse button once.
    """
    pyautogui.mouseDown()
    pyautogui.mouseUp()


@register_skill("go_back")
def go_back():
    """
    Returns to the upper level by pressing the "esc" key.
    """
    pydirectinput.press("esc")

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("select_next_up_product")
def select_next_up_product():
    """
    This function simulates the action of selecting the product on the next upside of the current selected product.
    It uses the pydirectinput library to press the "up" key.
    """
    pydirectinput.press("up")


@register_skill("select_next_down_product")
def select_next_down_product():
    """
    This function simulates the action of selecting the product on the next downside of the current selected product.
    It uses the pydirectinput library to press the "down" key.
    """
    pydirectinput.press("down")


@register_skill("select_leftside_product")
def select_leftside_product():
    """
    This function simulates the action of selecting the product on the next leftside of the current selected product.
    It uses the pydirectinput library to press the "left" key.
    """
    pydirectinput.press("left")


@register_skill("select_rightside_product")
def select_rightside_product():
    """
    This function simulates the action of selecting the product on the next rightside of the current selected product.
    It uses the pydirectinput library to press the "right" key.
    """
    pydirectinput.press("right")


@register_skill("select_next_product")
def select_next_product():
    """
    This function simulates the action of selecting the next product of the current selected product.
    It uses the pydirectinput library to press the "right" key.
    """
    pydirectinput.press("right")


__all__ = [
    "shopkeeper_interaction",
    "cancel_shopkeeper_interaction",
    #"select_products_by_mouse",
    #"select_upside_product",
    #"select_downside_product",
    "select_next_product",
    #"select_leftside_product",
    #"select_rightside_product",
    #"mouse_select_target_object",
    #"go_back"
]

