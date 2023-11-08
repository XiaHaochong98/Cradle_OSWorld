# Skill Library

Please setup your environment as:
```bash
pip install pyautogui
pip install pydirectinput
pip install ahk
pip install ahk[binary]

```

Keep the requirements.txt file updated in your branch, but only add dependencies that are really required by the system.

runner.py is the entry point to run an agent. Currently not working code, just an introductory sample.

## skills interface
The code for trade is in the following file path: uac/skills/trade  
First, You have to change the Settings in the game.

| Original interface | Changed interface |
|------------|------------|
| ![Original interface](image1.png) | ![Changed interface](image2.png) |  

Second:  
- pyautogui: Used to simulate mouse clicks, including long mouse presses.   
- pydirectinput: Used to simulate the operation of the keyboard.  
- ahk: Used to simulate mouse swiping, including moveTo and dragTo.
  
Third:  

map.py: Includes the operations needed to mount horse and dismount horse, open the map and manipulate with the map.    

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
-   mount_horse
-   add_waypoint
-   open_index
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
