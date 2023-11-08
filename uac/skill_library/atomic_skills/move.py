import time
import pyautogui
import pydirectinput

def turn(ahk, theta):
    '''
    Turn left/right for theta
    Negative theta for left
    Positive theta for right
    '''
    ahk.mouse_move(theta, 0, speed=100, relative=True)

def turn_right(ahk, theta):
    '''Continuous, Turn right for theta'''
    '''May be abondoned later'''
    assert 0 < theta
    ahk.mouse_move(theta, 0, speed=100, relative=True)

def turn_left(ahk, theta):
    '''Continuous, Turn left for theta'''
    '''May be abondoned later'''
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