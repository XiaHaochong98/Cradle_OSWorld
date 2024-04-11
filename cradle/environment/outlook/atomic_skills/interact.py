from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.environment.outlook.skill_registry import register_skill, post_skill_wait

config = Config()
logger = Logger()
io_env = IOEnvironment()


@register_skill("click_at")
def click_at(x, y, mouse_button):
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


__all__ = [
    "click_at",
    "type_text",
]
