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


def MouseMoveTo(x, y):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.mi = MouseInput(x, y, 0, 0x0001, 0, ctypes.pointer(extra))

    command = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))


config = Config()
io_env = IOEnvironment()
ahk = io_env.ahk


@register_skill("shoot")
def shoot(x, y):
    """
    Shoots the weapon in the game.
    """

    MouseMoveTo(x, y)
    ahk.click(click_count=1, button='R', relative=False)
    ahk.click(click_count=2, relative=False)


def reload_gun():
    """
    Reload the gun in the game.
    """
    pydirectinput.keyDown("r")


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
    "reload_gun",
    "call_animals",
]
