import os
import time
import ctypes
import math

from ahk import AHK
import pydirectinput
import pyautogui

from uac.utils import Singleton
from uac.config import Config
from uac.log import Logger

config = Config()
logger = Logger()


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


class IOEnvironment(metaclass=Singleton):
    """
    Wrapper for resources to interact with the game to make sure they're available where needed and multiple instances are not created.
    """

    # Constants
    RIGHT_MOUSE_BUTTON = 'R'
    LEFT_MOUSE_BUTTON = 'L'
    MIDDLE_MOUSE_BUTTON = 'M'
    WHEEL_UP_MOUSE_BUTTON = 'WU'
    WHEEL_DOWN_MOUSE_BUTTON = 'WD'

    MIN_DURATION = 2 # In seconds

    HOLD_DEFAULT_BLOCK_TIME = 2
    RELEASE_DEFAULT_BLOCK_TIME = 0.5

    MAX_ITERATIONS = 3

    KEY_KEY = 'key'
    BUTTON_KEY = 'button'
    EXPIRATION_KEY = 'expiration'

    # All key interactions are now tracked and use the same calling structure
    # - Release is equivalent to keyUp. I.e., release a key that was pressed or held.
    # - Hold is equivalent to keyDown. I.e., hold a key for a certain duration, probably while something else happens.
    # - Press is equivalent to keyDown followed by keyUp, after a delay. I.e., press a key for a short duration.
    ACTION_PRESS = 'press' # Equivalent to click on the mouse
    ACTION_HOLD = 'hold'
    ACTION_RELEASE = 'release'

    # List of keys currently held. To be either released by specific calls or after timeout (max iterations).
    # {
    #     self.KEY_KEY: key,
    #     self.EXPIRATION_KEY: self.MAX_ITERATIONS
    # }
    held_keys = []
    held_buttons = []

    # Used currently due to an issue with pause in RDR2
    backup_held_keys = []
    backup_held_buttons = []


    def __init__(self) -> None:
        """Initialize the IO environment class"""
        self.ahk = AHK()


    def pop_held_button(self, button):

        # pyautogui.mouseUp(button=button)
        self._mouse_button_up(button)

        # Remove from held list
        for i in range(len(self.held_buttons)):
            if self.held_buttons[i][self.BUTTON_KEY] == button:
                self.held_buttons.pop(i)
                break

        time.sleep(self.RELEASE_DEFAULT_BLOCK_TIME)


    def put_held_button(self, button):

        for b in self.held_buttons:
            if b == button:
                logger.warn(f'Button {b} already being held.')
                return
        else:
            entry = {
                self.BUTTON_KEY: button,
                self.EXPIRATION_KEY: self.MAX_ITERATIONS
            }
            self.held_buttons.append(entry)

            # pyautogui.mouseDown(button=button)
            self._mouse_button_down(button)

            time.sleep(self.HOLD_DEFAULT_BLOCK_TIME)


    def _mouse_button_down(self, button):
        self.ahk.click(button=button, direction='D')


    def _mouse_button_up(self, button):
        self.ahk.click(button=button, direction='U')


    def pop_held_keys(self, key):

        if self.check_held_keys(keys = [key]):
            pydirectinput.keyUp(key)
            time.sleep(self.RELEASE_DEFAULT_BLOCK_TIME)
            self.held_keys.pop()
        else:
            pydirectinput.keyUp(key) # Just as a guarantee to up an untracked key
            logger.warn(f'Key {key} was not being held at top.')

        self._to_message(self.held_keys, self.ACTION_RELEASE)


    def put_held_keys(self, key):

        top_key = _safe_list_get(self.held_keys, -1, self.KEY_KEY)
        if key == top_key:
            logger.warn(f'Key {key} already being held.')
        else:
            entry = {
                self.KEY_KEY: key,
                self.EXPIRATION_KEY: self.MAX_ITERATIONS
            }
            self.held_keys.append(entry)

            pydirectinput.keyDown(key)

            time.sleep(self.HOLD_DEFAULT_BLOCK_TIME)

            self._to_message(self.held_keys, self.ACTION_HOLD)


    def check_held_keys(self, keys):

        result = False

        if keys is not None and len(keys) != 0:
            for e in self.held_keys:
                k = e[self.KEY_KEY]
                if k in keys:
                    result = True
                    break

        return result


    def _to_message(self, list, purpose):

        vals = ', '.join(f'{e[self.KEY_KEY]}:{e[self.EXPIRATION_KEY]}' for e in list)
        msg = f'Held keys after {purpose}: {vals}'

        logger.debug(msg)

        return msg


    def update_timeouts(self):

        if self.held_keys is None or len(self.held_keys) == 0:
            return

        tmp_list = []

        for e in self.held_keys:

            t = e[self.EXPIRATION_KEY] - 1
            if t <= 0:
                key = e[self.KEY_KEY]
                logger.warn(f'Releasing key {key} after timeout.')
                pydirectinput.keyUp(key)
                time.sleep(0.1)

            else:
                e[self.EXPIRATION_KEY] = t
                tmp_list.append(e)

        self.held_keys = tmp_list.copy()
        del tmp_list

        tmp_list = []

        for e in self.held_buttons:

            t = e[self.EXPIRATION_KEY] - 1
            if t <= 0:
                button = e[self.BUTTON_KEY]
                logger.warn(f'Releasing mouse button {button} after timeout.')
                self._mouse_button_up(button)
                time.sleep(0.1)

            else:
                e[self.EXPIRATION_KEY] = t
                tmp_list.append(e)

        self.held_buttons = tmp_list.copy()
        del tmp_list


    def handle_hold_in_pause(self):
        self.backup_held_keys = self.held_keys.copy()
        if self.backup_held_keys is not None and self.backup_held_keys != []:
            for e in self.backup_held_keys:
                pydirectinput.keyUp(e[self.KEY_KEY])

        self.held_keys = []

        self.backup_held_buttons = self.held_buttons.copy()
        if self.backup_held_buttons is not None and self.backup_held_buttons != []:
            for e in self.backup_held_buttons:
                self._mouse_button_up(e[self.BUTTON_KEY])

        self.held_buttons = []


    def handle_hold_in_unpause(self):
        if self.backup_held_keys is not None and self.backup_held_keys != []:
            for e in self.backup_held_keys:
                pydirectinput.keyDown(e[self.KEY_KEY])

            self.held_keys = self.backup_held_keys.copy()

        if self.backup_held_buttons is not None and self.backup_held_buttons != []:
            for e in self.backup_held_buttons:
                self._mouse_button_down(e[self.BUTTON_KEY])

            self.held_buttons = self.backup_held_buttons.copy()


    def list_session_screenshots(self, session_dir: str = config.work_dir):

        # List all files in dir starting with "screen"
        screenshots = [f for f in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, f)) and f.startswith("screen")]

        # Sort list by creation time
        screenshots.sort(key=lambda x: os.path.getctime(os.path.join(session_dir, x)))

        return screenshots


    def mouse_move_normalized(self, x, y):
        x = int(x*config.game_resolution[0] - config.game_resolution[0] / 2)
        y = int(y*config.game_resolution[1] - config.game_resolution[1] / 2)
        # logger.debug(f"x {x} y {y}")

        self.mouse_move(x, y)


    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_ABSOLUT = 0x8000

    def mouse_move(self, x, y):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(x, y, 0, self.MOUSEEVENTF_MOVE, 0, ctypes.pointer(extra))

        command = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))


    def mouse_move_horizontal_angle(self, theta):
        distance = _theta_calculation(theta)
        self.ahk.mouse_move(distance, 0, speed=100, relative=True)


    def mouse_click(self, button, duration = None, clicks=1):
        self.mouse_click_button(button, duration, clicks)


    def mouse_click_button(self, button, duration = None, clicks=1):

        button = self.map_button(button)

        if duration is None:
            self.ahk.click(click_count=clicks, button=button, relative=False)
        else:
            self._mouse_button_down(button)
            time.sleep(duration)
            self._mouse_button_up(button)


    def mouse_hold(self, button, duration = None):

        if duration is None:
            self.mouse_hold_button(button)
        else:
            self._mouse_button_down(button)
            time.sleep(duration)
            self._mouse_button_up(button)


    def mouse_hold_button(self, button):

        button = self.map_button(button)

        self.put_held_button(button)


    def mouse_release(self, button):
        self.mouse_release_button(button)


    def mouse_release_button(self, button):

        button = self.map_button(button)

        self.pop_held_button(button)


    def _check_multi_key(self, input):

        if input is not None and len(input) > 1:
            if type(input) is list:
                return (True, input)
            else:
                key_tokens = input.split(',')
                keys = []
                for k in key_tokens:
                    k = k.strip()
                    if k != '':
                        k = self.map_key(k)
                        keys.append(k)

                if len(keys) == 0:
                    return (False, None)
                elif len(keys) == 1:
                    return (False, keys[0])
                else:
                    return (True, keys)

        else:
            return (False, None)


    # Special function to facilitate multi-key combos from GPT-4V like "io_env.key_hold('w,space')", which are commonly generated
    def _multi_key_action(self, keys, action, duration = 2):

        actions = [self.ACTION_PRESS, self.ACTION_HOLD, self.ACTION_RELEASE]

        if action not in actions:
            logger.warn(f'Invalid action: {action}. Ignoring it.')

        # Act in order, release in reverse
        for key in keys:

            # Special case to facilitate multi-key combos
            if key != keys[-1]:
                action = self.ACTION_HOLD

            if action == self.ACTION_PRESS:
                self.key_press(key)
            elif action == self.ACTION_HOLD:
                self.key_hold(key)

        if duration is None:
            duration = 0.3

        time.sleep(duration)

        for key in reversed(keys):
            self.key_release(key)


    def key_press(self, key, duration=None):

        key = self.map_key(key)

        f, keys = self._check_multi_key(key)
        if f == True:
            self._multi_key_action(keys, self.ACTION_PRESS, duration)
        else:

            if duration is None:
                pydirectinput.keyDown(key)
                #time.sleep(.3)
                pydirectinput.keyUp(key)
            else:
                pydirectinput.keyDown(key)
                time.sleep(duration)
                pydirectinput.keyUp(key)


    def key_hold(self, key, duration=None):

        key = self.map_key(key)

        # Hack for GPT-4V tendency to specify unnecessary duration
        # if duration == 2:
        #    duration = None

        f, keys = self._check_multi_key(key)
        if f == True:
            self._multi_key_action(keys, self.ACTION_HOLD, duration)
        else:

            if duration is not None:
                pydirectinput.keyDown(key)
                time.sleep(duration)
                pydirectinput.keyUp(key)
            else:
                self.put_held_keys(key)


    def key_release(self, key):

        key = self.map_key(key)

        self.pop_held_keys(key)


    def release_held_keys(self):
        # logger.warn(f'Releasing all held keys: {self.held_keys}')
        for i in range(len(self.held_keys)):
            self.held_keys.pop()


    def release_held_buttons(self):
        # logger.warn(f'Releasing all held buttons: {self.held_buttons}')
        for i in range(len(self.held_buttons)):
            self._mouse_button_up(self.held_buttons[i][self.BUTTON_KEY])


    # @TODO mapping can be improved
    def map_button(self, button):

        if button is None or button == '':
            logger.error('Empty Button.')
            raise Exception(f'Empty mouse button IO: {button}')

        if len(button) > 1:
            button = button.lower().replace('_', '').replace(' ', '')

        if button in ['right', 'rightbutton', 'rightmousebutton', 'r', 'rbutton', 'rmouse', 'rightmouse']:
            return self.RIGHT_MOUSE_BUTTON
        elif button in ['left', 'leftbutton', 'leftmousebutton', 'l', 'lbutton', 'lmouse', 'leftmouse']:
            return self.LEFT_MOUSE_BUTTON
        elif button in ['middle', 'middelbutton', 'middlemousebutton', 'm', 'mbutton', 'mmouse', 'middlemouse', 'center', 'centerbutton', 'centermouse']:
            return self.MIDDLE_MOUSE_BUTTON

        return button


    # @TODO mapping can be improved
    def map_key(self, key):

        if key is None or key == '':
            logger.error('Empty key.')
            raise Exception(f'Empty key IO: {key}')

        if len(key) > 1:
            key = key.lower().replace('_', '').replace('-', '')

        if key in ['lshift', 'left shift', 'leftshift', 'shift left', 'shiftleft']:
            return 'shift'
        elif key in ['rshift', 'right shift', 'rightshift', 'shift right', 'shiftright']:
            return 'shift'

        if key in ['lalt', 'left alt', 'leftalt', 'alt left', 'altleft']:
            return 'alt'
        elif key in ['ralt', 'right alt', 'rightalt', 'alt right', 'altright']:
            return 'alt'

        if key in ['lctrl', 'left ctrl', 'leftctrl', 'ctrl left', 'ctrlleft', 'lcontrol', 'left control', 'leftcontrol', 'control left', 'contorlleft']:
            return 'ctrl'
        elif key in ['rctrl', 'right ctrl', 'rightctrl', 'ctrl right', 'ctrlright', 'rcontrol', 'right control', 'rightcontrol', 'control right', 'contorlright']:
            return 'ctrl'

        if key in [' ', 'whitespace', 'spacebar', 'space bar']:
            return 'space'

        return key


def _theta_calculation(theta):
    """
    Calculates the adjusted theta value based on the configured mouse move factor.

    Parameters:
    - theta: The original theta value to be adjusted.
    """
    return theta * config.mouse_move_factor


def _safe_list_get(list, idx, key = None, default = None):
    try:
        return list[idx][key]
    except IndexError:
        return default
