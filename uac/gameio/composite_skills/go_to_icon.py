import shutil, os
import time, math

import cv2
import numpy as np
from MTM import matchTemplates
from uac.gameio.atomic_skills.move import turn, move_forward, mount_horse
from uac.gameio.lifecycle.ui_control import take_screenshot
from uac.config import Config
from uac.log import Logger
from uac.utils.file_utils import assemble_project_path

config = Config()
logger = Logger()


def get_theta(origin_x, origin_y, center_x, center_y):
    '''
    The origin of the image coordinate system is usually located in the upper left corner of the image, with the x-axis to the right indicating a positive direction and the y-axis to the down indicating a positive direction. Using vertical upward as the reference line, i.e. the angle between it and the negative direction of the y-axis
    '''
    theta = math.atan2(center_x - origin_x, origin_y - center_y)
    theta = math.degrees(theta)
    return theta

# @TODO: This should be merged with the one in utils/template_matching.py
def match_template(src_file, template_file, template_resize_scale = 1, debug=False):
    srcimg = cv2.imread(assemble_project_path(src_file))
    template = cv2.imread(assemble_project_path(template_file))

    origin = (srcimg.shape[0] // 2, srcimg.shape[1] //2)

    # rotate
    # M = cv2.getRotationMatrix2D((w // 2, h // 2), r, 1)
    # template = cv2.warpAffine(template, M, (w, h))

    # resize
    if template_resize_scale != 1:
        template = cv2.resize(template, (0, 0), fx=template_resize_scale, fy=template_resize_scale)

    detection = matchTemplates([('', cv2.resize(template, (0, 0), fx=s, fy=s)) for s in [0.5, 0.6, 0.7, 0.8, 0.9, 1]],
                               srcimg,
                               N_object=1,
                               method=cv2.TM_CCOEFF_NORMED,
                               maxOverlap=0.1)
    (x, y, h, w), confidence = detection['BBox'].iloc[0], detection['Score'].iloc[0]

    # result = cv2.matchTemplate(srcimg, template, cv2.TM_CCOEFF_NORMED, mask=None)
    # min_val, confidence, min_loc, max_loc = cv2.minMaxLoc(result, mask=None)
    # h, w, c = template.shape

    center_x = x + w // 2
    center_y = y + h // 2

    # go towards it
    theta = get_theta(*origin, center_x, center_y)
    dis = np.sqrt((center_x - origin[0]) ** 2 + (center_y - origin[1]) ** 2)
    # KalmanFilter threshold = 0.59
    measure = {'confidence': confidence, 'distance': dis, 'bounding_box': (x, y, h, w)}

    if debug:
        logger.debug(f"confidence: {confidence:.3f}, distance: {dis:.3f}, theta: {theta:.3f}")
        vis = srcimg.copy()
        cv2.rectangle(vis, (x,y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(vis, f'{confidence:.3f}', (x,y), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.arrowedLine(vis, origin, (center_x, center_y), (0, 255, 0), 2, tipLength=0.1)
        measure['vis'] = vis
        #cv2.imshow("vis", measure['vis'])
    return theta, measure


def cv_go_to_icon(
        total_iterations,
        template_file,
        terminal_threshold=20,
        debug=False,
):
    
    save_dir = config.work_dir

    terminal_threshold *= config.resolution_ratio
        
    check_success, prev_dis, prev_theta, counter, ride_attempt, ride_mod, dis_stat = False, 0, 0, 0, 0, 10, []

    for step in range(total_iterations):
        
        timestep = time.time()

        #1. Get observation: screenshot
        take_screenshot(timestep, config.game_region, config.minimap_region, draw_axis=False)
        theta, info = match_template(os.path.join(save_dir, f"minimap_{timestep}.jpg"), template_file, config.resolution_ratio, debug)
        dis, confidence = info['distance'], info['confidence']
        if debug: cv2.imwrite(os.path.join(save_dir, f"minimap_{timestep}_detect.jpg"), info['vis'])

        # Control
        # if check_success:  # 0. check success
        #     if ride_attempt > 2 and abs(theta) > 25 and dis > 2 * terminal_threshold:
        #         if debug:
        #             logger.debug(f"step {step:03d} | timestep {timestep} done | theta: {theta:.2f} | distance: {dis:.2f} | confidence: {confidence:.3f} {'below threshold' if confidence < 0.5 else ''}")
        #             logger.debug('success!')
        #         return True
        #     elif np.mean(dis_stat) < terminal_threshold and ride_attempt % ride_mod == 0:  # 1. check riding
        #         if debug: logger.debug('should try to ride')
        #         mount_horse()
        #     ride_attempt += 1
        #     dis_stat.append(dis)
        
        if dis < terminal_threshold and abs(theta) < 90:  # begin to settle
            # check_success = True
            # if not dis_stat:  # first time
            #     dis_stat.append(dis)
            # if debug: logger.debug('checking mode is on')
            logger.debug('Success! Reach the icon.')
            return True
        
        # 2. Check stuck
        if abs(prev_dis - dis) < 0.5 and abs(prev_theta - theta) < 0.5:
            counter += 1
            if counter >= 1:
                if debug: logger.debug('begin to get rid of stuck')
                for _ in range(2):
                    turn(np.random.randint(30, 60) if np.random.rand()<0.5 else -np.random.randint(30, 60))
                    move_forward(np.random.randint(2, 6))
        else:
            counter = 0

        # 3. Move
        #turn(np.clip(theta, -90, 90))
        turn(theta)
        move_forward(1.5)
        time.sleep(0.5)

        if debug: logger.debug(
            f"step {step:03d} | timestep {timestep} done | theta: {theta:.2f} | distance: {dis:.2f} | confidence: {confidence:.3f} {'below threshold' if confidence < 0.5 else ''}")
        prev_dis, prev_theta = dis, theta

    return False  # failed
