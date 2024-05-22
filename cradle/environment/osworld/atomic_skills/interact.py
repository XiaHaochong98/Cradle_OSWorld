# from cradle.config import Config
# from cradle.gameio.lifecycle.ui_control import switch_to_game
# from cradle.log import Logger
# from cradle.gameio import IOEnvironment
# from cradle.environment.feishu.skill_registry import register_skill, post_skill_wait
# import pyautogui
# config = Config()
# logger = Logger()
# io_env = IOEnvironment()
#
# @register_skill("move_to_position")
# def move_to_position(x, y):
#     """
#     Move the cursor to the specified position (x, y).
#
#     Parameters:
#     - x: The x-coordinate of the position to move the cursor to. Must be within the screen width range.
#     - y: The y-coordinate of the position to move the cursor to. Must be within the screen height range.
#     """
#     screen_width, screen_height = pyautogui.size()
#
#     if not (0 <= x <= screen_width):
#         raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")
#
#     if not (0 <= y <= screen_height):
#         raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")
#
#     pyautogui.moveTo(x, y)
#
# @register_skill("click")
# def click(button='left', x=None, y=None, num_clicks=1):
#     """
#     Click the specified mouse button at the given position.
#
#     Parameters:
#     - button: The button to click ('left', 'right', 'middle'). Defaults to 'left'.
#     - x: The x-coordinate to click at. Must be within the screen width range.
#     - y: The y-coordinate to click at. Must be within the screen height range.
#     - num_clicks: The number of times to click. Defaults to 1. Must be 1, 2, or 3.
#     """
#     if button not in ['left', 'right', 'middle']:
#         raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")
#
#     if num_clicks not in [1, 2, 3]:
#         raise ValueError(f"Invalid num_clicks '{num_clicks}'. Must be 1, 2, or 3.")
#
#     if x is not None and y is not None:
#         screen_width, screen_height = pyautogui.size()
#
#         if not (0 <= x <= screen_width):
#             raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")
#
#         if not (0 <= y <= screen_height):
#             raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")
#
#         pyautogui.click(x=x, y=y, button=button, clicks=num_clicks)
#     else:
#         pyautogui.click(button=button, clicks=num_clicks)
#
# @register_skill("mouse_down")
# def mouse_down(button='left'):
#     """
#     Press the specified mouse button.
#
#     Parameters:
#     - button: The button to press ('left', 'right', 'middle'). Defaults to 'left'.
#     """
#
#     if button not in ['left', 'right', 'middle']:
#         raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")
#
#     pyautogui.mouseDown(button=button)
#
# @register_skill("mouse_up")
# def mouse_up(button='left'):
#     """
#     Release the specified mouse button.
#
#     Parameters:
#     - button: The button to release ('left', 'right', 'middle'). Defaults to 'left'.
#     """
#     if button not in ['left', 'right', 'middle']:
#         raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")
#
#     pyautogui.mouseUp(button=button)
#
# @register_skill("right_click")
# def right_click(x=None, y=None):
#     """
#     Right-click at the specified position, or at the current position if no coordinates are provided.
#
#     Parameters:
#     -x : The x-coordinate to right-click at. Must be within the screen width range.
#     -y : The y-coordinate to right-click at. Must be within the screen height range.
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
#
# @register_skill("double_click")
# def double_click(x=None, y=None):
#     """
#     Double-click at the specified position, or at the current position if no coordinates are provided.
#
#     Parameters:
#     - x: The x-coordinate to double-click at. Must be within the screen width range.
#     - y: The y-coordinate to double-click at. Must be within the screen height range.
#     """
#     if x is not None and y is not None:
#         screen_width, screen_height = pyautogui.size()
#
#         if not (0 <= x <= screen_width):
#             raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")
#
#         if not (0 <= y <= screen_height):
#             raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")
#         pyautogui.doubleClick(x=x, y=y)
#     else:
#         pyautogui.doubleClick()
#
# @register_skill("drag_to_position")
# def drag_to_position(x, y):
#     """
#     Drag the cursor to the specified position (x, y) with the left button pressed.
#
#     Parameters:
#     - x: The x-coordinate of the position to drag the cursor to. Must be within the screen width range.
#     - y: The y-coordinate of the position to drag the cursor to. Must be within the screen height range.
#     """
#     screen_width, screen_height = pyautogui.size()
#
#     if not (0 <= x <= screen_width):
#         raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")
#
#     if not (0 <= y <= screen_height):
#         raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")
#
#     pyautogui.dragTo(x, y, button='left')
#
# @register_skill("scroll")
# def scroll(dx, dy):
#     """
#     Scroll the mouse wheel up or down.
#
#     Parameters:
#     - dx: The horizontal scroll amount. Positive values scroll right, negative values scroll left.
#     - dy: The vertical scroll amount. Positive values scroll up, negative values scroll down.
#     """
#     if dx != 0:
#         pyautogui.hscroll(dx)
#
#     if dy != 0:
#         pyautogui.scroll(dy)
#
# @register_skill("type_text")
# def type_text(text):
#     """
#     Type the specified text.
#
#     Parameters:
#     - text: The text to type.
#     """
#     if not isinstance(text, str):
#         raise ValueError(f"text must be a string, got {type(text)} instead.")
#
#     pyautogui.typewrite(text)
#
# @register_skill("press_key")
# def press_key(key):
#     """
#     Press the specified key and release it.
#
#     Parameters:
#     - key: The key to press and release. Must be a valid keyboard key.
#     """
#     if not isinstance(key, str):
#         raise ValueError(f"key must be a string, got {type(key)} instead.")
#
#     valid_keys = pyautogui.KEYBOARD_KEYS
#     if key not in valid_keys:
#         raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")
#
#     pyautogui.press(key)
#
# @register_skill("key_down")
# def key_down(key):
#     """
#     Press (hold down) the specified key.
#
#     Parameters:
#     - key: The key to press. Must be a valid keyboard key.
#     """
#     if not isinstance(key, str):
#         raise ValueError(f"key must be a string, got {type(key)} instead.")
#
#     valid_keys = pyautogui.KEYBOARD_KEYS
#     if key not in valid_keys:
#         raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")
#
#     pyautogui.keyDown(key)
#
# @register_skill("key_up")
# def key_up(key):
#     """
#     Release the specified key.
#
#     Parameters:
#     - key: The key to release. Must be a valid keyboard key.
#     """
#     if not isinstance(key, str):
#         raise ValueError(f"key must be a string, got {type(key)} instead.")
#
#     valid_keys = pyautogui.KEYBOARD_KEYS
#     if key not in valid_keys:
#         raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")
#
#     pyautogui.keyUp(key)
#
# @register_skill("press_hotkey")
# def press_hotkey(keys):
#     """
#     Press the specified key combination.
#
#     Parameters:
#     - keys: The keys to press in combination. Each key must be a valid keyboard key.
#     """
#     if not isinstance(keys, list):
#         raise ValueError(f"keys must be a list, got {type(keys)} instead.")
#
#     valid_keys = pyautogui.KEYBOARD_KEYS
#
#     for key in keys:
#         if not isinstance(key, str):
#             raise ValueError(f"Each key must be a string, got {type(key)} instead.")
#         if key not in valid_keys:
#             raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")
#
#     pyautogui.hotkey(*keys)
#
#
# __all__ = [
#     "move_to_position",
#     "click",
#     "mouse_down",
#     "mouse_up",
#     "right_click",
#     "double_click",
#     "drag_to_position",
#     "scroll",
#     "type_text",
#     "press_key",
#     "key_down",
#     "key_up",
#     "press_hotkey",
# ]


from cradle.config import Config
from cradle.gameio.lifecycle.ui_control import switch_to_game
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.environment.outlook.skill_registry import register_skill, post_skill_wait
import pyautogui
config = Config()
logger = Logger()
io_env = IOEnvironment()

# @register_skill("move_to_position")
# def move_to_position(x, y):
#     """
#     Move the cursor to the specified position (x, y).
#
#     Parameters:
#     - x: The x-coordinate of the position to move the cursor to. Must be within the screen width range.
#     - y: The y-coordinate of the position to move the cursor to. Must be within the screen height range.
#     """
#     screen_width, screen_height = pyautogui.size()
#
#     if not (0 <= x <= screen_width):
#         raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")
#
#     if not (0 <= y <= screen_height):
#         raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")
#
#     pyautogui.moveTo(x, y)

# @register_skill("click")
# def click(button='left', x=None, y=None, num_clicks=1):
#     """
#     Click the specified mouse button at the given position.
#
#     Parameters:
#     - button: The button to click ('left', 'right', 'middle'). Defaults to 'left'.
#     - x: The x-coordinate to click at. Must be within the screen width range.
#     - y: The y-coordinate to click at. Must be within the screen height range.
#     - num_clicks: The number of times to click. Defaults to 1. Must be 1, 2, or 3.
#     """
#     if button not in ['left', 'right', 'middle']:
#         raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")
#
#     if num_clicks not in [1, 2, 3]:
#         raise ValueError(f"Invalid num_clicks '{num_clicks}'. Must be 1, 2, or 3.")
#
#     if x is not None and y is not None:
#         screen_width, screen_height = pyautogui.size()
#
#         if not (0 <= x <= screen_width):
#             raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")
#
#         if not (0 <= y <= screen_height):
#             raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")
#
#         pyautogui.click(x=x, y=y, button=button, clicks=num_clicks)
#     else:
#         pyautogui.click(button=button, clicks=num_clicks)
#
# @register_skill("mouse_down")
# def mouse_down(button='left'):
#     """
#     Press the specified mouse button.
#
#     Parameters:
#     - button: The button to press ('left', 'right', 'middle'). Defaults to 'left'.
#     """
#
#     if button not in ['left', 'right', 'middle']:
#         raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")
#
#     pyautogui.mouseDown(button=button)
#
# @register_skill("mouse_up")
# def mouse_up(button='left'):
#     """
#     Release the specified mouse button.
#
#     Parameters:
#     - button: The button to release ('left', 'right', 'middle'). Defaults to 'left'.
#     """
#     if button not in ['left', 'right', 'middle']:
#         raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")
#
#     pyautogui.mouseUp(button=button)
#
# @register_skill("right_click")
# def right_click(x=None, y=None):
#     """
#     Right-click at the specified position, or at the current position if no coordinates are provided.
#
#     Parameters:
#     -x : The x-coordinate to right-click at. Must be within the screen width range.
#     -y : The y-coordinate to right-click at. Must be within the screen height range.
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
#
# @register_skill("double_click")
# def double_click(x=None, y=None):
#     """
#     Double-click at the specified position, or at the current position if no coordinates are provided.
#
#     Parameters:
#     - x: The x-coordinate to double-click at. Must be within the screen width range.
#     - y: The y-coordinate to double-click at. Must be within the screen height range.
#     """
#     if x is not None and y is not None:
#         screen_width, screen_height = pyautogui.size()
#
#         if not (0 <= x <= screen_width):
#             raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")
#
#         if not (0 <= y <= screen_height):
#             raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")
#         pyautogui.doubleClick(x=x, y=y)
#     else:
#         pyautogui.doubleClick()
#
# @register_skill("drag_to_position")
# def drag_to_position(x, y):
#     """
#     Drag the cursor to the specified position (x, y) with the left button pressed.
#
#     Parameters:
#     - x: The x-coordinate of the position to drag the cursor to. Must be within the screen width range.
#     - y: The y-coordinate of the position to drag the cursor to. Must be within the screen height range.
#     """
#     screen_width, screen_height = pyautogui.size()
#
#     if not (0 <= x <= screen_width):
#         raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")
#
#     if not (0 <= y <= screen_height):
#         raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")
#
#     pyautogui.dragTo(x, y, button='left')
#
# @register_skill("scroll")
# def scroll(dx, dy):
#     """
#     Scroll the mouse wheel up or down.
#
#     Parameters:
#     - dx: The horizontal scroll amount. Positive values scroll right, negative values scroll left.
#     - dy: The vertical scroll amount. Positive values scroll up, negative values scroll down.
#     """
#     if dx != 0:
#         pyautogui.hscroll(dx)
#
#     if dy != 0:
#         pyautogui.scroll(dy)
#
# @register_skill("type_text")
# def type_text(text):
#     """
#     Type the specified text.
#
#     Parameters:
#     - text: The text to type.
#     """
#     if not isinstance(text, str):
#         raise ValueError(f"text must be a string, got {type(text)} instead.")
#
#     pyautogui.typewrite(text)
#
# @register_skill("press_key")
# def press_key(key):
#     """
#     Press the specified key and release it.
#
#     Parameters:
#     - key: The key to press and release. Must be a valid keyboard key.
#     """
#     if not isinstance(key, str):
#         raise ValueError(f"key must be a string, got {type(key)} instead.")
#
#     valid_keys = pyautogui.KEYBOARD_KEYS
#     if key not in valid_keys:
#         raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")
#
#     pyautogui.press(key)
#
# @register_skill("key_down")
# def key_down(key):
#     """
#     Press (hold down) the specified key.
#
#     Parameters:
#     - key: The key to press. Must be a valid keyboard key.
#     """
#     if not isinstance(key, str):
#         raise ValueError(f"key must be a string, got {type(key)} instead.")
#
#     valid_keys = pyautogui.KEYBOARD_KEYS
#     if key not in valid_keys:
#         raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")
#
#     pyautogui.keyDown(key)
#
# @register_skill("key_up")
# def key_up(key):
#     """
#     Release the specified key.
#
#     Parameters:
#     - key: The key to release. Must be a valid keyboard key.
#     """
#     if not isinstance(key, str):
#         raise ValueError(f"key must be a string, got {type(key)} instead.")
#
#     valid_keys = pyautogui.KEYBOARD_KEYS
#     if key not in valid_keys:
#         raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")
#
#     pyautogui.keyUp(key)
#
# @register_skill("press_hotkey")
# def press_hotkey(keys):
#     """
#     Press the specified key combination.
#
#     Parameters:
#     - keys: The keys to press in combination. Each key must be a valid keyboard key.
#     """
#     if not isinstance(keys, list):
#         raise ValueError(f"keys must be a list, got {type(keys)} instead.")
#
#     valid_keys = pyautogui.KEYBOARD_KEYS
#
#     for key in keys:
#         if not isinstance(key, str):
#             raise ValueError(f"Each key must be a string, got {type(key)} instead.")
#         if key not in valid_keys:
#             raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")
#
#     pyautogui.hotkey(*keys)


# __all__ = [
#     # "move_to_position",
#     # "click",
#     # "mouse_down",
#     # "mouse_up",
#     # "right_click",
#     # "double_click",
#     # "drag_to_position",
#     # "scroll",
#     # "type_text",
#     # "press_key",
#     # "key_down",
#     # "key_up",
#     # "press_hotkey",
# ]



@register_skill("click_at_position")
def click_at_position(x, y, mouse_button):
    """
    Moves the mouse to the specified x, y corrdinates inside the application window and clicks at that position.

    Parameters:
    - x: The normalized x-coordinate of the target position. The value should be between 0 and 1.
    - y: The normalized y-coordinate of the target position. The value should be between 0 and 1.
    - mouse_button: The mouse button to be clicked. It should be one of the following values: "left", "right", "middle".
    """
    screen_width, screen_height = pyautogui.size()

    if not (0 <= x <= screen_width):
        raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")

    if not (0 <= y <= screen_height):
        raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")

    pyautogui.moveTo(x, y)


@register_skill("move_mouse_to_position")
def move_mouse_to_position(x, y):
    """
    Moves the mouse to the specified x, y corrdinates inside the application window.

    Parameters:
    - x: The normalized x-coordinate of the target position. The value should be between 0 and 1.
    - y: The normalized y-coordinate of the target position. The value should be between 0 and 1.
    """
    io_env.mouse_move_normalized(x, y)

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("mouse_drag")
def mouse_drag(source_x, source_y, target_x, target_y, mouse_button):
    """
    Use the mouse to drag from a source position to a target position. The type of drag depends on the mouse button used.
    The mouse is moved to the source x, y position, the button is pressed, the mouse is moved to the target x, y position, and the button is released.

    Parameters:
    - source_x: The normalized x-coordinate of the source position. The value should be between 0 and 1.
    - source_y: The normalized y-coordinate of the soruce position. The value should be between 0 and 1.
    - target_x: The normalized x-coordinate of the target position. The value should be between 0 and 1.
    - target_y: The normalized y-coordinate of the target position. The value should be between 0 and 1.
    - mouse_button: The mouse button to be clicked. It should be one of the following values: "left", "right", "middle".
    """
    io_env.mouse_move_normalized(source_x, source_y)
    io_env.mouse_click_button(mouse_button)
    io_env.mouse_move_normalized(target_x, target_y)
    io_env.mouse_release_button(mouse_button)

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("press_key")
def press_key(key):
    """
    Pressing the selected key in the current situation.

    Parameters:
    - key: A keyboard key to be pressed. For example, press the 'enter' key.
    """
    io_env.key_press(key)


@register_skill("press_keys_combined")
def press_keys_combined(keys):
    """
    Presses the keys in the list combined. For example, when pressing the shortcut or hotkey combination 'ctrl' + P.

    Parameters:
    - keys: List of keys to press together at the same time. Either list of key names, or a string of comma-separated key names.
    """
    io_env.key_press(keys)


@register_skill("type_text")
def type_text(text):
    """
    Types the specified text using the keyboard. One character at a time.

    Parameters:
    - text: The text to be typed into the current UI control.
    """
    io_env.keys_type(text)

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("go_back_to_target_application")
def go_back_to_target_application():
    """
    This function can be used to return to the target application, if some previous action opened a different application.
    """
    switch_to_game()

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)
    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


__all__ = [
    "go_back_to_target_application",
    "click_at_position",
    "move_mouse_to_position",
    "mouse_drag",
    "press_key",
    "press_keys_combined",
    "type_text",
]
