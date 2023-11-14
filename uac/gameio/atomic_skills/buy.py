import time
import pyautogui
import pydirectinput

from uac.gameio import IOEnvironment

io_env = IOEnvironment()
ahk = io_env.ahk


def zoom():
    """
    can zoom after open the catalogue
    """
    pyautogui.mouseDown(button="right")


def cancel_zoom():
    """
    Release the right mouse button to close zoom
    """
    pyautogui.mouseUp(button="right")


def browse_catalogue(duration=1):
    """
     Long press "e" to open the catalogue
    """
    pydirectinput.keyDown("e")
    time.sleep(duration)
    pydirectinput.keyUp("e")


def view_next_page():
    """
    press “e” can open next page,
    """
    pydirectinput.press("e")


def view_previous_page():
    """
    press “e” can return previous page,
    """
    pydirectinput.press("q")


def select_product_type():
    """
    When move the mouse over the location of the specified product type,
    the press enter can view the contained product
    """
    pydirectinput.press("enter")


def buy_product():
    """
    press "enter" can buy product
    """
    pydirectinput.press("enter")


def view_info():
    """
    view  product price and basic information
    """
    pydirectinput.press("f")


def hide_info():
    """
    hide product price and basic information
    """
    pydirectinput.press("f")


def product_details():
    """
    View product details
    """
    pydirectinput.press("space")


def scroll_up():
    pydirectinput.press("up")


def scroll_down():
    pydirectinput.press("down")


def scroll_up_for_info():
    ahk.click(button="WU")


def scroll_down_for_info():
    ahk.click(button="WD")


# Extra steps to buying clothing
def try_clothing():
    """
    view the try on clothes
    """
    pydirectinput.press("enter")


def view_all_clothing():
    """
     view all clothing
    """
    pydirectinput.press("space")


def select_clothing():
    """
    select clothing and buy this
    """
    pydirectinput.press("enter")


# When trying on clothes, you can choose the color of the clothes
def select_right_color():
    pydirectinput.press("right")


def select_left_color():
    pydirectinput.press("left")


def select_up_color():
    pydirectinput.press("up")


def select_down_color():
    pydirectinput.press("down")


# Buy products on the shelves
def examine_product(duration=1):
    pydirectinput.keyDown("e")
    time.sleep(duration)
    pydirectinput.keyUp("e")


def toggle_view():
    pydirectinput.press("v")


def buy_from_shelf(duration=1):
    pydirectinput.keyDown("r")
    time.sleep(duration)
    pydirectinput.keyUp("r")


def browse_shelf(duration=1):
    pyautogui.mouseDown(button="right")
    time.sleep(duration)
    pyautogui.mouseUp()
