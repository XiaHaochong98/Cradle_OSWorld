import pyautogui
import pydirectinput


def shopkeeper_interaction():
    """
    Long press the right mouse button to talk with shopkeeper,
    can open transaction type.
    It must be closed after determining the type of transaction
    """
    pyautogui.mouseDown(button="right")


def cancel_shopkeeper_interaction():
    pyautogui.mouseUp(button="right")


def select_products(ahk, width, height, speed=100):
    """
    Move the mouse to the specified position
    """
    ahk.mouse_move(width, height, speed=speed, relative=False)


def select_up_product():
    pydirectinput.press("up")


def select_down_product():
    pydirectinput.press("down")


def confirm_selection():
    """
    click mouse left once to confirm
    """
    pyautogui.mouseDown()
    pyautogui.mouseUp()


def go_back():
    """
    Return to upper level
    """
    pydirectinput.press("esc")
