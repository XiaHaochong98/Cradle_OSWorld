from groundingdino.util.inference import load_model, load_image, predict, annotate

from uac.utils import Singleton


class GdProvider(metaclass=Singleton):
    def __init__(self):
        self.detect_model = load_model("./cache/GroundingDINO_SwinB_cfg.py", "./cache/groundingdino_swinb_cogcoor.pth")

    def detect(self, image_path,
                  text_prompt="wolf .",
                  box_threshold=0.5,
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
