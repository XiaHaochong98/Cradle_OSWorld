# Environment configuration keys
ENVIRONMENT_NAME = 'env_name'
ENVIRONMENT_WINDOW_NAME_PATTERN = 'win_name_pattern'
ENVIRONMENT_SHORT_NAME = 'env_short_name'
ENVIRONMENT_SUB_PATH = 'sub_path'

# Gather information expected fields
ACTION_GUIDANCE = 'action_guidance'
ITEM_STATUS = 'item_status'
TASK_GUIDANCE = 'task_guidance'
DIALOGUE = 'dialogue'
GATHER_TEXT_REASONING = 'reasoning'
TARGET_OBJECT_NAME = 'target_object_name'
GATHER_INFO_REASONING = 'reasoning_of_object'
SCREEN_CLASSIFICATION = 'screen_classification'
GENERAL_GAME_INTERFACE = 'general game interface without any menu'
TRADE_INTERFACE = 'trade'
MAP_INTERFACE = 'map'
PAUSE_INTERFACE = 'pause'
SATCHEL_INTERFACE = 'satchel'
RADIAL_INTERFACE = 'radial menu'
LAST_TASK_GUIDANCE = 'last_task_guidance'
LAST_TASK_HORIZON = 'task_horizon'
TASK_DESCRIPTION = 'task_description'

# Two instances of augmentation info dict
PREVIOUS_AUGMENTATION_INFO = "previous_augmentation_info"
CURRENT_AUGMENTATION_INFO = "current_augmentation_info"

# SAM2SOM parameters
SAM2SOM_CONFIG = 'sam2som_config'
SAM_PRED_IOU_THRESH = 'sam_pred_iou_thresh'
SAM_RESIZE_RATIO = 'sam_resize_ratio'
SAM_CONTRAST_LEVEL = 'sam_contrast_level'
SAM_MAX_AREA = 'sam_max_area'

# Augmentation info dict attributes
IMAGE_DESCRIPTION = 'image_description'
IMAGE_DESCRIPTION_OF_BOUNDING_BOXES = 'image_description_of_bounding_boxes'
AUG_MOUSE_X = 'mouse_x'
AUG_MOUSE_Y = 'mouse_y'
AUG_BASE_IMAGE_PATH='image_path'
AUG_SOM_MOUSE_IMG_PATH = 'som_mouse_img_path'
AUG_MOUSE_IMG_PATH = 'mouse_img_path'
AUG_SOM_IMAGE_PATH = 'som_image_path'
AUG_SOM_MAP = 'som_map'
LENGTH_OF_SOM_MAP = 'length_of_som_map'

# SAME_FLAG between two image to check whether som_image should be generated agin or not 
IMAGE_SAME_FLAG = "image_same_flag"
MOUSE_POSITION_SAME_FLAG = "mouse_position_same_flag"

# Tags used in prompt templates
IMAGES_INPUT_TAG_NAME = 'image_introduction'
IMAGE_INTRO_TAG_NAME = 'introduction'
IMAGE_PATH_TAG_NAME = 'path'
IMAGE_RESOLUTION_TAG_NAME = 'resolution'
IMAGE_ASSISTANT_TAG_NAME = 'assistant'
IMAGES_INPUT_TAG = f'<${IMAGES_INPUT_TAG_NAME}$>'

# Minimap information
MINIMAP_INFORMATION = 'minimap_information'
RED_POINTS = 'red points'
YELLOW_POINTS = 'yellow points'
YELLOW_REGION = 'yellow region'
GD_PROMPT = 'red points . yellow points . yellow region .'

# Skill-related keys
DISTANCE_TYPE = 'distance'

# Local memory
AUGMENTED_IMAGES_MEM_BUCKET = 'augmented_image'
IMAGES_MEM_BUCKET = 'image'
NO_IMAGE = '[None]'

# LLM message type constants
MESSAGE_CONSTRUCTION_MODE_TRIPART = 'tripartite'
MESSAGE_CONSTRUCTION_MODE_PARAGRAPH = 'paragraph'

# Prompts when output is None
NONE_TASK_OUTPUT = "null"
NONE_TARGET_OBJECT_OUTPUT = "null"

# keys in exec_info
EXECUTED_SKILLS = 'executed_skills'
LAST_SKILL = 'last_skill'
ERRORS = 'errors'
ERRORS_INFO = 'errors_info'

# info in pre process action
INVALID_BBOX = 'invalid_bbox'