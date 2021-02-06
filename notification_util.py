import os
import platform
if 'Windows' == platform.system():
    import win32api
    import win32con


def show_notification(title, message):
    if 'Darwin' == platform.system():
        command = f'''
            osascript -e 'display notification "{message}" with title "{title}"'
        '''
        os.system(command)
    elif 'Windows' == platform.system():
        win32api.MessageBox(0, message,
                            "MessageBox",
                            win32con.MB_OK | win32con.MB_ICONWARNING)