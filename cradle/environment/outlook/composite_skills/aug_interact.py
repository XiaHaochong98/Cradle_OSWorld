from cradle.config import Config
from cradle.log import Logger
from cradle.gameio import IOEnvironment
from cradle.environment.outlook.skill_registry import register_skill, post_skill_wait
from cradle.environment.outlook.atomic_skills.interact import click_at_position, move_mouse_to_position
from cradle.provider.sam_provider import SamProvider

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
    label_id = str(label_id)
    x, y = 0.5, 0.5
    click_at_position(x, y, mouse_button)


@register_skill("hover_over_label")
def hover_over_label(label_id):
    """
    Moves the mouse to the position of the specified box id inside the application window, to hover over the UI item without clicking on it.

    Parameters:
    - label_id: The numerical label id of the bounding box to click at.
    """
    label_id = str(label_id)
    x, y = 0.5, 0.5
    move_mouse_to_position(x, y)


__all__ = [
    "click_on_label",
    "hover_over_label"
]
