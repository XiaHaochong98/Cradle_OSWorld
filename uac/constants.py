# Gather information expected fields
ACTION_GUIDANCE = 'action_guidance'
ITEM_STATUS = 'item_status'
TASK_GUIDANCE = 'task_guidance'
DIALOGUE = 'dialogue'
GATHER_TEXT_REASONING = 'reasoning'
IMAGE_DESCRIPTION = 'description'
TARGET_OBJECT_NAME = 'target_object_name'
GATHER_INFO_REASONING = 'reasoning'

# LLM message type constants
MESSAGE_CONSTRUCTION_MODE_TRIPART = 'tripartite'
MESSAGE_CONSTRUCTION_MODE_PARAGRAPH = 'paragraph'

# Tags used in prompt templates
IMAGES_INPUT_TAG_NAME = 'image_introduction'
IMAGE_INTRO_TAG_NAME = 'introduction'
IMAGE_PATH_TAG_NAME = 'path'
IMAGE_RESOLUTION_TAG_NAME = 'resolution'
IMAGE_ASSISTANT_TAG_NAME = 'assistant'

IMAGES_INPUT_TAG = f'<${IMAGES_INPUT_TAG_NAME}$>'
