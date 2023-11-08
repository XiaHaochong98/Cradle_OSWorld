import time
import pydirectinput


def sell_product(duration=1):
    """
    Open the trade bar for sale
    """
    pydirectinput.keyDown("r")
    time.sleep(duration)
    pydirectinput.keyUp("r")


def sell_product_all(duration=1):
    """
    Press and hold "f" to sell the full amount of this product
    But the quantity must be greater than one
    """
    pydirectinput.keyDown("f")
    time.sleep(duration)
    pydirectinput.keyUp("f")


def sell_one_product():
    """
    Press "enter" to sell one product
    """
    pydirectinput.press("enter")


def next_product_type():
    """
    press “e” to change products type,
    Return to next
    """
    pydirectinput.press("e")


def previous_product_type():
    """
    press “q” to change products type,
    Return to previous
    """
    pydirectinput.press("q")
