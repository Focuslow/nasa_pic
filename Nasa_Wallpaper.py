from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError, HTTPError
import os
from datetime import datetime, timedelta
import ctypes, win32con
import time
import shutil
import sys
from PySide2 import QtWidgets, QtGui, QtCore
import webbrowser


def internet_on():
    try:
        urlopen('http://google.com', timeout=1)
        return True
    except URLError as err:
        return False


def timer_set(path):
    if os.path.isfile(path + '\\' + 'cfg.txt'):
        with open(path + '\\' + 'cfg.txt', 'r') as file:
            txt = file.readlines()
            for line in range(2):
                if '\n' in txt[line]:
                    value = txt[line][txt[line].index(':') + 2:-1]
                else:
                    value = txt[line][txt[line].index(':') + 2:]

                if value == "True":
                    continue
                elif value == "False":
                    return False

                else:
                    return value

            file.close()
    else:
        return False


def changeToCurrent(path):
    file_name = getWallpaper()
    setDate = file_name[-14:-4]
    date = datetime.strftime(datetime.now(), "%d_%m_%Y")
    if setDate is not date:
        setDate_object = datetime.strptime(date, "%d_%m_%Y")
        name = date
        pic_path = path + "\\" + name + "\\" + name + ".jpg"
        if os.path.isfile(pic_path):
            setWallpaper(pic_path)

        else:
            dates = get_date_img_list(path)
            date = datetime.strftime(dates[-1], "%d_%m_%Y")
            name = date
            pic_path = path + "\\" + name + "\\" + name + ".jpg"
            if os.path.isfile(pic_path):
                setWallpaper(pic_path)


def walk(word):
    for i in range(len(word)):
        if i in [0, 1, 3, 4, 6, 7, 8, 9]:
            if word[i].isnumeric():
                if i == 9:
                    return True
                else:
                    continue
            else:
                return False
        elif i in [2, 5]:
            if word[i] == "_":
                continue
            else:
                return False


def get_date_dir_list(path):
    item_list = os.listdir(path)
    dir_list = []
    for f in item_list:
        if os.path.isdir(path + "\\" + f):
            dir_list.append(f)
    date_list = []
    for item in dir_list:
        if walk(item):
            date_list.append(datetime.strptime(item, "%d_%m_%Y"))

    date_list.sort()

    return date_list


def get_date_img_list(path):
    item_list = os.listdir(path)
    dir_list = []
    for f in item_list:
        if os.path.isdir(path + "\\" + f):
            if os.path.isfile(path + "\\" + f + "\\" + f + ".jpg"):
                dir_list.append(f)
    date_list = []
    for item in dir_list:
        if walk(item):
            date_list.append(datetime.strptime(item, "%d_%m_%Y"))

    date_list.sort()

    return date_list


def picDelete(path):
    date = datetime.now() - timedelta(days=50)
    name = date.strftime("%d_%m_%Y")
    if os.path.exists(path + "\\" + name):

        try:
            shutil.rmtree(path + "\\" + name)
        except PermissionError:
            try:
                os.remove(path + "\\" + name + "\\" + name + ".jpg")
            except FileNotFoundError:
                pass

    dirs = get_date_dir_list(path)
    imgs = get_date_img_list(path)

    for dir in dirs:
        if dir not in imgs:
            try:
                name = dir.strftime("%d_%m_%Y")
                os.rmdir(path + "\\" + name)
                shutil.rmtree(path + "\\" + name)
            except FileNotFoundError:
                pass
            except PermissionError:
                pass


def getWallpaper():
    ubuf = ctypes.create_unicode_buffer(512)
    ctypes.windll.user32.SystemParametersInfoW(win32con.SPI_GETDESKWALLPAPER, len(ubuf), ubuf, 0)
    return ubuf.value


def setWallpaper(path):
    changed = win32con.SPIF_UPDATEINIFILE | win32con.SPIF_SENDCHANGE
    ctypes.windll.user32.SystemParametersInfoW(win32con.SPI_SETDESKWALLPAPER, 0, path, changed)


def getUrl(date):
    end = date[-2:] + date[3:5] + date[0:2]
    url = "https://apod.nasa.gov/apod/" + "ap" + end + ".html"
    try:
        page = urlopen(url)
    except HTTPError as error:
        raise error
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    b = soup.find_all("img")
    if b == []:
        return 0
    else:
        local = b[0].get('src')
        pic_url = "https://apod.nasa.gov/apod/" + local
        a = pic_url
        return pic_url


def modifyDate(path):
    date = datetime.now()
    string = date.strftime('%d_%m_%Y')
    with open(path + '\\' + "date.txt", "w+") as file:
        file.write(string)
        file.close()


def sameDate(path):
    try:
        os.mkdir(path)
    except OSError:
        pass
    date = datetime.now()
    string = date.strftime('%d_%m_%Y')
    if os.path.exists(path + '\\' + 'date.txt'):
        with open(path + '\\' + 'date.txt', "r") as file:
            old_date = file.read()
            file.close()

        if string == old_date:
            return True
        else:
            return False

    else:
        with open(path + '\\' + "date.txt", "w+") as file:
            file.write(string)
            file.close()
            return False


def get_pic(path, date):
    if internet_on():
        try:
            url_path = getUrl(date)
        except HTTPError as error:
            raise error
        if url_path == 0:
            return 1
        else:
            try:
                os.mkdir(path + "\\" + date)
            except OSError:
                pass
            os.chdir(path + "\\" + date)
            urlretrieve(url_path, date + ".jpg")
            pic_path = project_path + "\\" + date + "\\" + date + ".jpg"

        return pic_path
    else:
        return False

def add_to_startup(file_path=""):
    USER_NAME = os.getlogin()
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(__file__))
    vbs_name = 'Nasa Wallpaper.vbs'
    bat_name = 'Nasa Wallpaper.bat'
    start = r'C:\Users\{}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'.format(USER_NAME)
    vbs_path = os.path.join(start,vbs_name)

    if not os.path.isfile(bat_name):
        with open(bat_name, "w") as f:
            f.write("cd " + file_path + '\n' + 'start \"\" ' "\"Nasa Wallpaper.exe\"")
            f.close()

    if not os.path.isfile(vbs_path):
        with open(vbs_path, "w") as f:
            f.write("Set WshShell = CreateObject(\"WScript.Shell\")" + '\n' + 'WshShell.Run chr(34) & "' + file_path + '\\' + bat_name +'" & Chr(34), 0' + "\n"+ 'Set WshShell = Nothing')
            f.close()

def remove_startup(file_path=""):
    USER_NAME = os.getlogin()
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(__file__))
    vbs_name = 'Nasa Wallpaper.vbs'
    bat_name = 'Nasa Wallpaper.bat'
    start = r'C:\Users\{}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'.format(USER_NAME)
    vbs_path = os.path.join(start, vbs_name)

    if os.path.isfile(file_path+"\\"+bat_name):
        os.remove(file_path+"\\"+bat_name)

    if os.path.isfile(vbs_path):
        os.remove(vbs_path)


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, path, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'Nasa wallpaper changer v1.3')
        self.project_path = path
        self.update()
        self.interval = 300000
        # self.interval = 5000
        self.startTimer(self.interval)
        self.timer = timer_set(project_path)  # 1 day interval of change
        self.timer_add = self.interval
        self.internet = internet_on()
        menu = QtWidgets.QMenu(parent)

        switch_back = menu.addAction("Change wallpaper one back")
        switch_back.triggered.connect(self.switch_back)
        switch_back.setIcon(QtGui.QIcon("Actions-go-previous-icon.png"))

        switch_next = menu.addAction("Change wallpaper one forward")
        switch_next.triggered.connect(self.switch_next)
        switch_next.setIcon(QtGui.QIcon("Actions-go-next-icon.png"))

        switch_current = menu.addAction("Change wallpaper to newest")
        switch_current.triggered.connect(self.switch_current)
        switch_current.setIcon(QtGui.QIcon("current-icon.png"))

        delete = menu.addAction("Delete picture")
        delete.triggered.connect(self.delete)
        delete.setIcon(QtGui.QIcon("delete.png"))

        info = menu.addAction("Picture info")
        info.triggered.connect(self.info)
        info.setIcon(QtGui.QIcon("Info-icon.png"))

        cfg = menu.addAction("Settings")
        cfg.triggered.connect(self.cfg)
        cfg.setIcon(QtGui.QIcon("setting.png"))

        exit_ = menu.addAction("Exit")
        exit_.triggered.connect(lambda: sys.exit())
        exit_.setIcon(QtGui.QIcon("Close-2-icon.png"))

        menu.addSeparator()
        self.setContextMenu(menu)

    def switch_back(self):
        file_name = getWallpaper()
        setDate = file_name[-14:-4]

        try:
            newDate_obj = datetime.strptime(setDate, "%d_%m_%Y") - timedelta(days=1)

        except ValueError:
            newDate_obj = datetime.strptime(datetime.now(), "%d_%m_%Y") - timedelta(days=1)

        try:
            dir_dates = get_date_dir_list(project_path)
            if newDate_obj in dir_dates:
                name = datetime.strftime(newDate_obj, "%d_%m_%Y")
                dir_path = project_path + "\\" + name + "\\"
                pic_path = project_path + "\\" + name + "\\" + name + ".jpg"

                if os.path.isdir(dir_path):
                    if os.path.isfile(pic_path):
                        setWallpaper(pic_path)

                    else:
                        newDate_obj = newDate_obj - timedelta(days=1)
                        newDate = datetime.strftime(newDate_obj, "%d_%m_%Y")
                        try:
                            os.mkdir(project_path + "\\" + newDate)
                            os.rmdir(project_path + "\\" + newDate)
                            fail = get_pic(project_path, newDate)
                            if fail:
                                if fail == 1:
                                    while fail == 1:
                                        newDate_obj = newDate_obj - timedelta(days=1)
                                        newDate = datetime.strftime(newDate_obj, "%d_%m_%Y")
                                        fail = get_pic(project_path, newDate)

                                    setWallpaper(project_path + "\\" + newDate + "\\" + newDate + ".jpg")
                                else:
                                    setWallpaper(get_pic(project_path, newDate))
                            else:
                                return 0
                        except OSError:
                            dir_path = project_path + "\\" + newDate
                            pic_path = project_path + "\\" + newDate + "\\" + newDate + ".jpg"
                            i = 0
                            while os.path.isdir(dir_path) and not os.path.isfile(pic_path):
                                newDate_obj = newDate_obj - timedelta(days=1)
                                newDate = datetime.strftime(newDate_obj, "%d_%m_%Y")
                                pic_path = project_path + "\\" + newDate + "\\" + newDate + ".jpg"
                                dir_path = project_path + "\\" + newDate
                                i = 1

                            if i == 0 or os.path.isfile(pic_path):
                                setWallpaper(pic_path)
                            else:
                                fail = get_pic(project_path, newDate)
                                if fail:
                                    if fail == 1:
                                        while fail == 1:
                                            newDate_obj = newDate_obj - timedelta(days=1)
                                            newDate = datetime.strftime(newDate_obj, "%d_%m_%Y")
                                            fail = get_pic(project_path, newDate)

                                        setWallpaper(project_path + "\\" + newDate + "\\" + newDate + ".jpg")
                                    else:
                                        setWallpaper(get_pic(project_path, newDate))
                                else:
                                    return 0

            else:
                if os.path.exists(project_path + '\\' + 'deleted.txt'):
                    with open(project_path + '\\' + 'deleted.txt', "r") as file:
                        string_del = file.read()
                        deleted = string_del.split(";")
                        file.close()
                name = datetime.strftime(newDate_obj, "%d_%m_%Y")
                if os.path.exists(project_path + '\\' + 'deleted.txt'):
                    while name in deleted:
                        newDate_obj = newDate_obj - timedelta(days=1)
                        name = datetime.strftime(newDate_obj, "%d_%m_%Y")
                        if name not in deleted:
                            newDate = datetime.strftime(newDate_obj, "%d_%m_%Y")
                            fail = get_pic(project_path, newDate)
                            if fail:
                                if fail == 1:
                                    newDate_obj = newDate_obj - timedelta(days=1)
                                    name = datetime.strftime(newDate_obj, "%d_%m_%Y")
                                elif fail != 1:
                                    pic_path = project_path + "\\" + name + "\\" + name + ".jpg"
                                    if os.path.isfile(pic_path):
                                        setWallpaper(pic_path)
                                        return None
                            else:
                                return 0
                if dir_dates.index(datetime.strptime(setDate, "%d_%m_%Y")) == 0:
                    newDate = datetime.strftime(newDate_obj, "%d_%m_%Y")
                    fail = get_pic(project_path, newDate)
                    if fail:
                        if fail == 1:
                            while fail == 1:
                                newDate_obj = newDate_obj - timedelta(days=1)
                                newDate = datetime.strftime(newDate_obj, "%d_%m_%Y")
                                fail = get_pic(project_path, newDate)
                            setWallpaper(project_path + "\\" + newDate + "\\" + newDate + ".jpg")
                        else:
                            setWallpaper(project_path + "\\" + newDate + "\\" + newDate + ".jpg")
                    else:
                        return 0
                else:
                    # newDate_object = dir_dates[dir_dates.index(datetime.strptime(setDate, "%d_%m_%Y")) - 1]
                    # name = datetime.strftime(newDate_object, "%d_%m_%Y")
                    pic_path = project_path + "\\" + name + "\\" + name + ".jpg"
                    os.listdir(project_path)

                    if os.path.isfile(pic_path):
                        setWallpaper(pic_path)

                    else:
                        if get_pic(project_path, name):
                            setWallpaper(pic_path)

        except ValueError:
            pass
        except IndexError:
            pass

    def switch_next(self):
        file_name = getWallpaper()
        setDate = file_name[-14:-4]
        try:
            setDate_obj = datetime.strptime(setDate, "%d_%m_%Y")

            if datetime.now() > setDate_obj:
                newDate_object = setDate_obj + timedelta(days=1)
                dir_dates = get_date_img_list(project_path)
                if newDate_object in dir_dates:
                    name = datetime.strftime(newDate_object, "%d_%m_%Y")
                    pic_path = project_path + "\\" + name + "\\" + name + ".jpg"
                    os.listdir(project_path)
                    if os.path.isfile(pic_path):
                        setWallpaper(pic_path)

                else:
                    dir_dates_temp = dir_dates.copy()
                    if dir_dates_temp.index(setDate_obj) == len(dir_dates_temp) - 1:
                        if os.path.exists(project_path + '\\' + 'deleted.txt'):
                            with open(project_path + '\\' + 'deleted.txt', "r") as file:
                                string_del = file.read()
                                deleted = string_del.split(";")
                                file.close()
                        else:
                            deleted = ""

                        newDate_object = setDate_obj + timedelta(days=1)
                        while newDate_object < datetime.now():
                            newDate = datetime.strftime(newDate_object, "%d_%m_%Y")
                            if newDate in deleted:
                                newDate_object = setDate_obj + timedelta(days=1)
                                continue
                            else:
                                fail = get_pic(project_path, newDate)
                                if fail:
                                    continue
                                elif fail == 1:
                                    break
                                else:
                                    setWallpaper(project_path + "\\" + newDate + "\\" + newDate + ".jpg")
                    else:
                        newDate_object = dir_dates_temp[dir_dates_temp.index(setDate_obj) + 1]
                        name = datetime.strftime(newDate_object, "%d_%m_%Y")
                        pic_path = project_path + "\\" + name + "\\" + name + ".jpg"
                        os.listdir(project_path)

                        if os.path.isfile(pic_path):
                            setWallpaper(pic_path)



        except ValueError:
            pass
        except IndexError:
            pass

    def switch_current(self):
        changeToCurrent(project_path)

    def delete(self):
        file_name = getWallpaper()
        setDate = file_name[-14:-4]
        try:
            setDate_obj = datetime.strptime(setDate, "%d_%m_%Y")
            self.switch_next()
            new = getWallpaper()
            if new == file_name:
                # with open(project_path+"\\date.txt", "w") as file:
                #     file.write("")
                self.switch_back()
                new = getWallpaper()
                if new == file_name:
                    setWallpaper("//xx")

            if os.path.exists(file_name[0:-14]):
                try:
                    shutil.rmtree(file_name[0:-14])
                except PermissionError:
                    try:
                        os.remove(file_name)
                    except FileNotFoundError:
                        pass

            with open(project_path + '\\' + 'deleted.txt', "a") as file:
                file.write(setDate + ";")
                file.close()

        except ValueError:
            pass

    def info(self):
        file_name = getWallpaper()
        setDate = file_name[-14:-4]
        try:
            setDate_obj = datetime.strptime(setDate, "%d_%m_%Y")
            url = "https://apod.nasa.gov/apod/" + "ap" + setDate[-2:] + setDate[3:5] + setDate[
                                                                                       0:2] + ".html"  # ap200907.html 7th september 2020
            webbrowser.open(url)

        except ValueError:
            pass

    def cfg(self):
        self.cfgwin = SettingsMenu()
        self.cfgwin.setupui(self.cfgwin, self)
        self.cfgwin.show()

    def timerEvent(self, event: QtCore.QTimerEvent):
        self.update()
        if self.timer:
            if int(self.timer) <= self.timer_add:
                self.cycle()
                self.timer_add = self.interval
            else:
                self.timer_add += self.interval

    def update(self):
        if internet_on():
            same = sameDate(project_path)
            httpfail = False
            # print(same)
            if not same:
                date = datetime.now()
                name = date.strftime("%d_%m_%Y")
                try:
                    pic_path = get_pic(project_path, name)
                except HTTPError:
                    httpfail = True
                    pic_path = 0

                    with open(project_path + '\\' + 'date.txt', "w+") as file:
                        date_old = datetime.now() - timedelta(days=1)
                        name_old = date_old.strftime("%d_%m_%Y")
                        file.write(name_old)
                        file.close()

                i = 0
                while (pic_path == 0 or i < 20) and (httpfail == True or len(get_date_img_list(project_path)) == 0):
                    date = date - timedelta(days=1)
                    date = datetime(date.year, date.month, date.day)
                    if date not in get_date_img_list(project_path):
                        name = date.strftime("%d_%m_%Y")
                        try:
                            pic_path = get_pic(project_path, name)
                        except HTTPError:
                            pic_path = 0
                        i += 1

                        if pic_path:
                            httpfail = False

                    else:
                        name = date.strftime("%d_%m_%Y")
                        pic_path = project_path + "\\" + name + "\\" + name + ".jpg"
                        if pic_path == getWallpaper():
                            break
                        else:
                            setWallpaper(pic_path)
                            break

                        if not httpfail:
                            modifyDate(project_path)

                if pic_path != 0:
                    setWallpaper(pic_path)
                    picDelete(project_path)

    def cycle(self):
        imgs = get_date_img_list(project_path)
        if not len(imgs) > 1:
            return 0
        else:
            date = getWallpaper()[-14:-4]
            date_obj = datetime.strptime(date, '%d_%m_%Y')
            current = imgs.index(date_obj)
            new_ppr_date = imgs[current - 1]
            new_ppr = datetime.strftime(new_ppr_date, '%d_%m_%Y')
            path = project_path + "\\" + new_ppr + "\\" + new_ppr + ".jpg"
            setWallpaper(path)


class SettingsMenu(QtWidgets.QWidget):
    def setupui(self, Window, main):
        self.parent = main
        Window.setObjectName("Settings")
        Window.setWindowTitle("Settings")
        Window.resize(400, 320)
        Window.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("nasa.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Window.setWindowIcon(icon)

        self.mainwin = QtWidgets.QWidget(Window)
        self.mainlayout = QtWidgets.QVBoxLayout()
        self.mainlayout.setContentsMargins(20, 20, 20, 20)
        self.mainlayout.setAlignment(QtCore.Qt.AlignHCenter)
        self.mainlayout.setSpacing(8)
        self.mainwin.setLayout(self.mainlayout)

        self.lay1 = QtWidgets.QHBoxLayout(self.mainwin)

        self.lay8 = QtWidgets.QHBoxLayout(self.mainwin)
        self.lay8.setContentsMargins(5, 0, 0, 0)
        self.lay8.setSpacing(164)

        self.lay2 = QtWidgets.QHBoxLayout(self.mainwin)
        self.lay2.setContentsMargins(5, 0, 0, 0)
        self.lay2.setSpacing(20)

        self.lay3 = QtWidgets.QHBoxLayout(self.mainwin)
        self.lay3.setContentsMargins(30, 10, 0, -5)

        self.lay4 = QtWidgets.QHBoxLayout(self.mainwin)
        self.lay4.setContentsMargins(20, 0, 0, 0)
        self.lay4.setSpacing(18)

        self.lay5 = QtWidgets.QVBoxLayout(self.mainwin)
        self.lay5.setContentsMargins(0, 10, 0, 0)
        self.lay5.setAlignment(QtCore.Qt.AlignCenter)
        self.lay5.setSpacing(10)

        self.lay6 = QtWidgets.QVBoxLayout(self.mainwin)
        self.lay6.setAlignment(QtCore.Qt.AlignCenter)
        self.lay6.setSpacing(10)

        self.lay7 = QtWidgets.QHBoxLayout(self.mainwin)
        self.lay7.setContentsMargins(0, 20, 0, 0)
        self.lay7.setAlignment(QtCore.Qt.AlignCenter)
        self.lay7.setSpacing(10)

        self.mainlayout.addLayout(self.lay1)
        self.mainlayout.addLayout(self.lay8)
        self.mainlayout.addLayout(self.lay2)
        self.mainlayout.addLayout(self.lay3)
        self.mainlayout.addLayout(self.lay4)
        self.mainlayout.addLayout(self.lay5)
        self.mainlayout.addLayout(self.lay6)
        self.mainlayout.addLayout(self.lay7)

        self.delbtntxt = QtWidgets.QLabel(self.mainwin)
        self.delbtntxt.setText("Reset list of deleted pictures")
        self.delbtntxt.setFixedHeight(30)
        self.delbtntxt.setFixedWidth(200)

        self.delbtn = QtWidgets.QPushButton(self.mainwin)
        self.delbtn.setFixedHeight(30)
        self.delbtn.setFixedWidth(100)
        self.delbtn.setText("Reset")

        self.lay1.addWidget(self.delbtntxt)
        self.lay1.addWidget(self.delbtn)

        self.checkbox0txt = QtWidgets.QLabel(self.mainwin)
        self.checkbox0txt.setText("Launch after startup")

        self.checkbox0 = QtWidgets.QCheckBox(self.mainwin)

        self.lay8.addWidget(self.checkbox0txt)
        self.lay8.addWidget(self.checkbox0)

        self.radiotxt = QtWidgets.QLabel(self.mainwin)
        self.radiotxt.setText("Change wallpaper with interval chosen below")

        self.radiobtn = QtWidgets.QCheckBox(self.mainwin)

        self.lay2.addWidget(self.radiotxt)
        self.lay2.addWidget(self.radiobtn)

        self.regslider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self.mainwin)
        self.regslider.setFixedWidth(300)
        self.regslider.setRange(1, 6)
        self.regslider.setTickInterval(1)
        self.regslider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.regslider.setSingleStep(1)
        self.switcher = {
            1: 1800000,  # 30mins in milisec
            2: 1800000 * 2,  # hour
            3: 1800000 * 4,  # 2h
            4: 1800000 * 8,  # 4h
            5: 1800000 * 16,
            6: 1800000 * 32
        }
        if self.parent.timer in list(self.switcher.values()):
            position = list(self.switcher.values()).index(self.parent.timer) + 1
        else:
            position = 6
        self.regslider.setSliderPosition(position)
        self.regslider.setEnabled(False)
        self.lay3.addWidget(self.regslider)
        ticks = ['30 Min', '  Hour', '2 Hours', '4 Hours', '8 Hours', 'Day']
        for i in range(6):
            label = QtWidgets.QLabel(self.mainwin)
            label.setText(ticks[i])
            self.lay4.addWidget(label)

        self.delpicbtntxt = QtWidgets.QLabel(self.mainwin)
        self.delpicbtntxt.setText("Delete all downloaded pictures and reset")
        self.delpicbtntxt.setFixedHeight(30)
        self.delpicbtntxt.setFixedWidth(250)

        self.delpicsbtn = QtWidgets.QPushButton(self.mainwin)
        self.delpicsbtn.setFixedHeight(30)
        self.delpicsbtn.setFixedWidth(100)
        self.delpicsbtn.setText("Delete all")

        self.lay5.addWidget(self.delpicbtntxt)
        self.lay6.addWidget(self.delpicsbtn)

        self.leavebtn = QtWidgets.QPushButton(self.mainwin)
        self.leavebtn.setFixedHeight(30)
        self.leavebtn.setFixedWidth(100)
        self.leavebtn.setText("Leave")

        self.savebtn = QtWidgets.QPushButton(self.mainwin)
        self.savebtn.setFixedHeight(30)
        self.savebtn.setFixedWidth(100)
        self.savebtn.setText("Save")

        self.lay7.addWidget(self.savebtn)
        self.lay7.addWidget(self.leavebtn)

        QtCore.QMetaObject.connectSlotsByName(Window)

        self.connbtns()

    def connbtns(self):
        self.delbtn.clicked.connect(self.dellst)
        self.radiobtn.clicked.connect(self.allowslider)
        self.regslider.valueChanged.connect(self.sliderinfo)
        self.delpicsbtn.clicked.connect(self.delpics)
        self.leavebtn.clicked.connect(self.hide)
        self.savebtn.clicked.connect(self.save)

    def startupset(self):
        if self.checkbox0.isChecked():
            add_to_startup()

        else:
            remove_startup()

    def dellst(self):
        if os.path.isfile(project_path + '\\deleted.txt'):
            try:
                os.remove(project_path + '\\deleted.txt')
            except OSError:
                pass

    def delpics(self):
        if os.path.isdir(project_path):
            for item in os.listdir(project_path):
                path = project_path + '\\' + item
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

            if os.path.isfile(project_path+"\\"+"date.txt"):
                os.remove(project_path+"\\"+"date.txt")

            if os.path.isfile(project_path+"\\"+"cfg.txt"):
                os.remove(project_path+"\\"+"cfg.txt")

            if os.path.isfile(project_path+"\\"+"deleted.txt"):
                os.remove(project_path+"\\"+"deleted.txt")

    def allowslider(self):
        if self.radiobtn.isChecked():
            self.regslider.setEnabled(True)

        else:
            self.regslider.setSliderPosition(6)
            self.regslider.setEnabled(False)

    def sliderinfo(self):
        sliderpos = self.regslider.sliderPosition()
        self.parent.timer = self.switcher.get(sliderpos)

    def save(self):
        with open(project_path + '\\' + "cfg.txt", "w+") as file:
            file.write(
                "Changing regulary: " + str(self.regslider.isEnabled()) + "\n" + "Interval: " + str(self.parent.timer))
            file.close()

        self.startupset()

    def closeEvent(self, event: QtGui.QCloseEvent):
        event.ignore()
        self.hide()


def tray(path):
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon("nasa.png"), path, w)
    while not tray_icon.isSystemTrayAvailable():
        time.sleep(5)
    tray_icon.setVisible(True)
    tray_icon.show()
    tray_icon.showMessage('Nasa wallpaper changer v1.3', 'It works I guess... yay', QtGui.QIcon("nasa.png"))
    app.exec_()


if __name__ == '__main__':
    user = os.getlogin()
    project_path = r"C:\Users\{}\Nasa Wallpaper".format(user)
    try:
        os.mkdir(project_path)
    except:
        pass

    tray(project_path)
