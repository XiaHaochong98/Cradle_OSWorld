import time

from uac.config import Config
from uac.gameio import IOEnvironment
from uac.gameio.skill_registry import register_skill, post_skill_wait

config = Config()
io_env = IOEnvironment()


@register_skill("zoom")
def zoom():
    """
    Enables zoom after opening the catalog.
    """
    io_env.mouse_click_button_and_hold(io_env.RIGHT_MOUSE_BUTTON)


@register_skill("cancel_zoom")
def cancel_zoom():
    """
    Releases the right mouse button to exit zoom.
    """
    io_env.mouse_release_button(io_env.RIGHT_MOUSE_BUTTON)


@register_skill("browse_catalogue")
def browse_catalogue(duration=1):
    """
    Opens the catalog by pressing the "e" key for a specified duration.
    Note: it must run the shopkeeper_interaction function before running this function.

    Parameters:
     - duration: The duration for which the "e" key is held down (default is 1 second).
    """
    io_env.key_hold('e', duration)

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("view_next_page")
def view_next_page():
    """
    Pressing "e" opens the next page in the catalog.
    """
    io_env.key_press('e')

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("view_previous_page")
def view_previous_page():
    """
    Pressing "q" returns to the previous page in the catalog.
    """
    io_env.key_press('q')

    post_skill_wait(config.DEFAULT_POST_ACTION_WAIT_TIME)


@register_skill("confirm_selection")
def confirm_selection():
    """
    Confirm the selected item in the menu.
    """
    io_env.key_press('enter')


@register_skill("select_next_product_type_in_menu")
def select_next_product_type_in_menu():
    """
    Move to the next product type in the menu by pressing the "down" arrow key.
    """
    io_env.key_press('down')


@register_skill("select_previous_product_type_in_menu")
def select_previous_product_type_in_menu():
    """
    Move to the previous product type in the menu by pressing the "up" arrow key.
    """
    io_env.key_press('up')


@register_skill("buy_product")
def buy_product():
    """
    Pressing "enter" purchases the selected product.
    """
    io_env.key_press('enter')


@register_skill("view_info")
def view_info():
    """
    Views product price and basic information by pressing "f".
    """
    io_env.key_press('f')


@register_skill("hide_info")
def hide_info():
    """
    Hides product price and basic information by pressing "f".
    """
    io_env.key_press('f')


@register_skill("product_details")
def product_details():
    """
    Views detailed information about the product by pressing "space".
    """
    io_env.key_press('space')


@register_skill("scroll_up_keyboard_for_info")
def scroll_up_keyboard_for_info():
    """
    Scrolls up in the catalog using the "up" arrow key.
    """
    io_env.key_press('up')


@register_skill("scroll_down_keyboard_for_info")
def scroll_down_keyboard_for_info():
    """
    Scrolls down in the catalog using the "down" arrow key.
    """
    io_env.key_press('down')


@register_skill("scroll_up_mouse_for_info")
def scroll_up_mouse_for_info():
    """
    Scrolls up in the catalog using the mouse wheel up.
    """
    io_env.mouse_click_button(io_env.WHEEL_UP_MOUSE_BUTTON)


@register_skill("scroll_down_mouse_for_info")
def scroll_down_mouse_for_info():
    """
    Scrolls down in the catalog using the mouse wheel down.
    """
    io_env.mouse_click_button(io_env.WHEEL_DOWN_MOUSE_BUTTON)


# Extra steps to buying clothing
@register_skill("try_clothing")
def try_clothing():
    """
    Views the option to try on clothes.
    """
    io_env.key_press('enter')


@register_skill("view_all_clothing")
def view_all_clothing():
    """
    Views all available clothing options.
    """
    io_env.key_press('space')


@register_skill("select_clothing")
def select_clothing():
    """
    Selects and buys the chosen clothing item.
    """
    io_env.key_press('enter')


# When trying on clothes, you can choose the color of the clothes
@register_skill("select_right_color")
def select_right_color():
    """
    Selects the color to the right using the keyboard arrow key.
    """
    io_env.key_press('right')


@register_skill("select_left_color")
def select_left_color():
    """
    Selects the color to the left using the keyboard arrow key.
    """
    io_env.key_press('left')


@register_skill("select_up_color")
def select_up_color():
    """
    Selects the color above using the keyboard arrow key.
    """
    io_env.key_press('up')


@register_skill("select_down_color")
def select_down_color():
    """
    Selects the color below using the keyboard arrow key.
    """
    io_env.key_press('down')


# Buy products on the shelves
@register_skill("examine_product")
def examine_product(duration=1):
    """
    Examines a product on the shelf for a specified duration.

    Parameters:
     - duration: The duration for which the "e" key is held down (default is 1 second).
    """
    io_env.key_hold('e', duration)


@register_skill("toggle_view")
def toggle_view():
    """
    Toggles the view mode.
    """
    io_env.key_press('v')


@register_skill("purchase_from_shelf")
def purchase_from_shelf(duration=1):
    """
    Buys a product from the shelf by holding down the "r" key for a specified duration.

    Parameters:
     - duration: The duration for which the "r" key is held down (default is 1 second).
    """
    io_env.key_hold('r', duration)


@register_skill("browse_shelf")
def browse_shelf(duration=1):
    """
    Opens the context menu on a shelf by holding down the right mouse button for a specified duration.

    Parameters:
     - duration: The duration for which the right mouse button is held down (default is 1 second).
    """
    io_env.mouse_click_button_and_hold(io_env.RIGHT_MOUSE_BUTTON, duration)


# @register_skill("select_product_type")
# def select_product_type():
#     """
#     Select the specified product type and pressing enter to view the contained products.
#     """
#     pydirectinput.press("enter")

@register_skill("select_product_type")
def select_product_type():
    """
    Moving the mouse over the specified product type and pressing enter
    allows viewing the contained products.
    """
    io_env.key_press('enter')


__all__ = [
    #"zoom",
    #"cancel_zoom",
    "browse_catalogue",
    "view_next_page",
    "view_previous_page",
    #"confirm_selection",
    #"select_product_type",
    #"select_next_product_type_in_menu",
    #"select_previous_product_type_in_menu",
    "buy_product",
    #"view_info",
    #"hide_info",
    # "product_details",
    # "scroll_up_keyboard_for_info",
    # "scroll_down_keyboard_for_info",
    # "scroll_up_mouse_for_info",
    # "scroll_down_mouse_for_info",
    # "try_clothing",
    # "view_all_clothing",
    # "select_clothing",
    # "select_right_color",
    # "select_left_color",
    # "select_up_color",
    # "select_down_color",
    # "examine_product",
    # "toggle_view",
    # "purchase_from_shelf",
    # "browse_shelf"
]

