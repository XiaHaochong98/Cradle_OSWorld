# UAC
Repository for the Universal Agent Control project.

Please setup your environment as:
```bash
conda create --name uac-dev python=3.10
conda activate uac-dev
pip3 install -r requirements.txt
```

### To install Faiss:
```bash
# CPU-only version
conda install -c pytorch faiss-cpu=1.7.4 mkl=2021 blas=1.0=mkl
```

### To install GroundingDino:

Download its weights to the cache directory:

```bash
mkdir cache
cd cache
curl -L -C - -O https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swinb_cogcoor.pth
cd ..
```

**Note:**
You should have a CUDA environment, please make sure you have properly installed CUDA dependencies first. You can use the following command to detect it on Linux.
```bash
nvcc -V
```

Or search for its environment variable: CUDA_HOME or CUDA_PATH. On Windows it should be something like "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8" and on Linux like "/usr/local/cuda".

If you don't get the specific version, you should download cudatoolkit and cuDNN first (version 11.8 is recommended).

If you don't download CUDA correctly, after installing GroundingDino, the code will produce: 

```bash
NameError: name '_C' is not defined
```

If this happened, please re-setup CUDA and pytorch, reclone the git and perform all installation steps again.

On Windows install from https://developer.nvidia.com/cuda-11-8-0-download-archive (Linux packages also available).

Make sure pytorch is installed using the right CUDA dependencies.

```bash
conda install pytorch torchvision cudatoolkit=11.8 -c nvidia -c pytorch
```

If this doesn't work, or you prefer the pip way, you can try something like:

```bash
pip3 install --upgrade torch==2.1.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html
pip3 install torchvision==0.16.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html
```

Now, you should install the pre-compiled GroundingDino with the project dependencies. You can use the package in our repo and the following commands:

```bash
cd deps
pip install groundingdino-0.1.0-cp310-cp310-win_amd64.whl
cd ..
```

Once it is installed, we need to pre-download some required model files and set some environment variables.

```bash
# Define the necessary environment variables, this can be done in the .env file in the uac directory
HUGGINGFACE_HUB_CACHE = "./cache/hf" # This can be the full path too, if the relative one doesn't work

# Pre-download huggingface files needed by GroundingDino
# This step may require a VPN connection
mkdir $HUGGINGFACE_HUB_CACHE
huggingface-cli download bert-base-uncased config.json tokenizer.json vocab.txt tokenizer_config.json model.safetensors --cache-dir $HUGGINGFACE_HUB_CACHE

# Define the last necessary environment variable, this can be done in the .env file in the uac directory
# This step will avoid needing a VPN to run
TRANSFORMERS_OFFLINE = "TRUE"
```

If for some reason there is some incompatibility in installing or running GroundingDino, it's recommended to recreate your environment.

Only if really necessary, you can try to clone and compile/install GroundingDino yourself.

```bash
# Clone
cd ..
git clone https://github.com/IDEA-Research/GroundingDINO.git
cd GroundingDINO

# Build and install it
pip3 install -r requirements.txt
pip3 install .
cd ../UAC
```

It should install without errors and now it will be available for any project using the same conda environment (uac-dev).

To build the C++ code on Windows, you may need to install build tools.

Download them from https://visualstudio.microsoft.com/visual-cpp-build-tools/
Make sure to select "Desktop Environment with C++" and include the 1st 3 optional packages:
- MSVC v141 or higher
- Windows SDK for your OS version
- CMake tools

### Other dependencies

Keep the UAC requirements.txt file updated in your branch, but only add dependencies that are really required by the system.

runner.py is the entry point to run an agent. Currently not working code, just an introductory sample.

To install the videosubfinder for gather information module:

Download the videosubfinder from https://sourceforge.net/projects/videosubfinder/ and extract the files into the res/tool/subfinder folder.

The file structure should be like this:
- res
  - tool
    - subfinder
      - RGBImages
      - VideoSubFinderWXW.exe
      - test.srt
      ...

#### Tunning the videosubfinder
To get the best extraction results, you can tune the subfinder by changing the parameters in the settings/general.cfg file.
Change the following keys to the corresponding values:
vedges_points_line_error = 0.9  
ila_points_line_error = 0.9  
sub_frame_length = 8   

## General guidelines

Always, **always**, **ALLWAYS** get the latest /main branch.

Any file with text content in the project in the resources directory (./res) should be in UTF-8 encoding. Use the uac.utils to open/save files.


## Infra code

### 1. OpenAI provider

OpenAI provider now can expose embeddings and LLM from OpenAI and Azure together. Users only need to create one instance of each and pass the appropriate configuration.

Example configurations are in /conf. To avoid exposing sensitive details, keys and other private info should be defined in environmental variables.

The suggested way to do it is to create a .env file in the root of the repository (never push this file to GitHub) where variables can be defined, and then mention the variable names in the configs.

Please check the examples below.

Sample .env file containing private info that should never be on git/GitHub:
```
OA_OPENAI_KEY = "abc123abc123abc123abc123abc123ab"
AZ_OPENAI_KEY = "123abc123abc123abc123abc123abc12"
AZ_BASE_URL = "https://abc123.openai.azure.com/"
```

Sample config for an OpenAI provider:
```
{
	"key_var" : "OA_OPENAI_KEY",
	"emb_model": "text-embedding-ada-002",
	"comp_model": "gpt-4-vision-preview",
	"is_azure": false
}
```

### 2. Prompt definition files

Prompt files are located in the repo at ./res/prompts. Out of the code tree.

There three types of prompt-related files: input_example, output_example, and templates. Examples are json files. Templates are text files with special markers inside. See details below.

Inside each of these directories, most files will fit into three categories: decision_making, gather_information, and success_detection

Files are named according to the format: ./res/prompts/\<type\>/\<category\>_\<sub_task\>.\<ext\>

For example: 
./res/**input_example**/**decision_making**_**follow_red_line**.json, is an example of **input** for the **decision making** prompt for the **follow the red line** sub-task. In the future, most filenamess will end in "_general", when they are not sub-task-specific anymore.

As shown below, such "input_example" files illustrate the **parameters** needed to fill a prompt "template".
Not all input examples need the same parameters. Only the parameters required the corresponding specific template (".prompt" file).

Also, in most situations the format of the parameter "output-format" (if it exists) must be exactly the same as the corresponding "output_example" json file.

**>>> Allways check the /main branch for the latest examples!!!**

### 2.1 Prompt for Gather Information

#### 2.1.1 Input Example for Gather Information

```python
input_example = {
    "type": "gather_information",
    "image_path": "./res/samples/game_screenshot.png"
}
# type: the type of the prompt, should be "gather_information"
# image_path: the path of the image
```

Other parameters will be added.

#### 2.1.2 Output Example for Gather Information

```python
output_example = {
    "type": "gather_information",
    "description": "The image shows a scene from the video game Red Dead Redemption 2. It presents a third-person perspective of a character, presumably the protagonist Arthur Morgan, riding a horse. The character is dressed in typical cowboy attire, including a hat, and is equipped with what appears to be a revolver holstered on his right hip, and a satchel slung across his left shoulder. The environment is sunny and seems to be an idyllic forest clearing with a variety of trees, including pines and others with more broad leaves. The atmosphere is serene and there are several horses scattered around the area, suggesting a temporary camp or resting spot for a group.\n\nOn the bottom of the image, there's a prompt indicating \"Hitch Horse [E]\", suggesting that the player on a PC can press the \"E\" key to hitch their horse to a post or another item intended for that purpose.\n\nAs for the minimap on the bottom-left corner, the semi-opaque circular map provides some immediate context for the player's surrounding area:\n\n1. A red path is drawn on the minimap leading from the character's current position towards the northwest direction. This generally indicates a suggested route the player should take to reach a specific destination or objective.\n2. There are various icons on the map, including a camp (teepee icon), a mail or delivery point (letter icon), a question mark which might indicate a point of interest or a stranger mission, some facility amenity icons (fork and knife for provisions, a tent for rest or camp upgrades), and a money bag icon which typically represents the camp's contribution box where the player can donate money.\n3. The player's character icon is in the center of the minimap, depicted as a white arrow, showing the current direction the character is facing.\n\nThe surrounding context of the minimap is vital for in-game navigation and decision-making. Based on the minimap, the player seems to be in a campsite or has just exited one. They have a clear destination set to the northwest, and based on the surrounding icons, there are several amenities and potential interactions available to them within the camp."
}

# 1. type: the type of the prompt, should be "gather_information"
# 2. description: the description of the image
```

Other parameters will be added.

#### 2.1.3 Template for Gather Information

```python
"""
Please describe the screenshot image in detail. Pay attention to any maps in the image, if any, especially key icons, red paths to follow, or created waypoints.
"""
```

Not the final template, to be improved.


### 2.2 Prompt for Decision Making
#### 2.2.1 Input Example for Decision Making

```python
input_example = {
    "type": "decision_making",
    "task_description": "mark the \"Saloon\" on a Map as the Waypoint via the Index and close the Map to return to the gameplay. You should only output one action",
    "skill_library": "[\n    {\n      \"function_expression\": \"open_map()\",\n      \"description\": \"Toggles the map view in the game, opening or closing it.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"add_marker()\",\n      \"description\": \"Places a marker on the map at the current mouse location by pressing 'z'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"add_waypoint()\",\n      \"description\": \"Sets a waypoint at the current selection or mouse location on the map by pressing 'enter'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"close_map()\",\n      \"description\": \"Closes the map view in the game by pressing 'esc'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"zoom_map()\",\n      \"description\": \"Zooms in on the map.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"reduce_map()\",\n      \"description\": \"Zooms out on the map.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"open_index()\",\n      \"description\": \"Opens the game index by pressing 'space'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"close_index()\",\n      \"description\": \"Closes the game index by pressing 'space'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"next_index_object()\",\n      \"description\": \"Cycles to the next index object after the index is open, using 'q'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"previous_index_object()\",\n      \"description\": \"Cycles to the previous index object after the index is open, using 'e'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"confirm_mouse_selection()\",\n      \"description\": \"Confirms a selection by simulating a mouse click.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"move_map(width,height)\",\n      \"description\": \"Moves the map based on specified width and height offsets.\",\n      \"parameters\": {\n        \"width\": \"Horizontal offset for the map movement.\",\n        \"height\": \"Vertical offset for the map movement.\"\n      }\n    },\n    {\n       \"fucntion_expresstion\": \"move_mouse_on_map(width,height,speed,relative)\",\n      \"description\": \"Moves the mouse on the map to specified width and height, with optional speed and relative position adjustment.\",\n      \"parameters\": {\n        \"width\": \"Horizontal position for mouse movement.\",\n        \"height\": \"Vertical position for mouse movement.\",\n        \"speed\": \"Speed of the mouse movement.\",\n        \"relative\": \"Boolean indicating if movement is relative to the current position.\"\n      }\n    },\n    {\n       \"fucntion_expresstion\": \"select_up_index_object()\",\n      \"description\": \"Selects the next object in the index upwards.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"select_down_index_object()\",\n      \"description\": \"Selects the next object in the index downwards.\",\n      \"parameters\": {}\n    }\n  ]",
    "decision_making_memory_description": "",
    "gathered_information_description": "",
    "number_of_execute_skills": 1,
    "image_introduction": [
        {
            "introduction": "the first image is the observation from the previous two timestep",
            "path": "./res/prompts/testing/decision_making/map_create_waypoint/screenshots/-1.jpg",
            "assistant": ""
        },
        {
            "introduction": "the second image is the previous timestep",
            "path": "./res/prompts/testing/decision_making/map_create_waypoint/screenshots/0.jpg",
            "assistant": ""
        }
    ],
    "output_format": "{\n    \"type\": \"decision_making\",\n    \"skill_steps\": [\"skill1(args1,args2)\"],\n    \"reasoning\": \"summary of the reasoning to chose the skill or sequence of skills\"\n}",
    "__comments__": "This is a template for decision making task, the key are (1) task_description: the goal of the current decision making task and the step-by-step logic to achieve it, (2) input_description: The prompt for gpt to understand the inputs, (3) skills_description: all the skills that gpt can choose from and their description, (4) decision_making_memory_description: input from memory to help decision making, (5) gathered_information_description: input from gather_information to help decision making, (6) output_description: the output format and requirements for decision making."
}

# 1. type: str, the type of the prompt, should be "decision_making"

# 2. task_description: str, the goal of the current decision making task

# 3. skill_library: str, the skills that GPT-4V can choose from. The specific format will be the one used in the skill library code.

"""
    "skill_library": "[\n    {\n      \"function_expression\": \"open_map()\",\n      \"description\": \"Toggles the map view in the game, opening or closing it.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"add_marker()\",\n      \"description\": \"Places a marker on the map at the current mouse location by pressing 'z'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"add_waypoint()\",\n      \"description\": \"Sets a waypoint at the current selection or mouse location on the map by pressing 'enter'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"close_map()\",\n      \"description\": \"Closes the map view in the game by pressing 'esc'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"zoom_map()\",\n      \"description\": \"Zooms in on the map.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"reduce_map()\",\n      \"description\": \"Zooms out on the map.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"open_index()\",\n      \"description\": \"Opens the game index by pressing 'space'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"close_index()\",\n      \"description\": \"Closes the game index by pressing 'space'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"next_index_object()\",\n      \"description\": \"Cycles to the next index object after the index is open, using 'q'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"previous_index_object()\",\n      \"description\": \"Cycles to the previous index object after the index is open, using 'e'.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"confirm_mouse_selection()\",\n      \"description\": \"Confirms a selection by simulating a mouse click.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"move_map(width,height)\",\n      \"description\": \"Moves the map based on specified width and height offsets.\",\n      \"parameters\": {\n        \"width\": \"Horizontal offset for the map movement.\",\n        \"height\": \"Vertical offset for the map movement.\"\n      }\n    },\n    {\n       \"fucntion_expresstion\": \"move_mouse_on_map(width,height,speed,relative)\",\n      \"description\": \"Moves the mouse on the map to specified width and height, with optional speed and relative position adjustment.\",\n      \"parameters\": {\n        \"width\": \"Horizontal position for mouse movement.\",\n        \"height\": \"Vertical position for mouse movement.\",\n        \"speed\": \"Speed of the mouse movement.\",\n        \"relative\": \"Boolean indicating if movement is relative to the current position.\"\n      }\n    },\n    {\n       \"fucntion_expresstion\": \"select_up_index_object()\",\n      \"description\": \"Selects the next object in the index upwards.\",\n      \"parameters\": {}\n    },\n    {\n       \"fucntion_expresstion\": \"select_down_index_object()\",\n      \"description\": \"Selects the next object in the index downwards.\",\n      \"parameters\": {}\n    }\n  ]"
"""
    # 3.1 function_expression: str, the call function expression of the skill
    # 3.2 description: str, the description of the skill
    # 3.3 parameters: dict, the arguments of the skill
    #    [args1]: any, the first argument of the skill, the key is the name of the argument, not only the "args1"
    #    [args2]: any, the second argument of the skill, the key is the name of the argument, not only the "args2"
        
# 4. decision_making_memory_description: str, input from memory to help decision making

# 5. gathered_information_description: str, input from gather_information to help decision making

# 6. number_of_execute_skills: int, the number of skills that will be executed in the decision making process

# 7. image_introduction: list of dict, the introduction of the images

"""
    "image_introduction":[
        {
            "introduction": "the first image is the observation from the previous timestep",
            "path": "./res/samples/screen_redline.jpg",
            "assistant": "response of the GPT-4V"
        },
        {
            "introduction": "the second image is the current observation",
            "path": "./res/samples/minimap_redline.jpg",
            "assistant": ""
        }
    ]
"""

    # 7.1 introduction: str, the introduction of the image
    # 7.2 path: str, the path of the image
    # 7.3 assistant: str, the response of the GPT-4V, if it is empty, indicates that this image has not had a reply from GPT-4V and will not have an assitant message

# 8. output_format: str, the output format and requirements for decision making

"""
    "output_format":"{\n    \"type\": \"decision_making\",\n    \"skill_steps\": [\"skill1(args1,args2)\"],\n    \"reasoning\": \"summary of the reasoning to chose the skill or sequence of skills\"\n}"
"""

    # 8.1 type: str, the type of the prompt, should be "decision_making"
    # 8.2 skill_steps: list of str, the sequence of function expression that GPT-4V chose
    # 8.3 reasoning: str, summary of the reasoning to chose the action or sequence of actions

# 9. __comments__: str, comments for the input_example
```

Calling GPT-4V message example:
```python
messages=[
            {
                "role": "system",
                "content": [
                    {
                      "type" : "text",
                      "text" : f"{system_prompts[0]}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_inputs["image_introduction"][0]["introduction"]}"
                    },
                   {
                       "type": "image_url",
                       "image_url": 
                           {
                               "url": f"data:image/jpeg;base64,{encode_image(["image_introduction"][0]["introduction"])}"
                           }
                   }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_inputs["image_introduction"][0]["introduction"]}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_inputs["image_introduction"][1]["introduction"]}"
                    },
                   {
                       "type": "image_url",
                       "image_url": 
                           {
                               "url": f"data:image/jpeg;base64,{encode_image(["image_introduction"][1]["introduction"])}"
                           }
                   }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_inputs[0]}"
                    }
                ]
            }
        ]
```

#### 2.2.2 Output Example for Decision Making

```python
output_example = {
    "type": "decision_making",
    "skill_steps": [
        "skill1(args1,args2)"
    ],
    "reasoning": "summary of the reasoning to chose the skill or sequence of skills",
    "__comments__": "skill_steps is a list of skills that gpt should choose from, reasoning is the summary of the reasoning to chose the skill or sequence of skills."
}

# 1. type: str, the type of the prompt, should be "decision_making"

# 2. skill_steps: list of str, the sequence of function expression that GPT-4V chose

# 3. reasoning: str, summary of the reasoning to chose the action or sequence of actions

# 4. __comments__: str, comments for the output_example
```

#### 2.2.3 Template for Decision Making

```python
"""
You are an assistant who assesses my progress in playing Red Dead Redemption 2 and provides expert guidance. Imagine you are playing Red Dead Redemption 2 with the keyboard and mouse, the image is the screenshot of your computer. Assist me in making a decision to complete a game task.

The task is to <$task_description$>.

I will give you extra information retrieved from memory and gathered from the game, you may use them to help your decision, neglect them if they are empty.

Memory:
<$decision_making_memory_description$>

Gathered_information:
<$gathered_information_description$>

Decomposed {<$task_description$>} to multiple automatic skills based on skills description, and choose some of them to finish the {<$task_description$>} and output the decomposed names of the sequence fo skills in the value of "skills".

<$skill_library$>

Based on the above input, including input images, what should be the next steps or one step? You should think step-by-step, and give your reasoning process in the value of "reasoning". The maximum number of skills you can include in the "skill_steps" must obey the requirement in {<$task_description$>}. Fill the "skill_steps" with the sequence of functions you chose to perform, if the function has a parameter, you should also decide the parameter for it, if it does not have a parameter just output "function_name()". Output an empty "skill_steps" list if no action needs to be take further. You should only output a JSON file without other explanation, do not give a markdown of a JSON file, and respond with the string format. Your output should be in the following format:
<$output_format$>
"""
```

### 2.3 Prompt for Success Detection
#### 2.3.1 Input Example for Success Detection

```python
input_example = {
    "type": "success_detection",
    "task_description": "mark a Waypoint via the Index and close the Map to return to the game",
    "image_instruction": [
        {
            "introduction": "the first image is the observation from the previous timestep",
            "path": "./res/samples/screen_redline.jpg",
            "assistant": ""
        },
        {
            "introduction": "the second image is the current observation",
            "path": "./res/samples/minimap_redline.jpg",
            "assistant": ""
        }
    ],
    "output_format": "{\n        \"type\": \"success_detection\",\n        \"task_description\": \"the task description\",\n        \"decision\":\n            {\n                \"criteria\": \"1.,2.,...\",\n                \"reasoning\": \"the reasoning for the decision\",\n                \"success\": false\n            }\n    }",
    "__comments__": "This is a template for success detection"
}

# 1. type: str, the type of the prompt, should be "success_detection"

# 2. task_description: str, the goal of the current success detection task

# 3. image_introduction: list of dict, the introduction of the images
    "image_introduction":[
        {
            "introduction": "the first image is the observation from the previous timestep",
            "path": "./res/samples/screen_redline.jpg",
            "assistant": "response of the GPT-4V"
        },
        {
            "introduction": "the second image is the current observation",
            "path": "./res/samples/minimap_redline.jpg",
            "assistant": ""
        }
    ]
    # 3.1 introduction: str, the introduction of the image
    # 3.2 path: str, the path of the image
    # 3.3 assistant: str, the response of the GPT-4V, if it is empty, indicates that this image has not had a reply from GPT-4V and will not have an assitant message

# 4. output_format: str, the output format and requirements for decision making
    "output_format":"{\n        \"type\": \"success_detection\",\n        \"task_description\": \"the task description\",\n        \"decision\":\n            {\n                \"criteria\": \"1.,2.,...\",\n                \"reasoning\": \"the reasoning for the decision\",\n                \"success\": false\n            }\n    }"

    # 4.1 type: str, the type of the prompt, should be "success_detection"
    # 4.2 task_description: str, the goal of the current success detection task
    # 4.3 decision:
    #    criteria: str, the criteria for success detection
    #    reasoning: str, the reasoning for success detection
    #    success: bool, whether the success detection is successful

# 5. __comments__: str, comments for the input_example
```

Calling GPT-4V message example:

```python
messages=[
            {
                "role": "system",
                "content": [
                    {
                      "type" : "text",
                      "text" : f"{system_prompts[0]}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_inputs["image_introduction"][0]["introduction"]}"
                    },
                   {
                       "type": "image_url",
                       "image_url": 
                           {
                               "url": f"data:image/jpeg;base64,{encode_image(["image_introduction"][0]["introduction"])}"
                           }
                   }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_inputs["image_introduction"][0]["introduction"]}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_inputs["image_introduction"][1]["introduction"]}"
                    },
                   {
                       "type": "image_url",
                       "image_url": 
                           {
                               "url": f"data:image/jpeg;base64,{encode_image(["image_introduction"][1]["introduction"])}"
                           }
                   }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_inputs[0]}"
                    }
                ]
            }
        ]
```

#### 2.3.2 Output Example for Success Detection

```python
output_example = {
    "type": "success_detection",
    "task_description": "map_create_waypoint",
    "decision":
        {
            "criteria": "The map must be open with the 'Saloon' marked as a Waypoint, and then the map must be closed to indicate the task completion.",
            "reasoning": "Both provided images show the in-game character standing near a campfire, with the mini-map visible on the bottom left corner. The mini-map does not provide sufficient information to determine if the 'Saloon' has been marked as a Waypoint via the Index, nor do these images show the main map being closed after marking a Waypoint. We can not see any waypoint marker on the mini-map nor any actions related to opening or navigating the full map.",
            "success": false
        },
    "__comments__": "This is a output example for success detection."
}

# 1. type: str, the type of the prompt, should be "success_detection"

# 2. task_description: str, the goal of the current success detection task

# 3. decision:
#    criteria: str, the criteria for success detection
#    reasoning: str, the reasoning for success detection
#    success: bool, whether the success detection is successful
        
# 4. __comments__: str, comments for the output_example
```

#### 2.3.3 Template for Success Detection

```python
"""
You are an assistant who assesses my progress in playing Red Dead Redemption 2 and provides expert guidance. Imagine you are playing Red Dead Redemption 2 with the keyboard and mouse, the image is the screenshot of your computer. Assist me in deciding whether the task has been successfully done.

Based on the above input, including input images. The task is to <$task_description$>. You need to think about the independent criteria to judge whether this task is fully completed. In addition, if there are any in-game prompts or instructions that are similar to {<$task_description$>}, it could indicate that the task has not been completed. If the previous state is completed and the current state is not completed, it also indicates that the task has not been completed. Output the criteria first in the value of "criteria". Based on images (<$image_descriptions$>), ask yourself whether one of the criteria is fully fulfilled for {task}. If fulfilled, then output true. If not, output false. Noted that the task must be completely accomplished to output a true. If some information from the previous action is not shown in these two images. you may assume the previous actions have been executed correctly. Output the think procedure in the value of "reasoning" and then output the answer. Note that you must output the answer true/false in the value of "success".

The output json object should follow this format:
<$output_format$>
"""
```

This format allows easy manual modifications and trying different changes, instead of having to edit objects and escape characters. Treat is as a text file (always in UTF-8).

Tags marked with **\<$ $\>** correspond to the values of the parameters passed as input when calling the backend large model. input_example.json files are just examples or the structure. The actual values will follow the same names and format in the real execution calls.

## Game & Skill Libraryg


### 1. Change settings before running the code.

#### 1.1 Mouse mode
Change mouse mode in the control setting to DirectInput.
| Original interface | Changed interface |
|------------|------------|
| ![Original interface](docs/images/raw_input.png) | ![Changed interface](docs/images/direct_input.png) |  

#### 1.2 Control
Change both two 'Tap and Hold Speed Control' to on, so we can press w twice to run, saving the need to press shift. Also change 'Aiming Mode' to 'Hold To Aim', so we do not need to keep pressing mouse right button when aiming.
| Original interface | Changed interface |
|------------|------------|
| ![Original interface](docs/images/move_control_previous.png) | ![Changed interface](docs/images/move_control_now.png) |  

#### 1.3 Game screen
Use Win+Tab to open two desktops. Put the code on the right desktop and open the game in the left desktop. The recommended default resolution to use is 1920x1080, but it can vary if the **16:9** aspect ratio is preserved. This means your screen must be of size (1920,1080), (2560,1440) or (3840,2160). DO NOT change the aspect ratio. Also, remember to set the game Screen Type to **Windowed Borderless**.
![game_position](docs/images/game_position.png)

#### 1.4 Mini-map
Remember to enlarge the icon to ensure the program is working well following: `SETTING -> DISPLAY ->  Radar Blip Size = Large` and  `SETTING -> DISPLAY ->  Map Blip Size = Large` and  `SETTING -> DISPLAY ->  Radar = Expanded` (or press Alt + X).

![](docs/images/enlarge_minimap.png)

![minimap_setting](docs/images/minimap_setting.png)

### 2. Three libraries for keyboard & mouse control  

- pyautogui: Used to simulate mouse clicks, including long mouse presses.   
- pydirectinput: Used to simulate the operation of the keyboard.  
- ahk: Used to simulate mouse swiping, including moveTo and dragTo.
  
### 3. File Structure
Most of our code are in the uac/gameio and uac/utils.

#### 3.1 uac/gameio/atomic_skills:
move.py: Includes turn, move_forward, mount horse and dismount horse.

map.py: Includes the operations needed to open the map and manipulate with the map.    

sell.py: Includes the actions needed to sell our products.    

buy.py: It is mainly divided into three parts:   
-   1. Interact with shopkeeper to buy products.   
-   2. The extra work required to buy clothes.   
-   3. Buy products on shelves.  

trade_utils.py: Stores the functions used to buy and sell products when trading.  

If you're just buying things from camp to town, you might at involve the following functions (for example: Buying fruit can):   

In the map.py:
-   open_map
-   close_map
-   add_waypoint
-   open_index
-   close_index
-   confirm_selection
-   select_down_index_object
-   select_up_index_object

In the buy.py
-   browse_catalogue
-   view_next_page
-   view_previous_page
-   select_product_type
-   buy_product
    

In the trade_utils.py
-   shopkeeper_interaction
-   cancel_shopkeeper_interaction
-   select_products
-   confirm_selection

#### 3.2 uac/gameio/composite_skills:
Currently, we only have 'cv_navigation' as a composite skill. Includes calculate_turn_angle (between the red line in the mini-map and the normal line, which is used in the cv_navigation).

#### 3.4 uac/gameio/lifecycle/ui_control.py
Contains code for switch game and code between two desktops and take_screenshot of the game.


## Running examples

We provide two "toy" examples so far.

4.1 openai_runner.py shows how to use the OpenAI provider and call GPT-4V directly to test prompts.

4.2 runner.py the agent run, involving other components.

The generated direction_map in the runs/<timestamp> should have a green line cross the white arrow and parallel to the red line (overlayed by the generated blue lines).
![direction_map](docs/images/direction_map.jpg) 


## Known issues
- You need to use time.sleep() between the execution of two skills for now.
- Planning and success detection sometimes not ideal.
- Very high latency and call errors in GPT-4V API.
