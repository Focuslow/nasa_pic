from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve, URLError
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
    page = urlopen(url)
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
        url_path = getUrl(date)
        if url_path == 0:
            return 0
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


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    """
    CREATE A SYSTEM TRAY ICON CLASS AND ADD MENU
    """

    def __init__(self, icon, path, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'Nasa wallpaper changer v1.2')
        self.project_path = path
        self.internetTimer = QtCore.QTimer()
        self.startTimer(5000)
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

        exit_ = menu.addAction("Exit")
        exit_.triggered.connect(lambda: sys.exit())
        exit_.setIcon(QtGui.QIcon("Close-2-icon.png"))

        menu.addSeparator()
        self.setContextMenu(menu)
        self.activated.connect(self.onTrayIconActivated)

    def onTrayIconActivated(self, reason):
        """
        This function will trigger function on click or double click
        :param reason:
        :return:
        """
        # if reason == self.DoubleClick:
        #     self.open_notepad()
        # # if reason == self.Trigger:
        # #     self.open_notepad()

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
                                if fail == 0:
                                    while fail == 0:
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
                                    if fail == 0:
                                        while fail == 0:
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
                                if fail == 0:
                                    newDate_obj = newDate_obj - timedelta(days=1)
                                    name = datetime.strftime(newDate_obj, "%d_%m_%Y")
                                elif fail != 0:
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
                        if fail == 0:
                            while fail == 0:
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
                        if get_pic(project_path,name):
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

    def timerEvent(self, event:QtCore.QTimerEvent):
        if internet_on():
            same = sameDate(project_path)
            # print(same)
            if not same:
                modifyDate(project_path)
                date = datetime.now()
                name = date.strftime("%d_%m_%Y")
                pic_path = get_pic(project_path, name)
                if pic_path == 0 or not pic_path:
                    pass
                else:
                    setWallpaper(pic_path)
                    picDelete(project_path)

def tray(path):
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon("nasa.png"), path, w)
    while not tray_icon.isSystemTrayAvailable():
        time.sleep(5)
    tray_icon.setVisible(True)
    tray_icon.show()
    tray_icon.showMessage('Nasa wallpaper changer v1.2', 'It works I guess... yay',QtGui.QIcon("nasa.png"))
    app.exec_()


if __name__ == '__main__':
    user = os.getlogin()
    project_path = r"C:\Users\{}\Nasa Wallpaper".format(user)
    try:
        os.mkdir(project_path)
    except:
        pass

    tray(project_path)





