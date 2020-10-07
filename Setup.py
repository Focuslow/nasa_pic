import os, winshell
from win32com.client import Dispatch




def createShortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Nasa Wallpaper.lnk")
    target = os.path.dirname(os.path.realpath(__file__)) + '\\Nasa Wallpaper.exe'
    wDir = os.path.dirname(os.path.realpath(__file__))
    icon = os.path.dirname(os.path.realpath(__file__)) + '\\nasa.ico'
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    if icon == '':
        pass
    else:
        shortcut.IconLocation = icon
    shortcut.save()



def add_to_startup(file_path=""):
    USER_NAME = os.getlogin()
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(__file__))
    vbs_name = 'Nasa Wallpaper.vbs'
    bat_name = 'Nasa Wallpaper.bat'
    start = r'C:\Users\{}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'.format(USER_NAME)
    vbs_path = os.path.join(start,vbs_name)
    with open(bat_name, "w") as f:
        f.write("cd " + file_path + '\n' + 'start \"\" ' "\"Nasa Wallpaper.exe\"")
        f.close()

    with open(vbs_path, "w") as f:
        f.write("Set WshShell = CreateObject(\"WScript.Shell\")" + '\n' + 'WshShell.Run chr(34) & "' + file_path + '\\' + bat_name +'" & Chr(34), 0' + "\n"+ 'Set WshShell = Nothing')
        f.close()


createShortcut()
add_to_startup()