import time
import pydirectinput

from uac.config import Config
from uac.gameio import IOEnvironment
from uac.gameio.skill_registry import register_skill, post_skill_wait

config = Config()
io_env = IOEnvironment()
ahk = io_env.ahk


def _theta_calculation(theta):
    """
    Calculates the adjusted theta value based on the configured mouse move factor.

    Parameters:
    - theta: The original theta value to be adjusted.
    """
    return theta * config.mouse_move_factor


@register_skill("turn")
def turn(theta):
    """
    Turns the in-game character left or right based on the specified theta angle.

    Parameters:
    - theta: The angle for the turn. Use a negative value to turn left and a positive value to turn right.
    For example, if theta = 30, the character will turn right 30 degrees. If theta = -30, the character will turn left 30 degrees.
    """
    theta = _theta_calculation(theta)

    ahk.mouse_move(theta, 0, speed=100, relative=True)


@register_skill("turn_right")
def turn_right(theta):
    """
    Continuous function to turn the in-game character to the right for the specified theta angle.

    Parameters:
    - theta: The angle in radians for the continuous right turn, theta must be a positive number.
    """
    theta = _theta_calculation(theta)
    assert 0 < theta

    ahk.mouse_move(theta, 0, speed=100, relative=True)


@register_skill("turn_left")
def turn_left(theta):
    """
    Continuous function to turn the in-game character to the left for the specified theta angle.

    Parameters:
    - theta: The angle in radians for the continuous left turn. theta must be a negative number.
    """
    theta = _theta_calculation(theta)
    assert theta < 0

    ahk.mouse_move(theta, 0, speed=100, relative=True)


@register_skill("move_forward")
def move_forward(duration):
    """
    Moves the in-game character forward for the specified duration.

    Parameters:
    - duration: The duration in seconds for which the character should move forward.
    """
    pydirectinput.keyDown('w')
    time.sleep(duration)
    pydirectinput.keyUp('w')


@register_skill("mount_horse")
def mount_horse():
    """
    Needs to be close to the horse. Mounts the horse by pressing the "e" key.
    """
    pydirectinput.press("e")

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("dismount_horse")
def dismount_horse():
    """
    Dismounts the horse by pressing the "e" key.
    """
    pydirectinput.press("e")

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("stop_horse")
def stop_horse():
    """
    Stops the horse by pressing the "Ctrl" key.
    """
    pydirectinput.press("ctrl")


__all__ = [
    "turn",
    #"turn_right",
    #"turn_left",
    "move_forward",
    "mount_horse",
    "dismount_horse",
    #"stop_horse",
]
