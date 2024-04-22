from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.environment.chrome.skill_registry import register_skill, post_skill_wait

config = Config()
logger = Logger()
io_env = IOEnvironment()

@register_skill("click_at_position")
def click_at_position(x, y, mouse_button):
    """
    Moves the mouse to the specified x,y corrdinates inside the application window and clicks at that position.

    Parameters:
    - x: The normalized x-coordinate of the target position. The value should be between 0 and 1.
    - y: The normalized y-coordinate of the target position. The value should be between 0 and 1.
    - mouse_button: The mouse button to be clicked. It should be one of the following values: "left", "right", "middle".
    """
    io_env.mouse_move_normalized(x, y)
    io_env.mouse_click_button(mouse_button)

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)

@register_skill("type_text")
def type_text(text):
    """
    Types the specified text using the keyboard. One character at a time.

    Parameters:
    - text: The text to be typed into the current UI control.
    """
    io_env.keys_type(text)

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)

@register_skill("press_enter")
def press_enter():
    """
    Pressing "enter" to move to the next state.
    """
    io_env.key_press('enter')

@register_skill("print_file")
def print_file():
    """
    Print the current file.
    """
    io_env.key_press('ctrl, p')

@register_skill("download_file")
def download_file():
    """
    Download the current file.
    """
    io_env.key_press('ctrl, s')

__all__ = [
    "click_at_position",
    "type_text",
    "press_enter",
    "print_file",
    "download_file"
]
