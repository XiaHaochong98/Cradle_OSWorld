import numpy as np
from glob import glob
from PIL import Image, ImageDraw, ImageFont
import os
import pydirectinput
import pyautogui
import time

def switch_to_game():
    pyautogui.hotkey("ctrl", "win", "left")
    time.sleep(1)
    pyautogui.moveTo(200, 200)
    pyautogui.click()
    pydirectinput.press('esc')
    time.sleep(1)                                                     # wait for game to back

def switch_to_code():
    pydirectinput.press('esc')                                              # pause game
    pyautogui.hotkey("ctrl", "win", "right")                               # switch desktop


def take_screenshot(save_dir,
               index = 0,
               screen_region=(0,45, 2560, 1600),
               mini_map_region=(70,1110, 480, 480),
               draw_axis=False):
    # save screenshots
    # You need to modify the region to your own
    screen = pyautogui.screenshot(save_dir + "/screen_" + str(index) + ".jpg", region=screen_region)
    mini_map = pyautogui.screenshot(save_dir + "/mini_map_" + str(index) + ".jpg", region=mini_map_region)

    if draw_axis:
        # draw axis on the screenshot
        draw = ImageDraw.Draw(screen)
        width, height = screen.size
        cx, cy = width // 2, height // 2

        draw.line((cx, 0, cx, height), fill="blue", width=3)  # Y
        draw.line((0, cy, width, cy), fill="blue", width=3)  # X

        font = ImageFont.truetype("arial.ttf", 30)
        offset_for_text = 30
        interval = 0.1
        for i in range(10):
            if i > 0:
                draw.text((cx + interval * (i ) * width // 2, cy), str(i ), fill="blue", font = font)
                draw.text((cx - interval * (i) * width // 2, cy), str(-i), fill="blue", font = font)
                draw.text((cx - offset_for_text - 10, cy + interval * (i ) * height // 2), str(-i), fill="blue", font = font)
            draw.text((cx - offset_for_text, cy - interval * (i ) * height // 2), str(i), fill="blue", font = font)

        screen.save(save_dir + "/axes_screen_" + str(index) + ".jpg",)