from uac.config import Config
from uac.gameio import IOEnvironment
from uac.gameio.skill_registry import register_skill

config = Config()
io_env = IOEnvironment()



@register_skill("aim")
def aim():
    """
    Aim the weapon in the game.
    Parameters:
    - x: The normalized abscissa of the pixel.
    - y: The normalized ordinate of the pixel.
    """
    io_env.mouse_hold_button(button=io_env.RIGHT_MOUSE_BUTTON)


@register_skill("choose_weapons_at")
def choose_weapons_at(x, y):
    """
    Move the mouse to a specific location to choose weapons in the game.
    Parameters:
    - x: The normalized abscissa of the pixel.
    - y: The normalized ordinate of the pixel.
    """
    io_env.mouse_move_normalized(x, y)


# @register_skill("shoot")
def shoot(x, y):
    """
    Shoot the weapon at a specific location in view.
    Parameters:
    - x: The normalized abscissa of the pixel.
    - y: The normalized ordinate of the pixel.
    """
    io_env.mouse_move_normalized(x, y)
    io_env.mouse_click_button(button=io_env.LEFT_MOUSE_BUTTON, clicks=2)


@register_skill("view_weapons")
def view_weapons():
    """
    View the weapon wheel.
    """
    io_env.key_hold('tab')


@register_skill("fight")
def fight():
    """
    Fight agains another person.
    """
    io_env.key_press('f,f,f,f,f,f')


# def call_animals():
#     """
#     Call animals in the game.
#     """
#     pyautogui.mouseDown(button="right")
#     pydirectinput.keyDown("r")
#     time.sleep(0.5)
#     pydirectinput.keyUp("r")
#     pyautogui.mouseUp(button="right")


__all__ = [
    "aim",
    # "shoot",
    "choose_weapons_at",
    "view_weapons",
    "fight",
    #"call_animals",
]