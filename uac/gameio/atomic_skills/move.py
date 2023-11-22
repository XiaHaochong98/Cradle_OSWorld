import time
import pydirectinput

from uac.config import Config
from uac.gameio import IOEnvironment

config = Config()
io_env = IOEnvironment()
ahk = io_env.ahk

def theta_calculation(theta):
    return theta * config.mouse_move_factor

def turn(theta):
    '''
    Turn left/right for theta
    Negative theta for left
    Positive theta for right
    '''
    theta = theta_calculation(theta)

    ahk.mouse_move(theta, 0, speed=100, relative=True)

def turn_right(theta):
    '''Continuous, Turn right for theta'''
    '''May be abondoned later'''
    theta = theta_calculation(theta)
    assert 0 < theta

    ahk.mouse_move(theta, 0, speed=100, relative=True)

def turn_left(theta):
    '''Continuous, Turn left for theta'''
    '''May be abondoned later'''
    theta = theta_calculation(theta)
    assert theta < 0

    ahk.mouse_move(theta, 0, speed=100, relative=True)

def move_forward(duration):
    '''move forward for duration seconds'''
    pydirectinput.keyDown('w')
    time.sleep(duration)
    pydirectinput.keyUp('w')

def mount_horse():
    """
    Mount horse
    """
    pydirectinput.press("e")

def dismount_horse():
    """
    dismount horse
    """
    pydirectinput.press("e")

def stop_horse():
    """
    stop the horse
    """
    pydirectinput.press("ctrl")    