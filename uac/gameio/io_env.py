import os
import time
import ctypes

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

    MAX_ITERATIONS = 3

    KEY_KEY = 'key'
    EXPIRATION_KEY = 'expiration'

    # Key actions
    # All key interactions are now tracked and use the same calling structure
    # - Release is equivalent to keyUp. I.e., release a key that was pressed or held.
    # - Hold is equivalent to keyDown. I.e., hold a key for a certain duration, probably while something else happens.
    # - Press is equivalent to keyDown followed by keyUp, after a delay. I.e., press a key for a short duration.
    ACTION_PRESS = 'press'
    ACTION_HOLD = 'hold'
    ACTION_RELEASE = 'release'

    # List of keys currently held. To be either released by specific calls or after timeout (max iterations).
    held_keys = []


    def __init__(self) -> None:
        """Initialize the IO environment class"""
        self.ahk = AHK()


    def pop_held_keys(self, key):

        if self.check_held_keys(keys = [key]):
            pydirectinput.keyUp(key)
            time.sleep(0.5)
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


    def check_held_keys(self, keys = ['tab', 'b']):

        result = False

        for e in self.held_keys:
            k = e[self.KEY_KEY]
            if k in keys:
                result = True
                break

        return result


    def _to_message(self, list, purpose):

        vals = ', '.join(f'{e[self.KEY_KEY]}:{e[self.EXPIRATION_KEY]}' for e in list)
        msg = f'Held keys after {purpose}: {vals}'

        # @TODO change to debug
        logger.write(msg)

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


    def list_session_screenshots(self, session_dir: str = config.work_dir):

        # List all files in dir starting with "screen"
        screenshots = [f for f in os.listdir(session_dir) if os.path.isfile(os.path.join(session_dir, f)) and f.startswith("screen")]

        # Sort list by creation time
        screenshots.sort(key=lambda x: os.path.getctime(os.path.join(session_dir, x)))

        return screenshots


    def mouse_move_normalized(self, x, y):
        x = int(x*config.game_resolution[0] - config.game_resolution[0] / 2)
        y = int(y*config.game_resolution[1] - config.game_resolution[1] / 2)
        self.mouse_move(x, y)


    def mouse_move(self, x, y):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(x, y, 0, 0x0001, 0, ctypes.pointer(extra))

        command = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))


    def mouse_move_horizontal_angle(self, theta):
        distance = _theta_calculation(theta)
        self.ahk.mouse_move(distance, 0, speed=100, relative=True)


    def mouse_click_button(self, button, clicks=1):
        self.ahk.click(click_count=clicks, button=button, relative=False)


    def mouse_click_button_and_hold(self, button):
        pyautogui.mouseDown(button=button)


    def mouse_release_button(self, button):
        pyautogui.mouseUp(button=button)


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
        logger.warn(f'Releasing all held keys: {self.held_keys}')
        for i in range(len(self.held_keys)):
            self.held_keys.pop()


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
