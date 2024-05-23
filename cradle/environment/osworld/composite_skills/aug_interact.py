from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.environment.osworld.skill_registry import register_skill, post_skill_wait
from cradle.environment.osworld.atomic_skills.interact import click_at_position,move_mouse_to_position
from cradle.provider.sam_provider import SamProvider
import pyautogui

config = Config()
logger = Logger()
io_env = IOEnvironment()
sam_provider = SamProvider()


@register_skill("click_on_label")
def click_on_label(label_id, mouse_button):
    """
    Moves the mouse to the position of the specified box id inside the application window and clicks.

    Parameters:
    - label_id: The numerical label id of the bounding box to click at.
    - mouse_button: The mouse button to be clicked. It should be one of the following values: "left", "right", "middle".
    """
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

    label_id = str(label_id)
    x, y = 0.5, 0.5
    click_at_position(x, y, mouse_button)

@register_skill("double_click_on_label")
def double_click_on_label(label_id, mouse_button):
    """
    Moves the mouse to the position of the specified box id inside the application window and clicks.

    Parameters:
    - label_id: The numerical label id of the bounding box to click at.
    - mouse_button: The mouse button to be clicked. It should be one of the following values: "left", "right", "middle".
    """

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

    label_id = str(label_id)
    x, y = 0.5, 0.5
    double_click_at_position(x, y)


@register_skill("hover_over_label")
def hover_over_label(label_id):
    """
    Moves the mouse to the position of the specified box id inside the application window, to hover over the UI item without clicking on it.

    Parameters:
    - label_id: The numerical label id of the bounding box to click at.
    """
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

    label_id = str(label_id)
    x, y = 0.5, 0.5
    move_mouse_to_position(x, y)

@register_skill("mouse_drag_to_label")
def mouse_drag_to_label(label_id):
    """
    Drag the cursor to the specified target with the left button pressed.

    Parameters:
    - label_id: The numerical label id of the bounding box to click at.
    """
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

    label_id = str(label_id)
    x, y = 0.5, 0.5
    mouse_drag(x, y)


__all__ = [
    "click_on_label",
    "double_click_on_label",
    "hover_over_label",
    "mouse_drag_to_label"
]