import time

import pydirectinput
import pyautogui
import ctypes

from uac.config import Config
from uac.gameio import IOEnvironment
from uac.gameio.skill_registry import register_skill

PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort),
    ]


class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]
    
config = Config()
io_env = IOEnvironment()
ahk = io_env.ahk

def MouseMoveTo(x, y):
    # first de-normalization, then relative pixel calculation
    move_x = int(x*config.game_resolution[0] - config.game_resolution[0] / 2)
    move_y = int(y*config.game_resolution[1] - config.game_resolution[1] / 2)
    
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput(move_x, move_y, 0, 0x0001, 0, ctypes.pointer(extra))

    command = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

@register_skill("choose_weapons_at")
def choose_weapons_at(x, y):
    """
    Move the mouse to a specific location to choose weapons in the game.
    Parameters:
    - x: The abscissa of the pixel.
    - y: The ordinate of the pixel.
    """
    MouseMoveTo(x, y)
    

@register_skill("shoot")
def shoot(x, y):
    """
    Shoot the weapon at a specific location in view.
    Parameters:
    - x: The abscissa of the pixel.
    - y: The ordinate of the pixel.
    """

    MouseMoveTo(x, y)
    ahk.click(click_count=1, button='R', relative=False)
    ahk.click(click_count=2, relative=False)
    
@register_skill("view_weapons")
def view_weapons():
    """
    View the weapon wheel.
    """
    pydirectinput.keyDown('tab')


def call_animals():
    """
    Call animals in the game.
    """
    pyautogui.mouseDown(button="right")
    pydirectinput.keyDown("r")
    time.sleep(0.5)
    pydirectinput.keyUp("r")
    pyautogui.mouseUp(button="right")


__all__ = [
    "shoot",
    "choose_weapons_at",
    "view_weapons",
]
