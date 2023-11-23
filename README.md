# UAC
Repository for the Universal Agent Control project.

Please setup your environment as:
```bash
conda create --name uac-dev python=3.10
conda activate uac-dev
pip3 install -r requirements.txt
```

To install Faiss:
```bash
# CPU-only version
conda install -c pytorch faiss-cpu=1.7.4 mkl=2021 blas=1.0=mkl
# GPU(+CPU) version
conda install -c pytorch -c nvidia faiss-gpu=1.7.4 mkl=2021 blas=1.0=mkl
```

Keep the requirements.txt file updated in your branch, but only add dependencies that are really required by the system.

runner.py is the entry point to run an agent. Currently not working code, just an introductory sample.


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

**>>> Allways check the /main branch for the latest examples!!!**

#### Input Examples

Sample json:
```
{
    "type": "success_detection",
    "goal": "Go to store",
    "image_paths": ["./res/samples/screen_redline.jpg", "./res/samples/minimap_redline.jpg"],
    "image_descriptions": "the images sent to you are: 1. the screenshot for the current observation, and 2. the emphasized minimap image",
    "output_format":"{\n  \"type\": \"success_detection\",\n  \"goal\": \"Go to store\",\n  \"decision\": \n    {\n      \"criteria\": \"1.\",\n      \"reason\": \"The selected place 'Grub' in the index is not the target place 'General Store'.\",\n      \"success\": false\n    }\n}"
}
```

As shown, such file illustrates the **parameters** needed to fill a prompt template (in this case, the "success detection" one). Also in this example, the format of the parameter "output-format" is exactly the same as the corresponding "output_example" json file.

Not all input examples need the same parameters. Only the parameters required in a specific template (".prompt" file).

#### Output Examples

Sample json:
```
{
  "type": "success_detection",
  "goal": "Open the map",
  "decision":
    {
      "criteria": "1.xx, 2.xx",
      "reasoning": "Since the map is currently not open and it is the first step required to mark a waypoint, we need to open the map using the 'open_map' function.",
      "success": false
    }
}
```

### Prompt Template Examples 

Sample prompt:
```
The screenshot is a map describing the game world. On the left side of the screenshot, there is an index listing all the possible places to be chosen as the waypoint.

The index lists all the possible places in a sequential manner. The selected place is marked with a red rectangle. Your task is to decide whether the selected place is the same as the target place. Your input contains a screenshot of the map containing the index list and text of the target place. Your output should be a JSON file that contains the distance of the target place to the current selected place. 

The JSON file should be in the following format:
<$output_format$>
```

This format allows easy manual modifications and trying different changes, instead of having to edit objects and escape characters. Treat is as a text file (always in UTF-8).

Tags marked with **\<$ $\>** correspond to the values of the parameters passed as input when calling the backend large model. input_example.json files are just examples or the structure. The actual values will follow the same names and format in the real execution calls.


## Game & Skill Library


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
Use Win+Tab to open two desktops. Put the code on the right desktop and open the game in the left desktop. The recommended default resolution to use is 1920x1080, but it can vary if the **16:9** aspect ratio is preserved (like 2560x1440 or 3840x2160). DO NOT change the aspect ratio. Also, remember to set the game Screen Type to **Windowed Borderless**.
![game_position](docs/images/game_position.png)

#### 1.4 Mini-map
Press Alt and press X to make the mini-map expand.
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
