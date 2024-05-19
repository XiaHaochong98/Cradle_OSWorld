import pyautogui


def move_to_position(x, y):
    """
    Move the cursor to the specified position (x, y).

    Parameters:
    x (float): The x-coordinate of the position to move the cursor to. Must be within the screen width range.
    y (float): The y-coordinate of the position to move the cursor to. Must be within the screen height range.

    Returns:
    None
    """
    # Check if the provided coordinates are within the valid range of the screen size
    screen_width, screen_height = pyautogui.size()

    if not (0 <= x <= screen_width):
        raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")

    if not (0 <= y <= screen_height):
        raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")

    # Move the cursor to the specified position
    pyautogui.moveTo(x, y)


def click(button='left', x=None, y=None, num_clicks=1):
    """
    Click the specified mouse button at the given position.

    Parameters:
    button (str): The button to click ('left', 'right', 'middle'). Defaults to 'left'.
    x (float, optional): The x-coordinate to click at. Must be within the screen width range.
    y (float, optional): The y-coordinate to click at. Must be within the screen height range.
    num_clicks (int, optional): The number of times to click. Defaults to 1. Must be 1, 2, or 3.

    Returns:
    None
    """
    # Validate button
    if button not in ['left', 'right', 'middle']:
        raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")

    # Validate num_clicks
    if num_clicks not in [1, 2, 3]:
        raise ValueError(f"Invalid num_clicks '{num_clicks}'. Must be 1, 2, or 3.")

    # Check if x and y are provided and valid
    if x is not None and y is not None:
        screen_width, screen_height = pyautogui.size()

        if not (0 <= x <= screen_width):
            raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")

        if not (0 <= y <= screen_height):
            raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")

        # Click at the specified position
        pyautogui.click(x=x, y=y, button=button, clicks=num_clicks)
    else:
        # Click at the current position
        pyautogui.click(button=button, clicks=num_clicks)


def mouse_down(button='left'):
    """
    Press the specified mouse button.

    Parameters:
    button (str): The button to press ('left', 'right', 'middle'). Defaults to 'left'.

    Returns:
    None
    """
    # Validate button
    if button not in ['left', 'right', 'middle']:
        raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")

    # Press the specified mouse button
    pyautogui.mouseDown(button=button)


def mouse_up(button='left'):
    """
    Release the specified mouse button.

    Parameters:
    button (str): The button to release ('left', 'right', 'middle'). Defaults to 'left'.

    Returns:
    None
    """
    # Validate button
    if button not in ['left', 'right', 'middle']:
        raise ValueError(f"Invalid button '{button}'. Must be 'left', 'right', or 'middle'.")

    # Release the specified mouse button
    pyautogui.mouseUp(button=button)


def right_click(x=None, y=None):
    """
    Right-click at the specified position, or at the current position if no coordinates are provided.

    Parameters:
    x (float, optional): The x-coordinate to right-click at. Must be within the screen width range.
    y (float, optional): The y-coordinate to right-click at. Must be within the screen height range.

    Returns:
    None
    """
    # Check if x and y are provided and valid
    if x is not None and y is not None:
        screen_width, screen_height = pyautogui.size()

        if not (0 <= x <= screen_width):
            raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")

        if not (0 <= y <= screen_height):
            raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")

        # Right-click at the specified position
        pyautogui.rightClick(x=x, y=y)
    else:
        # Right-click at the current position
        pyautogui.rightClick()


def double_click(x=None, y=None):
    """
    Double-click at the specified position, or at the current position if no coordinates are provided.

    Parameters:
    x (float, optional): The x-coordinate to double-click at. Must be within the screen width range.
    y (float, optional): The y-coordinate to double-click at. Must be within the screen height range.

    Returns:
    None
    """
    # Check if x and y are provided and valid
    if x is not None and y is not None:
        screen_width, screen_height = pyautogui.size()

        if not (0 <= x <= screen_width):
            raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")

        if not (0 <= y <= screen_height):
            raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")

        # Double-click at the specified position
        pyautogui.doubleClick(x=x, y=y)
    else:
        # Double-click at the current position
        pyautogui.doubleClick()


def drag_to_position(x, y):
    """
    Drag the cursor to the specified position (x, y) with the left button pressed.

    Parameters:
    x (float): The x-coordinate of the position to drag the cursor to. Must be within the screen width range.
    y (float): The y-coordinate of the position to drag the cursor to. Must be within the screen height range.

    Returns:
    None
    """
    # Check if the provided coordinates are within the valid range of the screen size
    screen_width, screen_height = pyautogui.size()

    if not (0 <= x <= screen_width):
        raise ValueError(f"x-coordinate {x} is out of range. It should be between 0 and {screen_width}.")

    if not (0 <= y <= screen_height):
        raise ValueError(f"y-coordinate {y} is out of range. It should be between 0 and {screen_height}.")

    # Drag the cursor to the specified position with the left button pressed
    pyautogui.dragTo(x, y, button='left')


def scroll(dx, dy):
    """
    Scroll the mouse wheel up or down.

    Parameters:
    dx (int): The horizontal scroll amount. Positive values scroll right, negative values scroll left.
    dy (int): The vertical scroll amount. Positive values scroll up, negative values scroll down.

    Returns:
    None
    """
    # Scroll horizontally
    if dx != 0:
        pyautogui.hscroll(dx)

    # Scroll vertically
    if dy != 0:
        pyautogui.scroll(dy)


def type_text(text):
    """
    Type the specified text.

    Parameters:
    text (str): The text to type.

    Returns:
    None
    """
    if not isinstance(text, str):
        raise ValueError(f"text must be a string, got {type(text)} instead.")

    # Type the specified text
    pyautogui.typewrite(text)


def press_key(key):
    """
    Press the specified key and release it.

    Parameters:
    key (str): The key to press and release. Must be a valid keyboard key.

    Returns:
    None
    """
    if not isinstance(key, str):
        raise ValueError(f"key must be a string, got {type(key)} instead.")

    # List of valid keyboard keys can be obtained from pyautogui.KEYBOARD_KEYS
    valid_keys = pyautogui.KEYBOARD_KEYS
    if key not in valid_keys:
        raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")

    # Press and release the specified key
    pyautogui.press(key)


def key_down(key):
    """
    Press (hold down) the specified key.

    Parameters:
    key (str): The key to press. Must be a valid keyboard key.

    Returns:
    None
    """
    if not isinstance(key, str):
        raise ValueError(f"key must be a string, got {type(key)} instead.")

    # List of valid keyboard keys can be obtained from pyautogui.KEYBOARD_KEYS
    valid_keys = pyautogui.KEYBOARD_KEYS
    if key not in valid_keys:
        raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")

    # Press the specified key
    pyautogui.keyDown(key)


def key_up(key):
    """
    Release the specified key.

    Parameters:
    key (str): The key to release. Must be a valid keyboard key.

    Returns:
    None
    """
    if not isinstance(key, str):
        raise ValueError(f"key must be a string, got {type(key)} instead.")

    # List of valid keyboard keys can be obtained from pyautogui.KEYBOARD_KEYS
    valid_keys = pyautogui.KEYBOARD_KEYS
    if key not in valid_keys:
        raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")

    # Release the specified key
    pyautogui.keyUp(key)


def press_hotkey(keys):
    """
    Press the specified key combination.

    Parameters:
    keys (list of str): The keys to press in combination. Each key must be a valid keyboard key.

    Returns:
    None
    """
    if not isinstance(keys, list):
        raise ValueError(f"keys must be a list, got {type(keys)} instead.")

    # List of valid keyboard keys can be obtained from pyautogui.KEYBOARD_KEYS
    valid_keys = pyautogui.KEYBOARD_KEYS

    for key in keys:
        if not isinstance(key, str):
            raise ValueError(f"Each key must be a string, got {type(key)} instead.")
        if key not in valid_keys:
            raise ValueError(f"'{key}' is not a valid key. Valid keys are: {valid_keys}")

    # Press the specified key combination
    pyautogui.hotkey(*keys)
