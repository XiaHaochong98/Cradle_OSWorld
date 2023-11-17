import time
import os
import math

import cv2
import numpy as np

from uac.gameio.atomic_skills.move import turn, move_forward
from uac.gameio.lifecycle.ui_control import take_screenshot

def cv_navigation(save_dir, total_time_step, screen_region, mini_map_region, debug = False):

    for timestep in range(total_time_step):
        print("timestep", timestep)
        if timestep > 0:
            turn(turn_angle)
            move_forward(0.3)
            time.sleep(0.1) # avoid running too fast
        
        take_screenshot(save_dir, timestep, screen_region, mini_map_region, draw_axis=False)

        turn_angle = calculate_turn_angle(save_dir, timestep, debug)

def calculate_turn_angle(file_path, index, debug = False, show_image = False):
    mini_map_path = file_path + "/mini_map_" + str(index) + ".jpg"
    output_path = file_path + "/direction_map_" + str(index) + ".jpg"
    image = cv2.imread(mini_map_path)    

    # Convert the image to HSV space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Calculate image center
    image_center = np.array([image.shape[1] // 2, image.shape[0] // 2])
    width, height  = image_center
    center_x = width 
    center_y = height

    # Define range for red color
    lower_red_1 = np.array([0,30,30])
    upper_red_1 = np.array([10,255,255])
    lower_red_2 = np.array([160,30,30])
    upper_red_2 = np.array([180,255,255])

    # Threshold the HSV image to get the red regions
    mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
    mask = mask1 + mask2

    kernel = np.ones((3,3), np.uint8)
    mask_upper_bottom = cv2.dilate(mask, kernel, iterations = 2)
    # mask = cv2.erode(mask, kernel, iterations = 2)

    def get_contour(mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours by area and get the top 5
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        
        # Find the minimum distance from each contour to the image center
        def min_distance_from_center(contour):
            return min([  np.linalg.norm(np.array(point[0]) - image_center) for point in contour])

        # Find the contour with the minimum distance to the image center
        closest_contour = min(contours, key=min_distance_from_center)
        output_mask = np.zeros_like(mask)
        contour = cv2.drawContours(output_mask, [closest_contour], -1, (1), thickness=cv2.FILLED) * 255

        lines = None
        minLineLength = width / 15
        threshold = 10
        while (lines is None or len(lines) < 10) and threshold > 0:
            lines = cv2.HoughLinesP(contour, 1, np.pi / 180, threshold=threshold, minLineLength= minLineLength, maxLineGap=100)
            if minLineLength <= 10:
                threshold -= 1
            minLineLength /= 1.1
        if threshold == 0:
            return None
        return lines
    
    lines = get_contour(mask)
    lines_upper_bottom = get_contour(mask_upper_bottom)

    if lines is None or lines_upper_bottom is None:
        return 0

    line_img = np.zeros_like(image)
    upper_bottom_img = np.zeros_like(image)

    def slope_to_angle(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1

        angle_radians = math.atan2(dy, dx)
        angle_degrees = math.degrees(angle_radians)

        if angle_degrees < 0:
            angle_degrees += 180

        return angle_degrees

    # Calcualte the average slope with the lines near the center of the mini-map
    central_line_angles = []
    central_dots = []
    distance_threshold = height / 50

    while len(central_line_angles) < 5:
        central_line_angles = []
        central_dots = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_img, (x1, y1), (x2, y2), (255), 1)
            cv2.line(image, (x1, y1), (x2, y2), (255), 1)

            if (x1 - center_x)**2 + (y1 -center_y)**2 < distance_threshold**2 or (x2 - center_x)**2 + (y2 -center_y)**2 < distance_threshold**2:
                angle_degrees = slope_to_angle(x1, y1, x2, y2)
                central_line_angles.append(angle_degrees)

                if (x1 - center_x)**2 + (y1 -center_y)**2 < (x2 - center_x)**2 + (y2 - center_y)**2:
                    central_dots.append((x1, y1))
                else:
                    central_dots.append((x2, y2))

        distance_threshold *= 1.2
    # if debug:
    #     print("distance_threshold", distance_threshold)
    #     print("central_dots", central_dots)

    # Use the average of the y of the chosen lines to determine the red line is in the upper/bottom half of the mini-map
    central_line_y = []
    distance_threshold = height / 5
    while not central_line_y:
        for line in lines_upper_bottom:
            cv2.line(upper_bottom_img, (x1, y1), (x2, y2), (255), 1)
            
            x1, y1, x2, y2 = line[0]
            if (x1 - center_x)**2 + (y1 - center_y)**2 < distance_threshold**2 or (x2 - center_x)**2 + (y2 - center_y)**2 < distance_threshold**2:
                if (x1 - center_x)**2 + (y1 - center_y)**2 > (x2 - center_x)**2 + (y2 - center_y)**2:
                    central_line_y.append(y1)
                else:
                    central_line_y.append(y2)
        distance_threshold *= 1.2

    angle_degrees = np.average(central_line_angles)

    # if debug:
    #     print(central_line_y)

    is_upper = np.average(central_line_y)  <= center_y * 1.05

    deviation_angle_degrees = None
    deviation_threshold = width / 10
    central_dot_upper = True
    if len(central_dots) > 0:
        average_dot = np.average(central_dots, axis=0)
        if (average_dot[0] - center_x)**2 + (average_dot[1] - center_y)**2 > deviation_threshold**2:
            deviation_angle_degrees = slope_to_angle(average_dot[0], average_dot[1], center_x, center_y)
            central_dot_upper = average_dot[1] <= center_y


    def cal_real_turn_angle(angle_degrees, is_upper):
        if angle_degrees > 90:
            angle_degrees -= 180

        # calculate turn angle(the angle between the red line and normal line)
        # positive: the red line is on the right
        # negative: the red line is on the left
        if angle_degrees < 0:
            turn_angle = 90 + angle_degrees
        else:
            turn_angle = -90 + angle_degrees

        # process the angle if the red line is in the bottom half of the mini-map
        if not is_upper:
            if turn_angle > 0:
                real_turn_angle = turn_angle - 180
            else:
                real_turn_angle = turn_angle + 180
        else:
            real_turn_angle = turn_angle
        return real_turn_angle
    
    red_line_turn_angle = cal_real_turn_angle(angle_degrees, is_upper)
    real_turn_angle = red_line_turn_angle
    if deviation_angle_degrees:
        deviation_turn_angle = cal_real_turn_angle(deviation_angle_degrees, central_dot_upper)
        if is_upper == central_dot_upper:
            real_turn_angle = (real_turn_angle + deviation_turn_angle) / 2
        else:
            real_turn_angle = deviation_turn_angle

    real_turn_angle *= 1.1

    angle_radians = math.radians(real_turn_angle)
    slope = math.tan(angle_radians)
    if slope == 0:
        slope = 0.0001
    slope = 1 / slope

    if debug:
        print("slope", slope)
        print("red_line_turn_angle", red_line_turn_angle)
        print("is_upper", is_upper)
        if deviation_angle_degrees:
            print("deviation_turn_angle", deviation_turn_angle)
            print("central_dot_upper", central_dot_upper)
        print("real turn angle", real_turn_angle)

    # Draw green line to show the calculated turn direction
    offset = 50
    if abs(slope * offset) >= center_y:
        offset = (center_y - 1) / abs(slope)

    end_x = center_x + offset
    start_x = center_x - offset
    end_y = center_y - slope * offset  
    start_y = center_y + slope * offset  

    cv2.line(image, (int(start_x), int(start_y)), (int(end_x), int(end_y)), (0, 255, 0), 2)

    if len(central_dots) > 0 and (average_dot[0] - center_x)**2 + (average_dot[1] - center_y)**2 > deviation_threshold**2:
        point = (int(average_dot[0]), int(average_dot[1]))  
        color = (0, 255, 255)  
        cv2.circle(image, point, 5, color, -1)
    
    cv2.imwrite(output_path, image)

    if show_image:
        cv2.imshow('upper', upper_bottom_img)
        cv2.imshow('Image with Lines', line_img)
        cv2.imshow('Image', image)
        cv2.imshow('mask_upper_bottom', mask_upper_bottom)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return real_turn_angle