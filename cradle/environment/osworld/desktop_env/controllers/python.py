import json
import logging
import random
from typing import Any, Dict, Optional

import requests

from desktop_env.envs.actions import KEYBOARD_KEYS

logger = logging.getLogger("desktopenv.pycontroller")


class PythonController:
    def __init__(self, vm_ip: str, pkgs_prefix: str = "import pyautogui; import time; pyautogui.FAILSAFE = False; {command}"):
        self.vm_ip = vm_ip
        self.http_server = f"http://{vm_ip}:5000"
        self.pkgs_prefix = pkgs_prefix  # fixme: this is a hacky way to execute python commands. fix it and combine it with installation of packages

    def get_screenshot(self):
        """
        Gets a screenshot from the server. With the cursor.
        """
        response = requests.get(self.http_server + "/screenshot")
        if response.status_code == 200:
            return response.content
        else:
            logger.error("Failed to get screenshot. Status code: %d", response.status_code)
            return None

    def get_terminal_output(self):
        """ Gets the terminal output from the server. None -> no terminal output or unexpected error.
        """
        response = requests.get(self.http_server + "/terminal")
        if response.status_code == 200:
            return response.json()["output"]
        else:
            logger.error("Failed to get terminal output. Status code: %d", response.status_code)
            return None

    def get_accessibility_tree(self) -> Optional[str]:

        response: requests.Response = requests.get(self.http_server + "/accessibility")
        if response.status_code == 200:
            return response.json()["AT"]
        else:
            logger.error("Failed to get accessibility tree. Status code: %d", response.status_code)
            return None

    def get_file(self, file_path: str):
        """
        Gets a file from the server.
        """
        response = requests.post(self.http_server + "/file", data={"file_path": file_path})
        if response.status_code == 200:
            logger.info("File downloaded successfully")
            return response.content
        else:
            logger.error("Failed to get file. Status code: %d", response.status_code)
            return None

    def execute_python_command(self, command: str) -> None:
        """
        Executes a python command on the server.
        It can be used to execute the pyautogui commands, or... any other python command. who knows?
        """
        # command_list = ["python", "-c", self.pkgs_prefix.format(command=command)]
        command_list = ["python", "-c", self.pkgs_prefix.format(command=command)]
        payload = json.dumps({"command": command_list, "shell": False})
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(self.http_server + "/execute", headers=headers, data=payload, timeout=90)
            if response.status_code == 200:
                logger.info("Command executed successfully: %s", response.text)
            else:
                logger.error("Failed to execute command. Status code: %d", response.status_code)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("An error occurred while trying to execute the command: %s", e)

    def execute_action(self, action: Dict[str, Any]):
        """
        Executes an action on the server computer.
        """
        if action in ['WAIT', 'FAIL', 'DONE']:
            return

        action_type = action["action_type"]
        parameters = action["parameters"] if "parameters" in action else {}
        move_mode = random.choice(
            ["pyautogui.easeInQuad", "pyautogui.easeOutQuad", "pyautogui.easeInOutQuad", "pyautogui.easeInBounce",
             "pyautogui.easeInElastic"])
        duration = random.uniform(0.5, 1)

        if action_type == "MOVE_TO":
            if parameters == {} or None:
                self.execute_python_command("pyautogui.moveTo()")
            elif "x" in parameters and "y" in parameters:
                x = parameters["x"]
                y = parameters["y"]
                self.execute_python_command(f"pyautogui.moveTo({x}, {y}, {duration}, {move_mode})")
            else:
                raise Exception(f"Unknown parameters: {parameters}")

        elif action_type == "CLICK":
            if parameters == {} or None:
                self.execute_python_command("pyautogui.click()")
            elif "button" in parameters and "x" in parameters and "y" in parameters:
                button = parameters["button"]
                x = parameters["x"]
                y = parameters["y"]
                if "num_clicks" in parameters:
                    num_clicks = parameters["num_clicks"]
                    self.execute_python_command(
                        f"pyautogui.click(button='{button}', x={x}, y={y}, clicks={num_clicks})")
                else:
                    self.execute_python_command(f"pyautogui.click(button='{button}', x={x}, y={y})")
            elif "button" in parameters and "x" not in parameters and "y" not in parameters:
                button = parameters["button"]
                if "num_clicks" in parameters:
                    num_clicks = parameters["num_clicks"]
                    self.execute_python_command(f"pyautogui.click(button='{button}', clicks={num_clicks})")
                else:
                    self.execute_python_command(f"pyautogui.click(button='{button}')")
            elif "button" not in parameters and "x" in parameters and "y" in parameters:
                x = parameters["x"]
                y = parameters["y"]
                if "num_clicks" in parameters:
                    num_clicks = parameters["num_clicks"]
                    self.execute_python_command(f"pyautogui.click(x={x}, y={y}, clicks={num_clicks})")
                else:
                    self.execute_python_command(f"pyautogui.click(x={x}, y={y})")
            else:
                raise Exception(f"Unknown parameters: {parameters}")

        elif action_type == "MOUSE_DOWN":
            if parameters == {} or None:
                self.execute_python_command("pyautogui.mouseDown()")
            elif "button" in parameters:
                button = parameters["button"]
                self.execute_python_command(f"pyautogui.mouseDown(button='{button}')")
            else:
                raise Exception(f"Unknown parameters: {parameters}")

        elif action_type == "MOUSE_UP":
            if parameters == {} or None:
                self.execute_python_command("pyautogui.mouseUp()")
            elif "button" in parameters:
                button = parameters["button"]
                self.execute_python_command(f"pyautogui.mouseUp(button='{button}')")
            else:
                raise Exception(f"Unknown parameters: {parameters}")

        elif action_type == "RIGHT_CLICK":
            if parameters == {} or None:
                self.execute_python_command("pyautogui.rightClick()")
            elif "x" in parameters and "y" in parameters:
                x = parameters["x"]
                y = parameters["y"]
                self.execute_python_command(f"pyautogui.rightClick(x={x}, y={y})")
            else:
                raise Exception(f"Unknown parameters: {parameters}")

        elif action_type == "DOUBLE_CLICK":
            if parameters == {} or None:
                self.execute_python_command("pyautogui.doubleClick()")
            elif "x" in parameters and "y" in parameters:
                x = parameters["x"]
                y = parameters["y"]
                self.execute_python_command(f"pyautogui.doubleClick(x={x}, y={y})")
            else:
                raise Exception(f"Unknown parameters: {parameters}")

        elif action_type == "DRAG_TO":
            if "x" in parameters and "y" in parameters:
                x = parameters["x"]
                y = parameters["y"]
                self.execute_python_command(
                    f"pyautogui.dragTo({x}, {y}, duration=1.0, button='left', mouseDownUp=True)")

        elif action_type == "SCROLL":
            # todo: check if it is related to the operating system, as https://github.com/TheDuckAI/DuckTrack/blob/main/ducktrack/playback.py pointed out
            if "dx" in parameters and "dy" in parameters:
                dx = parameters["dx"]
                dy = parameters["dy"]
                self.execute_python_command(f"pyautogui.hscroll({dx})")
                self.execute_python_command(f"pyautogui.vscroll({dy})")
            elif "dx" in parameters and "dy" not in parameters:
                dx = parameters["dx"]
                self.execute_python_command(f"pyautogui.hscroll({dx})")
            elif "dx" not in parameters and "dy" in parameters:
                dy = parameters["dy"]
                self.execute_python_command(f"pyautogui.vscroll({dy})")
            else:
                raise Exception(f"Unknown parameters: {parameters}")

        elif action_type == "TYPING":
            if "text" not in parameters:
                raise Exception(f"Unknown parameters: {parameters}")
            # deal with special ' and \ characters
            # text = parameters["text"].replace("\\", "\\\\").replace("'", "\\'")
            # self.execute_python_command(f"pyautogui.typewrite('{text}')")
            text = parameters["text"]
            self.execute_python_command("pyautogui.typewrite({:})".format(repr(text)))

        elif action_type == "PRESS":
            if "key" not in parameters:
                raise Exception(f"Unknown parameters: {parameters}")
            key = parameters["key"]
            if key.lower() not in KEYBOARD_KEYS:
                raise Exception(f"Key must be one of {KEYBOARD_KEYS}")
            self.execute_python_command(f"pyautogui.press('{key}')")

        elif action_type == "KEY_DOWN":
            if "key" not in parameters:
                raise Exception(f"Unknown parameters: {parameters}")
            key = parameters["key"]
            if key.lower() not in KEYBOARD_KEYS:
                raise Exception(f"Key must be one of {KEYBOARD_KEYS}")
            self.execute_python_command(f"pyautogui.keyDown('{key}')")

        elif action_type == "KEY_UP":
            if "key" not in parameters:
                raise Exception(f"Unknown parameters: {parameters}")
            key = parameters["key"]
            if key.lower() not in KEYBOARD_KEYS:
                raise Exception(f"Key must be one of {KEYBOARD_KEYS}")
            self.execute_python_command(f"pyautogui.keyUp('{key}')")

        elif action_type == "HOTKEY":
            if "keys" not in parameters:
                raise Exception(f"Unknown parameters: {parameters}")
            keys = parameters["keys"]
            if not isinstance(keys, list):
                raise Exception("Keys must be a list of keys")
            for key in keys:
                if key.lower() not in KEYBOARD_KEYS:
                    raise Exception(f"Key must be one of {KEYBOARD_KEYS}")

            keys_para_rep = "', '".join(keys)
            self.execute_python_command(f"pyautogui.hotkey('{keys_para_rep}')")

        elif action_type in ['WAIT', 'FAIL', 'DONE']:
            pass

        else:
            raise Exception(f"Unknown action type: {action_type}")

    # Record video
    def start_recording(self):
        """
        Starts recording the screen.
        """
        response = requests.post(self.http_server + "/start_recording")
        if response.status_code == 200:
            logger.info("Recording started successfully")
        else:
            logger.error("Failed to start recording. Status code: %d", response.status_code)

    def end_recording(self, dest: str):
        """
        Ends recording the screen.
        """
        try:
            response = requests.post(self.http_server + "/end_recording")
            if response.status_code == 200:
                logger.info("Recording stopped successfully")
                with open(dest, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            else:
                logger.error("Failed to stop recording. Status code: %d", response.status_code)
                return None
        except Exception as e:
            logger.error("An error occurred while trying to download the recording: %s", e)

    # Additional info
    def get_vm_platform(self):
        """
        Gets the size of the vm screen.
        """
        return self.execute_python_command("import platform; print(platform.system())")['output'].strip()

    def get_vm_screen_size(self):
        """
        Gets the size of the vm screen.
        """
        response = requests.post(self.http_server + "/screen_size")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Failed to get screen size. Status code: %d", response.status_code)
            return None

    def get_vm_window_size(self, app_class_name: str):
        """
        Gets the size of the vm app window.
        """
        response = requests.post(self.http_server + "/window_size", data={"app_class_name": app_class_name})
        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Failed to get window size. Status code: %d", response.status_code)
            return None

    def get_vm_wallpaper(self):
        """
        Gets the wallpaper of the vm.
        """
        response = requests.post(self.http_server + "/wallpaper")
        if response.status_code == 200:
            logger.info("Wallpaper downloaded successfully")
            return response.content
        else:
            logger.error("Failed to get wallpaper. Status code: %d", response.status_code)
            return None

    def get_vm_desktop_path(self):
        """
        Gets the desktop path of the vm.
        """
        response = requests.post(self.http_server + "/desktop_path")
        if response.status_code == 200:
            logger.info("Desktop path downloaded successfully")
            return response.json()["desktop_path"]
        else:
            logger.error("Failed to get desktop path. Status code: %d", response.status_code)
            return None

    def get_vm_directory_tree(self, path):
        """
        Gets the directory tree of the vm.
        """
        payload = json.dumps({"path": path})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(self.http_server + "/list_directory", headers=headers, data=payload)
        if response.status_code == 200:
            logger.info("Directory tree downloaded successfully")
            return response.json()["directory_tree"]
        else:
            logger.error("Failed to get directory tree. Status code: %d", response.status_code)
            return None
