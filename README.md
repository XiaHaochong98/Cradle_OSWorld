# UAC
Repository for the Universal Agent Control project.


Please setup your environment as:
```bash
conda create --name uac-dev python=3.10
conda activate uac-dev
pip3 install -r requirements.txt
```

Keep the requirements.txt file updated in your branch, but only add dependencies that are really required by the system.

runner.py is the entry point to run an agent. Currently not working code, just an introductory sample.

## Game & Skill Library
### 1. Change settings before running the code.

#### 1.1 Mouse mode
| Original interface | Changed interface |
|------------|------------|
| ![Original interface](images/image1.png) | ![Changed interface](images/image2.png) |  

#### 1.2 Game screen
Use win+tab to open two desktops. Put the code on the left desktop and open the game in the right desktop. The game should be scriptly at the top-left corner of the screen. The resolution we use is 2560X1600. 
![Original interface](images/game_position.png)

### 2. Three libraries for keyboard & mouse control  
- pyautogui: Used to simulate mouse clicks, including long mouse presses.   
- pydirectinput: Used to simulate the operation of the keyboard.  
- ahk: Used to simulate mouse swiping, including moveTo and dragTo.
  
### 3. File Structure
Most of our code are in the uac/skill_library and uac/utils.

#### 3.1 uac/skill_library/atomic_skills:
move.py: Includes turn, move_forward, mount horse and dismount horse.

map.py: Includes the operations needed to open the map and manipulate with the map.    

sell.py: Includes the actions needed to sell our products.    

buy.py: It is mainly divided into three parts:   
-   1. Interact with shopkeeper to buy products.   
-   2. The extra work required to buy clothes.   
-   3. Buy products on shelves.  
  
trade_utils.py: Stores the functions used to buy and sell products when trading.  

main.py: Calls functions from other python files.

If you're just buying things from camp to town, you might at involve the following functions(for example:Take buying fruit can):   
  
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

#### 3.2 uac/skill_library/composited_skills:
Currently, we only have the cv_navigation as the composited skill.

#### 3.3 uac/utils/angle_estimator.py:
Used for calcualte the angle between the red line in the mini-map and the normal line, which is used in the cv_navigation.

#### 3.4 uac/utils/UI_control.py
Contains code for switch game and code between two desktops and take_screenshot of the game.
You need to modify the screen_region and mini_map_region to fit your settings.

### 4. Toy example
We provide a toy exmple for the cv_navigation and map operation in skill_example.py. Modify the screen_region and mini_map_region to fit your screen at first.

### 5. Known issues
-   On some PCs, ahk.mouse_move turns twice the angle with the same parameters. 
-   You need to use time.sleep() between the execution of two skills.

