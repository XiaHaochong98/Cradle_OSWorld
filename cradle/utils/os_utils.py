import psutil
import platform

if platform.system() == "Windows":
    import win32gui
    import win32process


def getProcessIDByName(process_name):
    pids = []

    for proc in psutil.process_iter():
        if process_name in proc.name():
            pids.append(proc.pid)

    return pids


def getProcessNameByPID(process_id):
    for proc in psutil.process_iter():
        if process_id == proc.pid():
            return proc.pid()

    return None


def getProcessIDByWindowHandle(window_handle):

    pid = None

    if platform.system() == "Windows":
        _, pid = win32process.GetWindowThreadProcessId(window_handle)
    else:
        raise NotImplementedError("This function is only implemented for Windows.")

    return pid
