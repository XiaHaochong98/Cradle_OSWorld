from collections import namedtuple
import platform
import ctypes

import pyautogui

if platform.system() == 'Windows':
    from ahk import AHK
    import pydirectinput

    # Windows API constants
    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_ABSOLUT = 0x8000
    WIN_NORM_MAX = 65536 # int max val

    ahk = AHK()

    # PyDirectInput is only used for key pressing, so no need for mouse checks
    pydirectinput.FAILSAFE = False

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


    def _mouse_coord_to_abs_win(coord, width_or_height):
        abs_coord = ((WIN_NORM_MAX * coord) / width_or_height) + (-1 if coord < 0 else 1)
        return int(abs_coord)

elif platform.system() == "Darwin":
    import AppKit


def mouse_button_down(button):
    if platform.system() == 'Windows':
        ahk.click(button=button, direction='D')
    else:
        pyautogui.mouseDown(button=button, duration=0.2)


def mouse_button_up(button):
    if platform.system() == 'Windows':
        ahk.click(button=button, direction='U')
    else:
        pyautogui.mouseUp(button=button, duration=0.2)


def mouse_click(click_count, button, relative=False):
    if platform.system() == 'Windows':
        ahk.click(click_count=click_count, button=button, relative=relative)
    else:
        for i in range(click_count):
            mouse_button_down(button)
            mouse_button_up(button)


def mouse_move_to(x, y, duration = -1, relative = False, screen_resolution = None, game_region = None):

    if platform.system() == 'Windows':
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()

        # logger.debug(f'game coord x {x} y {y} relative {relative}')

        event_flag = MOUSEEVENTF_MOVE

        if relative is False:
            event_flag = MOUSEEVENTF_ABSOLUT | MOUSEEVENTF_MOVE
            x = x + game_region[0]
            y = y + game_region[1]

            # logger.debug(f'screen x {x} y {y}')

            x = _mouse_coord_to_abs_win(x, screen_resolution[0])
            y = _mouse_coord_to_abs_win(y, screen_resolution[1])

            # logger.debug(f'windows x {x} y {y}')

        ii_.mi = MouseInput(int(x), int(y), 0, event_flag, 0, ctypes.pointer(extra))

        command = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))
    else:
        pyautogui.moveTo(x, y, duration=duration, relative=relative)


def get_mouse_location():
    if platform.system() == 'Windows':
        return ahk.get_mouse_position()
    else:
        p = pyautogui.position()
        return (p.x, p.y)


def key_down(key):
    if platform.system() == 'Windows':
        pydirectinput.keyDown(key)
    else:
        pyautogui.keyDown(key)


def key_up(key):
    if platform.system() == 'Windows':
        pydirectinput.keyUp(key)
    else:
        pyautogui.keyUp(key)


def get_screen_size():
    return pyautogui.size()


def get_named_windows(env_name):

    if platform.system() == 'Windows':
        return pyautogui.getWindowsWithTitle(env_name)
    elif platform.system() == "Darwin":
        ws = AppKit.NSWorkspace.sharedWorkspace()
        for app in ws.runningApplications():
            if app.localizedName() == env_name:
                # app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)

                window = namedtuple('A', ['left', 'top', 'width', 'height'])
                window.left = 0
                window.top = 0
                window.width = 0
                window.height = 0
                return window
        return []
    else:
        raise ValueError(f"Platform {platform.system()} not supported yet")
