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

def no_internet(icon):
    infobox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Nasa wallpaper changer",
                                    "Not able to download older pictures due to no connection.",
                                    QtWidgets.QMessageBox.Ok)

    infobox.setWindowIcon(icon)
    infobox.exec_()

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
                    if value == 57600000:
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

    if os.path.isfile(path + '\\' + 'cfg.txt'):
        with open(path + '\\' + 'cfg.txt', 'r') as file:
            txt = file.readlines()
            if len(txt)==3:
                last_line = txt[2]
                value = int(last_line[last_line.index(':') + 2:])
    else:
        value = 50


    dirs = get_date_dir_list(path)
    imgs = get_date_img_list(path)
    i=0
    while len(dirs)>value:
        name = dirs[i].strftime("%d_%m_%Y")
        if os.path.exists(path + "\\" + name):

            try:
                shutil.rmtree(path + "\\" + name)
            except PermissionError:
                try:
                    os.remove(path + "\\" + name + "\\" + name + ".jpg")
                except FileNotFoundError:
                    pass
        i+=1

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
    vbs_path = os.path.join(start, vbs_name)

    if not os.path.isfile(bat_name):
        with open(bat_name, "w") as f:
            f.write("cd " + file_path + '\n' + 'start \"\" ' "\"Nasa Wallpaper.exe\"")
            f.close()

    if not os.path.isfile(vbs_path):
        with open(vbs_path, "w") as f:
            f.write(
                "Set WshShell = CreateObject(\"WScript.Shell\")" + '\n' + 'WshShell.Run chr(34) & "' + file_path + '\\' + bat_name + '" & Chr(34), 0' + "\n" + 'Set WshShell = Nothing')
            f.close()


def remove_startup(file_path=""):
    USER_NAME = os.getlogin()
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(__file__))
    vbs_name = 'Nasa Wallpaper.vbs'
    bat_name = 'Nasa Wallpaper.bat'
    start = r'C:\Users\{}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'.format(USER_NAME)
    vbs_path = os.path.join(start, vbs_name)

    if os.path.isfile(file_path + "\\" + bat_name):
        os.remove(file_path + "\\" + bat_name)

    if os.path.isfile(vbs_path):
        os.remove(vbs_path)


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, path, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'Nasa wallpaper changer v1.3')
        self.main_path = os.path.dirname(os.path.realpath(__file__))
        self.project_path = path
        picDelete(project_path)
        self.update()
        self.interval = 300000
        self.titleicon = icon
        self.startTimer(self.interval)
        self.timer = timer_set(project_path)  # 1 day interval of change
        self.timer_add = self.interval
        self.internet = internet_on()
        menu = QtWidgets.QMenu(parent)

        switch_back = menu.addAction("Change wallpaper one back")
        switch_back.triggered.connect(self.switch_back)
        switch_back.setIcon(QtGui.QIcon(self.main_path + "\\" + "Actions-go-previous-icon.png"))

        switch_next = menu.addAction("Change wallpaper one forward")
        switch_next.triggered.connect(self.switch_next)
        switch_next.setIcon(QtGui.QIcon(self.main_path + "\\""Actions-go-next-icon.png"))

        if len(get_date_img_list(project_path)) > 7:
            switch_slider = menu.addAction("Change wallpaper using slider")
            switch_slider.triggered.connect(self.switch_slider)
            switch_slider.setIcon(QtGui.QIcon(self.main_path + "\\""slider.png"))

        switch_current = menu.addAction("Change wallpaper to newest")
        switch_current.triggered.connect(self.switch_current)
        switch_current.setIcon(QtGui.QIcon(self.main_path + "\\""current-icon.png"))

        delete = menu.addAction("Delete picture")
        delete.triggered.connect(self.delete)
        delete.setIcon(QtGui.QIcon(self.main_path + "\\""delete.png"))

        info = menu.addAction("Picture info")
        info.triggered.connect(self.info)
        info.setIcon(QtGui.QIcon(self.main_path + "\\""Info-icon.png"))

        cfg = menu.addAction("Settings")
        cfg.triggered.connect(self.cfg)
        cfg.setIcon(QtGui.QIcon(self.main_path + "\\""setting.png"))

        exit_ = menu.addAction("Exit")
        exit_.triggered.connect(lambda: sys.exit())
        exit_.setIcon(QtGui.QIcon(self.main_path + "\\""Close-2-icon.png"))

        menu.addSeparator()
        self.setContextMenu(menu)

    def switch_back(self):
        file_name = getWallpaper()
        setDate = file_name[-14:-4]
        if internet_on():
            try:
                newDate_obj = datetime.strptime(setDate, "%d_%m_%Y") - timedelta(days=1)

            except ValueError:
                newDate_obj = datetime.strptime(datetime.now(), "%d_%m_%Y") - timedelta(days=1)

            try:
                dir_dates = get_date_img_list(project_path)
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
                                    no_internet(self.titleicon)
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
                                        no_internet(self.titleicon)
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
                            if newDate_obj in get_date_img_list(project_path):
                                pic_path = project_path + "\\" + name + "\\" + name + ".jpg"
                                if os.path.isfile(pic_path):
                                    setWallpaper(pic_path)
                                    return None
                            if name not in deleted:
                                newDate = datetime.strftime(newDate_obj, "%d_%m_%Y")
                                fail = get_pic(project_path, newDate)
                                if fail:
                                    if fail == 1:
                                        newDate_obj = newDate_obj - timedelta(days=1)
                                        name = datetime.strftime(newDate_obj, "%d_%m_%Y")
                                        if name in deleted:
                                            continue
                                    elif fail != 1:
                                        pic_path = project_path + "\\" + name + "\\" + name + ".jpg"
                                        if os.path.isfile(pic_path):
                                            setWallpaper(pic_path)
                                            return None
                                else:
                                    no_internet(self.titleicon)
                                    return 0
                    if dir_dates.index(datetime.strptime(setDate, "%d_%m_%Y")) == 0:
                        newDate = datetime.strftime(newDate_obj, "%d_%m_%Y")
                        fail = get_pic(project_path, newDate)
                        if fail:
                            if fail == 1:
                                while fail == 1:
                                    newDate_obj = newDate_obj - timedelta(days=1)
                                    newDate = datetime.strftime(newDate_obj, "%d_%m_%Y")
                                    try:
                                        if newDate in deleted:
                                            continue
                                    except UnboundLocalError:
                                        pass
                                    fail = get_pic(project_path, newDate)
                                setWallpaper(project_path + "\\" + newDate + "\\" + newDate + ".jpg")
                            else:
                                setWallpaper(project_path + "\\" + newDate + "\\" + newDate + ".jpg")
                        else:
                            no_internet(self.titleicon)
                            return 0
                    else:
                        newDate_object = dir_dates[dir_dates.index(datetime.strptime(setDate, "%d_%m_%Y")) - 1]
                        name = datetime.strftime(newDate_object, "%d_%m_%Y")
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
        else:
            date_obj = datetime.strptime(setDate,'%d_%m_%Y')
            imgs = get_date_img_list(project_path)
            if date_obj in imgs:
                index = imgs.index(date_obj)
                if index !=0:
                    newpic = imgs[index-1]
                    name = newpic.strftime('%d_%m_%Y')
                    path = project_path +'\\' + name + '\\' + name + '.jpg'
                    setWallpaper(path)

    def switch_next(self):
        file_name = getWallpaper()
        setDate = file_name[-14:-4]

        if internet_on():
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
                                        no_internet(self.titleicon)
                                        setWallpaper(project_path + "\\" + newDate + "\\" + newDate + ".jpg")

                            # wants pic from tmrw ffs
                            try:
                                newDate = datetime.strftime(newDate_object, "%d_%m_%Y")
                                fail = get_pic(project_path, newDate)
                                if fail and fail!=1:
                                    setWallpaper(project_path + "\\" + newDate + "\\" + newDate + ".jpg")
                                else:
                                    no_internet(self.titleicon)
                            except HTTPError:
                                infobx = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                                               "Newest picuture",
                                                               "Sorry new picture wasn't uploaded yet... can't look into future",
                                                               QtWidgets.QMessageBox.Ok)
                                infobx.setWindowIcon(self.titleicon)
                                infobx.show()
                                infobx.exec_()



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
        else:
            date_obj = datetime.strptime(setDate, '%d_%m_%Y')
            imgs = get_date_img_list(project_path)
            if date_obj in imgs:
                index = imgs.index(date_obj)
                if index != len(imgs)-1:
                    newpic = imgs[index + 1]
                    name = newpic.strftime('%d_%m_%Y')
                    path = project_path + '\\' + name + '\\' + name + '.jpg'
                    setWallpaper(path)

    def switch_slider(self):
        self.slider = Scaler()
        self.slider.setupui(self.slider, self)
        self.slider.show()

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

                        if not pic_path:
                            no_internet(self.titleicon)
                            break

                        if pic_path:
                            httpfail = False

                    else:
                        name = date.strftime("%d_%m_%Y")
                        pic_path = project_path + "\\" + name + "\\" + name + ".jpg"
                        if pic_path == getWallpaper():
                            break
                        else:
                            if not self.timer:
                                setWallpaper(pic_path)
                                break
                            else:
                                break

                if not httpfail:
                    modifyDate(project_path)

                if pic_path != 0 and not self.timer:
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
        Window.setWindowFlags( QtCore.Qt.Widget | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.parent.main_path + "\\""nasa.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Window.setWindowIcon(icon)

        self.mainwin = QtWidgets.QWidget(Window)
        self.mainlayout = QtWidgets.QVBoxLayout()
        self.mainlayout.setContentsMargins(20, 20, 20, 20)
        self.mainlayout.setAlignment(QtCore.Qt.AlignHCenter)
        self.mainlayout.setSpacing(8)
        self.mainwin.setLayout(self.mainlayout)

        self.lay1 = QtWidgets.QHBoxLayout(self.mainwin)
        self.lay1.setSpacing(30)
        self.lay1.setContentsMargins(10, 0, 0, 0)

        self.lay8 = QtWidgets.QHBoxLayout(self.mainwin)
        self.lay8.setContentsMargins(10, 0, 0, 0)
        self.lay8.setSpacing(164)

        self.lay2 = QtWidgets.QHBoxLayout(self.mainwin)
        self.lay2.setContentsMargins(10, 0, 0, 0)
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
        if int(self.parent.timer) in list(self.switcher.values()):
            position = list(self.switcher.values()).index(int(self.parent.timer)) + 1
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

        if timer_set(project_path):
            self.radiobtn.setChecked(True)
            self.regslider.setEnabled(True)

        USER_NAME = os.getlogin()
        file_path = os.path.dirname(os.path.realpath(__file__))
        vbs_name = 'Nasa Wallpaper.vbs'
        bat_name = 'Nasa Wallpaper.bat'
        start = r'C:\Users\{}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'.format(USER_NAME)
        vbs_path = os.path.join(start, vbs_name)
        bat_path = os.path.join(file_path, bat_name)
        if os.path.isfile(vbs_path):
            if os.path.isfile(bat_path):
                self.checkbox0.setChecked(True)


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

        infobox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Nasa wallpaper changer",
                                        "You are about to delete all pictures and start from scratch.",
                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Abort)
        infobox.setInformativeText("Are you sure ?")
        infobox.setWindowIcon(self.parent.titleicon)
        out = infobox.exec_()

        if out == 16384:  #out == yes
            if os.path.isdir(project_path):
                for item in os.listdir(project_path):
                    path = project_path + '\\' + item
                    try:
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                    except PermissionError:
                        pass

                if os.path.isfile(project_path + "\\" + "date.txt"):
                    os.remove(project_path + "\\" + "date.txt")

                if os.path.isfile(project_path + "\\" + "cfg.txt"):
                    os.remove(project_path + "\\" + "cfg.txt")

                if os.path.isfile(project_path + "\\" + "deleted.txt"):
                    os.remove(project_path + "\\" + "deleted.txt")

                setWallpaper("")
                self.parent.update()

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
        self.savebtn.setDown(True)

        with open(project_path + '\\' + "cfg.txt", "w+") as file:
            file.write(
                "Changing regulary: " + str(self.regslider.isEnabled()) + "\n" + "Interval: " + str(self.parent.timer)+ "\n" +
                "Max count of pictures: " + str(50))
            file.close()

        self.startupset()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.start(500)

        infobox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Nasa wallpaper changer",
                                        "Settings were successfully saved.",
                                        QtWidgets.QMessageBox.Ok)
        infobox.setWindowIcon(self.parent.titleicon)
        infobox.exec_()

        self.timer.timeout.connect(self.btnchange)

    def btnchange(self):
        self.savebtn.setDown(False)


class Scaler(QtWidgets.QWidget):
    def setupui(self, Window, main):
        self.parent = main
        Window.setObjectName("Picture slider")
        Window.setWindowTitle("Picture slider")
        Window.resize(500, 120)
        Window.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint| QtCore.Qt.WindowTitleHint| QtCore.Qt.WindowCloseButtonHint)
        Window.setWindowIcon(self.parent.titleicon)
        self.slider = QtWidgets.QSlider(Window)
        self.slider.setGeometry(QtCore.QRect(60, 30, 350, 25))
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setObjectName("Slider")
        self.srange = 11
        self.slider.setRange(1, self.srange)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setSingleStep(1)

        self.usebtn = QtWidgets.QPushButton(Window)
        self.usebtn.setGeometry(QtCore.QRect(125, 80, 100, 30))
        self.usebtn.setText("Use current")

        self.cancelbtn = QtWidgets.QPushButton(Window)
        self.cancelbtn.setGeometry(QtCore.QRect(245, 80, 100, 30))
        self.cancelbtn.setText("Quit")

        self.setupLabels(Window)

        self.btnset()

    def btnset(self):
        self.usebtn.clicked.connect(self.usepic)
        self.cancelbtn.clicked.connect(self.cancel)
        self.slider.sliderReleased.connect(self.moveslider)

    def setupLabels(self, Window):
        self.original = getWallpaper()
        self.saved = False
        self.old_txt = getWallpaper()[-14:-4]
        try:
            current_date = datetime.strptime(self.old_txt,'%d_%m_%Y')
        except:
            self.parent.update()
            current_date = datetime.strptime(self.old_txt, '%d_%m_%Y')

        self.imgs_lst = get_date_img_list(project_path)
        self.index = self.imgs_lst.index(current_date)
        to_end = len(self.imgs_lst)-self.index-1

        self.datelabelold = QtWidgets.QLabel(Window)
        self.datelabelold.setGeometry(QtCore.QRect(30, 60, 150, 16))
        self.datelabelold.setObjectName("label")

        self.current = QtWidgets.QLabel(Window)
        self.current.setGeometry(QtCore.QRect(125, 10, 150, 16))
        self.current.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.current.setObjectName("label_2")
        self.current.setText("Current Picture")

        self.datelabelnext = QtWidgets.QLabel(Window)
        self.datelabelnext.setGeometry(QtCore.QRect(330, 60, 155, 16))
        self.datelabelnext.setAlignment(QtCore.Qt.AlignCenter)
        self.datelabelnext.setObjectName("label_3")

        to_back = 10-to_end
        if to_back < 5:
            to_back=5

        self.datelabelold.setText(str(to_back) + " pictures back")

        if to_end ==0:
            self.datelabelnext.hide()
            self.current.setGeometry(QtCore.QRect(300, 60, 155, 16))
            self.slider.setSliderPosition(self.srange-to_end)
        elif to_end == 1:
            self.current.setGeometry(QtCore.QRect(255, 10, 155, 16))
            self.datelabelnext.setText(str(to_end) + " picture ahead")
            self.slider.setSliderPosition(self.srange - to_end)
        elif to_end<5:
            if to_end==2:
                x_cor = 220
            elif to_end==3:
                x_cor = 190
            else:
                x_cor = 155
            self.current.setGeometry(QtCore.QRect(x_cor, 10, 155, 16))
            self.datelabelnext.setText(str(to_end) + " pictures ahead")
            self.slider.setSliderPosition(self.srange - to_end)
        else:
            if to_end>5:
                to_end=5
            self.datelabelnext.setText(str(to_end) + " pictures ahead")
            self.slider.setSliderPosition(6)

        self.oldpos = self.slider.sliderPosition()

        QtCore.QMetaObject.connectSlotsByName(Window)

    def moveslider(self):
        self.newpos = self.slider.sliderPosition()

        move = -self.oldpos+self.newpos

        self.index = self.index + move

        self.previewPic()

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.start(300)

        self.timer.timeout.connect(self.resetslider)

    def previewPic(self):
        if self.index >= 0:
            preview_pic = self.imgs_lst[self.index]
            name = preview_pic.strftime('%d_%m_%Y')
            path = project_path + "\\" + name + "\\" + name + ".jpg"
            if os.path.isfile(path):
                setWallpaper(path)

        if self.index < 0:
            date = self.imgs_lst[0]
            days = abs(self.index)+1
            skip = False
            if os.path.exists(project_path + '\\' + 'deleted.txt'):
                with open(project_path + '\\' + 'deleted.txt', "r") as file:
                    string_del = file.read()
                    deleted = string_del.split(";")
                    file.close()

            for i in range(1,days):
                new = date - timedelta(days = i)
                new_txt = new.strftime("%d_%m_%Y")

                if new_txt not in deleted:
                    fail = get_pic(project_path,new_txt)
                else:
                    fail = 1

                if fail == 1:
                    while fail==1:
                        new = new - timedelta(days=1)
                        new_txt = new.strftime("%d_%m_%Y")

                        if new_txt not in deleted:
                            fail = get_pic(project_path, new_txt)

                elif not fail:
                    no_internet(self.parent.titleicon)

            self.index = 0
            self.imgs_lst = get_date_img_list(project_path)
            oldest = self.imgs_lst[0]
            name_oldest = oldest.strftime("%d_%m_%Y")
            path = project_path + "\\" + name_oldest + "\\" + name_oldest + ".jpg"
            setWallpaper(path)

    def updatelabels(self):
        pos = self.slider.sliderPosition()
        to_back = pos-1
        to_end = 11-pos

        self.datelabelold.setText(str(to_back) + " pictures back")

        if to_end == 0:
            self.datelabelnext.hide()
            self.current.setGeometry(QtCore.QRect(300, 60, 155, 16))
        elif to_end == 1:
            self.datelabelnext.show()
            self.current.setGeometry(QtCore.QRect(255, 10, 155, 16))
            self.datelabelnext.setText(str(to_end) + " picture ahead")
        elif to_end < 5:
            if to_end == 2:
                x_cor = 220
            elif to_end == 3:
                x_cor = 190
            else:
                x_cor = 155
            self.datelabelnext.show()
            self.current.setGeometry(QtCore.QRect(x_cor, 10, 155, 16))
            self.datelabelnext.setText(str(to_end) + " pictures ahead")
        else:
            if to_end > 5:
                to_end = 5
            self.datelabelnext.show()
            self.datelabelnext.setText(str(to_end) + " pictures ahead")
            self.current.setGeometry(QtCore.QRect(125, 10, 150, 16))

    def resetslider(self):

        if len(self.imgs_lst) - self.index >= 6:
            self.slider.setSliderPosition(6)

        else:
            self.slider.setSliderPosition(11-(len(self.imgs_lst) - self.index)+1)

        self.oldpos = self.slider.sliderPosition()

        self.updatelabels()

    def usepic(self):
        infobox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Nasa wallpaper changer",
                                        "Current picture has been set as your new wallpaper.",
                                        QtWidgets.QMessageBox.Ok)

        infobox.setWindowIcon(self.parent.titleicon)
        infobox.exec_()

        self.saved = True

    def cancel(self):
        if not self.saved:
            setWallpaper(self.original)
        self.close()

    def closeEvent(self, event:QtGui.QCloseEvent):
        self.cancel()

def tray(path):
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon(os.path.dirname(os.path.realpath(__file__)) + "\\" + "nasa.png"), path, w)
    while not tray_icon.isSystemTrayAvailable():
        time.sleep(5)
    tray_icon.setVisible(True)
    tray_icon.show()

    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(os.path.dirname(os.path.realpath(__file__)) + "\\" + "nasa.ico"), QtGui.QIcon.Normal,
                   QtGui.QIcon.Off)
    tray_icon.showMessage('Nasa wallpaper changer v1.3', 'It works I guess... yay', icon)
    app.setQuitOnLastWindowClosed(False)
    app.exec_()


if __name__ == '__main__':
    user = os.getlogin()
    project_path = r"C:\Users\{}\Nasa Wallpaper".format(user)
    try:
        os.mkdir(project_path)
    except:
        pass

    tray(project_path)
