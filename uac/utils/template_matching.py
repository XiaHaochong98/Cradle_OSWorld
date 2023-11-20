import json, cv2, os, time, sys
from typing import List, Union
from MTM import matchTemplates, drawBoxesOnRGB
import numpy as np
from glob import glob
import pandas as pd
from uac.config import Config

config = Config()
def showpair(vis, template, save=''):
    canvas_width = vis.shape[1] + template.shape[1]
    canvas_height = max(vis.shape[0], template.shape[0])
    canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
    canvas[:vis.shape[0], :vis.shape[1]] = vis
    canvas[:template.shape[0], vis.shape[1]:vis.shape[1] + template.shape[1]] = template
    if save: cv2.imwrite(save, canvas)
    cv2.namedWindow('match result', 0)
    cv2.imshow('match result', canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



def timing(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} consumes {elapsed_time:.4f}s")
        return result

    return wrapper


def log(message):
    print(message)



def read_csv(file):
    df = pd.read_csv(file, seq='\t')
    df.to_excel(os.path.splitext(file)[0] + '.xlsx')
    return df


# @timing
def template_match(image: np.ndarray, template: np.ndarray, scales: list):
    detection = matchTemplates([('', cv2.resize(template, (0, 0), fx=s, fy=s)) for s in scales], image, N_object=1,
                               method=cv2.TM_CCOEFF_NORMED, maxOverlap=0.1)
    detection['TemplateName'] = [str(round(i, 3)) for i in detection['Score']]  # confidence as name for display
    return detection


def match(src_file: str, template_file: str, result_json_file: str, **kwargs) -> List[dict]:
    '''
    Multi-scale template matching
    :param src_file: source image file
    :param template_file: template image file
    :param kwargs: extra parameters including
        scales: scales for template, default scales is 'normal', chosen from 'small','mid','normal', you can also specify a list of float numbers
        rotate: rotate angle for source image, rotate at the center of image clockwise
        save_path: save path for matched image
        log_results: log detection results

    :return:
    objects_list, a list of dicts, including template name, bounding box and confidence.
    '''
    os.makedirs(os.path.dirname(result_json_file), exist_ok=True)
    scales = 'normal' if not kwargs.get('scale') else kwargs.get('scale')
    if scales == 'small':
        scales = [0.1, 0.2, 0.3, 0.4, 0.5]
    elif scales == 'mid':
        scales = [0.3, 0.4, 0.5, 0.6, 0.7]
    elif scales == 'normal':
        scales = [0.8, 0.9, 1.0, 1.1, 1.2]
    elif scales == 'full':
        scales = [0.5,0.75,1.0,1.5,2]
    elif not isinstance(scales, list):
        raise ValueError('scales must be a list of float numbers or one of "small","mid","normal"')

    image = cv2.imread(src_file)
    template = cv2.imread(template_file)
    # resize template according to resolution ratio
    template = cv2.resize(template, (0, 0), fx=config.resolution_ratio, fy=config.resolution_ratio)


    if kwargs.get('rotate'):
        h, w, c = image.shape
        M = cv2.getRotationMatrix2D((w // 2, h // 2), kwargs.get('rotate'), 1)
        image = cv2.warpAffine(image, M, (w, h))  # np.rot90

    begin_detect_time = time.time()
    detection = template_match(image, template, scales)
    end_detect_time = time.time()

    template_name = os.path.splitext(os.path.basename(template_file))[0]

    if kwargs.get('save_path'):
        overlay = drawBoxesOnRGB(image, detection,
                                 showLabel=True,
                                 boxThickness=4,
                                 boxColor=(0, 255, 0),
                                 labelColor=(0, 255, 0),
                                 labelScale=1)
        save_path = kwargs.get('save_path')
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        showpair(overlay, template, save=os.path.join(save_path,f'{template_name}-{os.path.basename(src_file)}'))

    # DataFrame to list of dicts
    objects_list = []
    for bounding_box, confidence in zip(detection['BBox'], detection['Score']):
        object_dict = {
            "type":template_name,
            "name": template_name,
            "bounding_box": bounding_box,
            "reasoning": "",
            "value": 0,
            "confidence": confidence,
        }
        objects_list.append(object_dict)
        if kwargs.get('log_results'):
            log(f'{src_file}\t{template_file}\t{bounding_box}\t{confidence}\t{end_detect_time - begin_detect_time}',)
    with open(result_json_file, 'w') as f:
        json.dump(objects_list, f, indent=4)
    return objects_list