import shutil, os
import time, math
import cv2
import numpy as np
from MTM import matchTemplates as mt
from uac.gameio.atomic_skills.move import turn, move_forward, mount_horse
from uac.gameio.lifecycle.ui_control import take_screenshot


def get_theta(origin_x, origin_y, center_x, center_y):
    '''
    The origin of the image coordinate system is usually located in the upper left corner of the image, with the x-axis to the right indicating a positive direction and the y-axis to the down indicating a positive direction. Using vertical upward as the reference line, i.e. the angle between it and the negative direction of the y-axis
    '''
    theta = math.atan2(center_x - origin_x, origin_y - center_y)
    theta = math.degrees(theta)
    return theta


def matchTemplate(src_file, template_file, origin, debug=False, **kwargs):
    srcimg = cv2.imread(src_file)
    template = cv2.imread(template_file)

    # rotate
    # M = cv2.getRotationMatrix2D((w // 2, h // 2), r, 1)
    # template = cv2.warpAffine(template, M, (w, h))

    # resize
    # if kwargs['resize_scale']:
    #     scale = kwargs['resize_scale']
    #     template = cv2.resize(template, (0, 0), fx=scale, fy=scale)
    detection = mt([('', cv2.resize(template, (0, 0), fx=s, fy=s)) for s in [0.5, 0.6, 0.7, 0.8, 0.9, 1]], srcimg,
                   N_object=1,
                   method=cv2.TM_CCOEFF_NORMED, maxOverlap=0.1)
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
    measure = {'confidence': confidence, 'distance': dis}

    if debug:
        print(f"confidence: {confidence:.3f}, distance: {dis:.3f}, theta: {theta:.3f}")
        vis = srcimg.copy()
        cv2.rectangle(vis, (x,y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(vis, f'{confidence:.3f}', (x,y), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.arrowedLine(vis, origin, (center_x, center_y), (0, 255, 0), 2, tipLength=0.1)
        measure['vis'] = vis
    return theta, measure


def find_get_on_horse_cv(
        save_dir,
        total_time_step,
        template_file,
        screen_region,
        mini_map_region,
        mini_map_center=None,
        terminal_threshold=20,
        debug=False,
):
    # 0. switch to game, create experiment directory, and initialize
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    os.makedirs(save_dir, exist_ok=True)
    if mini_map_center is None:
        mini_map_center = (mini_map_region[2] // 2, mini_map_region[3] // 2)
    check_success, prev_dis, prev_theta, counter, ride_attempt, ride_mod, dis_stat = False, 0, 0, 0, 0, 10, []
    for timestep in range(total_time_step):
        # get observation: screenshot
        take_screenshot(save_dir, timestep, screen_region, mini_map_region, draw_axis=False)
        theta, info = matchTemplate(os.path.join(save_dir, f"mini_map_{timestep}.jpg"), template_file, mini_map_center,debug)
        dis, confidence = info['distance'], info['confidence']
        if debug: cv2.imwrite(os.path.join(save_dir, f"mini_map_{timestep}_detect.jpg"), info['vis'])
        # control
        if check_success:  # 0. check success
            if ride_attempt > 2 and abs(theta) > 25 and dis > 2 * terminal_threshold:
                if debug:
                    print(f"timestep {timestep:03d} done | theta: {theta:.2f} | distance: {dis:.2f} | confidence: {confidence:.3f} {'below threshold' if confidence < 0.5 else ''}")
                    print('success!')
                return True
            elif np.mean(dis_stat) < terminal_threshold and ride_attempt % ride_mod == 0:  # 1. check riding
                if debug: print('should try to ride')
                mount_horse()
            ride_attempt += 1
            dis_stat.append(dis)
        if dis < terminal_threshold:  # begin to settle
            check_success = True
            if not dis_stat:  # first time
                dis_stat.append(dis)
            if debug: print('checking mode is on')
        # 2. check stuck
        if abs(prev_dis - dis) < 0.5 and abs(prev_theta - theta) < 0.5:
            counter += 1
            if counter >= 1:
                if debug: print('begin to get rid of stuck')
                for _ in range(2):
                    turn(np.random.randint(30, 60) if np.random.rand()<0.5 else -np.random.randint(30, 60))
                    move_forward(np.random.randint(2, 6))
        else:
            counter = 0
        # 3. move
        turn(np.clip(theta, -90, 90))
        move_forward(1.5)
        if debug: print(
            f"timestep {timestep:03d} done | theta: {theta:.2f} | distance: {dis:.2f} | confidence: {confidence:.3f} {'below threshold' if confidence < 0.5 else ''}")
        prev_dis, prev_theta = dis, theta

    return False  # failed
