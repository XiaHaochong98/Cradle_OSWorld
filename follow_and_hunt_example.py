import shutil, os
import time, math

import cv2
import numpy as np
from MTM import matchTemplates
import torch
from torchvision.ops import box_convert

from uac.config import Config
from uac.log import Logger
from groundingdino.util.inference import load_model
from uac.gameio.composite_skills.follow_and_hunt import shooting, cv_go_hunting, groundingDINO_detect
from uac.gameio.lifecycle.ui_control import switch_to_code, switch_to_game, take_screenshot, pause_game, unpause_game

config = Config()
logger = Logger()

if __name__ == '__main__':
    # switch_to_game()
    
    # shooting example
    #shooting(total_steps=200, follow_dis_threshold=50,
    #         shoot_template_file=assemble_project_path('./res/icons/shoot.jpg'),
    #         debug=True)
    
    # hunting wolves in horse example
    # cv_go_hunting(total_steps=100,
    #                follow_template_files=[assemble_project_path(r'./res/icons/companion1_1.jpg'),assemble_project_path(r'./res/icons/companion1_1.jpg')],
    #                follow_dis_threshold=30,
    #                debug=True)
    
    #detection example by GroundingDINO
    groundingDINO_detect("./res/samples/camp-on-horse-no-line-000.jpg")
