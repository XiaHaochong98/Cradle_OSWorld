from groundingdino.util.inference import load_model, load_image, predict, annotate
from uac.gameio.lifecycle.ui_control import annotate_with_coordinates
from uac.utils import Singleton
import cv2
import torch

class GdProvider(metaclass=Singleton):
    def __init__(self):
        self.detect_model = load_model("./cache/GroundingDINO_SwinB_cfg.py", "./cache/groundingdino_swinb_cogcoor.pth")

    def detect(self, image_path,
                  text_prompt="wolf .",
                  box_threshold=0.4,
                  text_threshold=0.25,
                  device='cuda',
                  ):
        
        image_source, image = load_image(image_path)

        boxes, logits, phrases = predict(
            model=self.detect_model,
            image=image,
            caption=text_prompt,
            box_threshold=box_threshold,
            text_threshold=text_threshold,
            device=device
        )
        
        return image_source, boxes, logits, phrases

    def save_annotate_frame(self, image_source, boxes, logits, phrases, text_prompt, cur_screen_shot_path):

        # remove the main character itself from the boxes
        if "Person" in text_prompt:
            if len(boxes) > 1:
                index = 0
                dis = 1.5

                for i in range(len(boxes)):
                    down_mid = (boxes[i, 0], boxes[i, 1] + boxes[i, 3] / 2)
                    distance = torch.sum(torch.abs(torch.tensor(down_mid) - torch.tensor((0.5, 1.0))))

                    if distance < dis:
                        dis = distance
                        index = i
                
                boxes_ = torch.cat([boxes[:index], boxes[index + 1:]])
                logits_ = torch.cat([logits[:index], logits[index + 1:]])

                phrases.pop(index)
                
                annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes_[:,:], logits=logits_[:], phrases=phrases)
                cv2.imwrite(cur_screen_shot_path, annotated_frame)
            elif len(boxes)==1:

                phrases.pop(0)
                boxes_ = torch.tensor(boxes[1:])
                logits_ = torch.tensor(logits[1:])

                annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes_[:,:], logits=logits_[:], phrases=phrases)
                cv2.imwrite(cur_screen_shot_path, annotated_frame)
            else:
                annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes[:,:], logits=logits[:], phrases=phrases)
                cv2.imwrite(cur_screen_shot_path, annotated_frame)
            
        else:
            annotated_frame = annotate_with_coordinates(image_source=image_source, boxes=boxes[:,:], logits=logits[:], phrases=phrases)
            cv2.imwrite(cur_screen_shot_path, annotated_frame)

