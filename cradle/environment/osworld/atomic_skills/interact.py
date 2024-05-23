from cradle.config import Config
from cradle.gameio.lifecycle.ui_control import switch_to_game
from cradle.log import Logger
from cradle.gameio import IOEnvironment
# from cradle.environment.feishu.skill_registry import register_skill, post_skill_wait
from cradle.environment.osworld.skill_registry import register_skill
import pyautogui
config = Config()
logger = Logger()
io_env = IOEnvironment()

@register_skill("move_mouse_to_position")
def move_mouse_to_position(x, y):
    """
    Move the cursor to the specified position (x, y).

    Parameters:
    - x: The x-coordinate of the position to move the cursor to. Must be within the screen width range.
    - y: The y-coordinate of the position to move the cursor to. Must be within the screen height range.
    """
    screen_width, screen_height = pyautogui.size()

    if not (0 <= x <= screen_width):
        raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")

    if not (0 <= y <= screen_height):
        raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")

    pyautogui.moveTo(x, y)

@register_skill("click_at_position")
def click_at_position(button='left', x=None, y=None, num_clicks=1):
    """
    Click the specified mouse button at the given position.

    Parameters:
    - button: The button to click ('left', 'right', 'middle'). Defaults to 'left'.
    - x: The x-coordinate to click at. Must be within the screen width range.
    - y: The y-coordinate to click at. Must be within the screen height range.
    - num_clicks: The number of times to click. Defaults to 1. Must be 1, 2, or 3.
    """
    if button not in ['left', 'right', 'middle']:
        raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")

    if num_clicks not in [1, 2, 3]:
        raise ValueError(f"Invalid num_clicks '{num_clicks}'. Must be 1, 2, or 3.")

    if x is not None and y is not None:
        screen_width, screen_height = pyautogui.size()

        if not (0 <= x <= screen_width):
            raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")

        if not (0 <= y <= screen_height):
            raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")

        pyautogui.click(x=x, y=y, button=button, clicks=num_clicks)
    else:
        pyautogui.click(button=button, clicks=num_clicks)

@register_skill("mouse_down")
def mouse_down(button='left'):
    """
    Press the specified mouse button.

    Parameters:
    - button: The button to press ('left', 'right', 'middle'). Defaults to 'left'.
    """

    if button not in ['left', 'right', 'middle']:
        raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")

    pyautogui.mouseDown(button=button)

@register_skill("mouse_up")
def mouse_up(button='left'):
    """
    Release the specified mouse button.

    Parameters:
    - button: The button to release ('left', 'right', 'middle'). Defaults to 'left'.
    """
    if button not in ['left', 'right', 'middle']:
        raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")

    pyautogui.mouseUp(button=button)

# @register_skill("right_click")
# def right_click(x=None, y=None):
#     """
#     Right-click at the specified position, or at the current position if no coordinates are provided.
#
#     Parameters:
#     - x: The x-coordinate to right-click at. Must be within the screen width range.
#     - y: The y-coordinate to right-click at. Must be within the screen height range.
#     """
#     if x is not None and y is not None:
#         screen_width, screen_height = pyautogui.size()
#
#         if not (0 <= x <= screen_width):
#             raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")
#
#         if not (0 <= y <= screen_height):
#             raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")
#
#         pyautogui.rightClick(x=x, y=y)
#     else:
#         pyautogui.rightClick()

@register_skill("double_click_at_position")
def double_click_at_position(x=None, y=None):
    """
    Double-click at the specified position, or at the current position if no coordinates are provided.

    Parameters:
    - x: The x-coordinate to double-click at. Must be within the screen width range.
    - y: The y-coordinate to double-click at. Must be within the screen height range.
    """
    if x is not None and y is not None:
        screen_width, screen_height = pyautogui.size()

        if not (0 <= x <= screen_width):
            raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")

        if not (0 <= y <= screen_height):
            raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")
        pyautogui.doubleClick(x=x, y=y)
    else:
        pyautogui.doubleClick()

@register_skill("mouse_drag")
def mouse_drag(x, y):
    """
    Drag the cursor to the specified position (x, y) with the left button pressed.

    Parameters:
    - x: The x-coordinate of the position to drag the cursor to. Must be within the screen width range.
    - y: The y-coordinate of the position to drag the cursor to. Must be within the screen height range.
    """
    screen_width, screen_height = pyautogui.size()

    if not (0 <= x <= screen_width):
        raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")

    if not (0 <= y <= screen_height):
        raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")

    pyautogui.dragTo(x, y, button='left')

@register_skill("scroll")
def scroll(dx, dy):
    """
    Scroll the mouse wheel up or down.

    Parameters:
    - dx: The horizontal scroll amount. Positive values scroll right, negative values scroll left.
    - dy: The vertical scroll amount. Positive values scroll up, negative values scroll down.
    """
    if dx != 0:
        pyautogui.hscroll(dx)

    if dy != 0:
        pyautogui.scroll(dy)

@register_skill("type_text")
def type_text(text):
    """
    Type the specified text.

    Parameters:
    - text: The text to type.
    """
    if not isinstance(text, str):
        raise ValueError(f"text must be a string, got {type(text)} instead.")

    pyautogui.typewrite(text)

@register_skill("press_key")
def press_key(key):
    """
    Press the specified key and release it.

    Parameters:
    - key: The key to press and release. Must be a valid keyboard key.
    """
    if not isinstance(key, str):
        raise ValueError(f"key must be a string, got {type(key)} instead.")

    valid_keys = pyautogui.KEYBOARD_KEYS
    if key not in valid_keys:
        raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")

    pyautogui.press(key)

@register_skill("key_down")
def key_down(key):
    """
    Press (hold down) the specified key.

    Parameters:
    - key: The key to press. Must be a valid keyboard key.
    """
    if not isinstance(key, str):
        raise ValueError(f"key must be a string, got {type(key)} instead.")

    valid_keys = pyautogui.KEYBOARD_KEYS
    if key not in valid_keys:
        raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")

    pyautogui.keyDown(key)

@register_skill("key_up")
def key_up(key):
    """
    Release the specified key.

    Parameters:
    - key: The key to release. Must be a valid keyboard key.
    """
    if not isinstance(key, str):
        raise ValueError(f"key must be a string, got {type(key)} instead.")

    valid_keys = pyautogui.KEYBOARD_KEYS
    if key not in valid_keys:
        raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")

    pyautogui.keyUp(key)

@register_skill("press_hotkey")
def press_hotkey(keys):
    """
    Press the specified key combination.

    Parameters:
    - keys: The keys to press in combination. Each key must be a valid keyboard key.
    """
    if not isinstance(keys, list):
        raise ValueError(f"keys must be a list, got {type(keys)} instead.")

    valid_keys = pyautogui.KEYBOARD_KEYS

    for key in keys:
        if not isinstance(key, str):
            raise ValueError(f"Each key must be a string, got {type(key)} instead.")
        if key not in valid_keys:
            raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")

    pyautogui.hotkey(*keys)


__all__ = [
    # "move_mouse_to_position",
    # "click_at_position",
    "mouse_down",
    "mouse_up",
    # "right_click",
    # "double_click_at_position",
    # "mouse_drag",
    "scroll",
    "type_text",
    "press_key",
    "key_down",
    "key_up",
    "press_hotkey",
]