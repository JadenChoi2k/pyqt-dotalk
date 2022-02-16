import sys
from PyQt5.QtWidgets import QApplication, QWidget
import math
import preferences
from preferences import SCREEN_RATIO
from network.database.client.db_client import DbClient
from pages.login_page import LoginPage
from pages.home.home_page import HomePage
import meta

dbClient = DbClient()


def ratio_resize(self, x, y):
    self.resize(math.ceil(x * preferences.x_ratio()), math.ceil(y * preferences.y_ratio()))


def ratio_setFixedSize(self, x, y):
    self.setFixedSize(math.ceil(x * preferences.x_ratio()), math.ceil(y * preferences.y_ratio()))


def ratio_setFixedHeight(self, h):
    self.setFixedHeight(math.ceil(h * preferences.y_ratio()))


def ratio_setFixedWidth(self, w):
    self.setFixedWidth(math.ceil(w * preferences.x_ratio()))


QWidget.ratio_resize = ratio_resize
QWidget.ratio_setFixedSize = ratio_setFixedSize
QWidget.ratio_setFixedHeight = ratio_setFixedHeight
QWidget.ratio_setFixedWidth = ratio_setFixedWidth


if __name__ == '__main__':
    meta.project_info()
    app = QApplication(sys.argv)
    # set screen ratio
    size = app.primaryScreen().size()
    preferences.SCREEN_RATIO = (size.width() / 1920, size.height() / 1080)
    #
    login = LoginPage()
    login.show()
    app.exec_()

    if dbClient.isLogin():
        home = HomePage()
        try:
            home.show()
        except AttributeError as e:
            home.hide()
            print(e)
            login.show()
            app.exec_()
            home.show()
        sys.exit(app.exec_())
