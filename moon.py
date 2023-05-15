### imports ###
import os
import re
import sys
import urllib.request

import PySide6
import requests
import stem.process
from adblockparser import AdblockRules
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import QCoreApplication, QSize, Qt, QUrl, Slot
from PySide6.QtGui import QAction, QColor, QIcon, QPixmap
from PySide6.QtNetwork import QNetworkProxy
from PySide6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineUrlRequestInterceptor,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPushButton,
    QTabWidget,
    QToolBar,
)

### imports end ###
# ---------------------------------------------------------------------------------------------------#
### shows whats happening in terminal ###
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--force-dark-mode"
url = "https://filters.adtidy.org/extension/ublock/filters/101_optimized.txt"
raw_rules = requests.get(url).text.splitlines()

# Create AdblockRules object
rules = AdblockRules(raw_rules)


class RequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if rules.should_block(url):
            print(f"Blocked {url}")
            info.block(True)
        print("####### INTERCEPTING REQUEST #######")
        print(info.requestUrl())


### end of terminal part ###

# ---------------------------------------------------------------------------------------------------#


### Main Browser Window ###
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SKYNET")  # sets windows title
        background_color = QColor(33, 33, 33)  # dark gray color
        text_color = QColor(255, 255, 255)
        self.setWindowIcon(QtGui.QIcon("sky.png"))  # sets logo
        self.setStyleSheet("background-color: #000000")  # dark theme
        # Create a new BrowserTab instance and set it as the central widget

        self.toolBar = QToolBar()  # toolbar where the search input and back buttons are
        self.toolBar.setMinimumHeight(50)
        self.addToolBar(self.toolBar)

        # Add a "New Tab" button to the toolbar

        # Create a "New Tab" button in the toolbar and connect it to the newTab method
        self.backButton = QPushButton()
        self.backButton.setIcon(QIcon("outline_arrow_back_ios_new_white_24dp.png"))
        self.backButton.clicked.connect(self.back)
        self.toolBar.addWidget(self.backButton)
        self.forwardButton = QPushButton()
        self.forwardButton.setIcon(QIcon("outline_arrow_forward_ios_white_24dp.png"))
        self.forwardButton.clicked.connect(self.forward)
        self.toolBar.addWidget(self.forwardButton)
        self.addToolBar(self.toolBar)
        self.refreshButton = QPushButton()
        self.refreshButton.setIcon(QIcon("outline_refresh_white_24dp.png"))
        self.refreshButton.clicked.connect(self.load)
        self.toolBar.addWidget(self.refreshButton)

        self.homeButton = QPushButton()
        self.homeButton.setIcon(QIcon("outline_home_white_24dp.png"))
        self.homeButton.clicked.connect(self.home)
        self.toolBar.addWidget(self.homeButton)

        self.addressLineEdit = QLineEdit()
        self.addressLineEdit.setMinimumSize(QSize(200, 30))
        self.addressLineEdit.returnPressed.connect(self.load)
        self.addressLineEdit.setStyleSheet("color: white;")
        self.toolBar.addWidget(self.addressLineEdit)

        self.button = QPushButton()
        self.button.setIcon(QIcon("outline_menu_white_24dp.png"))
        self.button.setStyleSheet("color:white;")
        self.menu = QMenu(self.button)
        self.menu.setStyleSheet("color:white;")

        action1 = QAction("Settings", self)
        action1.setIcon(QIcon("outline_settings_white_24dp.png"))
        action1.triggered.connect(self.settings)
        action2 = QAction("New Tor Window", self)
        action2.setIcon(QIcon("outline_preview_white_24dp.png"))
        action3 = QAction("About", self)
        action3.triggered.connect(self.about)
        action4 = QAction("Exit", self)
        action4.setIcon(QIcon("outline_power_settings_new_white_24dp.png"))
        action4.triggered.connect(self.exit)

        self.label = QLabel(self)
        self.label.setStyleSheet("color: #ffffff")
        self.toolBar.addWidget(self.label)

        # Set the text of the label to the text obtained from the API

        self.menu.addAction(action1)
        self.menu.addAction(action2)
        self.menu.addAction(action3)
        self.menu.addAction(action4)

        self.button.setMenu(self.menu)
        self.toolBar.addWidget(self.button)

        self.webEngineView = QWebEngineView()
        self.webEngineView.setStyleSheet(
            f"background-color: {background_color.name()}; color: {text_color.name()};"
        )

        self.setCentralWidget(self.webEngineView)
        initialUrl = "http://ip-api.com/json"
        self.addressLineEdit.setText(initialUrl)
        self.webEngineView.load(QUrl(initialUrl))
        self.webEngineView.page().titleChanged.connect(self.setWindowTitle)
        self.webEngineView.page().urlChanged.connect(self.urlChanged)

    def home(self):
        url = "https://duckduckgo.com"
        self.webEngineView.load(url)

    def exit(self):
        self.close

    def about(self):
        url = "simplystudios.github.io/anshwadhwa"
        self.webEngineView.load(url)

    def settings(self):
        url = "https://hinduwiki.ml"
        self.webEngineView.load(url)

    def load(self):
        url = QUrl.fromUserInput(self.addressLineEdit.text())
        if url.isValid():
            self.webEngineView.load(url)

        # Check if a QApplication instance already exists

    @Slot()
    def back(self):
        self.webEngineView.page().triggerAction(QWebEnginePage.Back)

    @Slot()
    def forward(self):
        self.webEngineView.page().triggerAction(QWebEnginePage.Forward)

    @Slot(QUrl)
    def urlChanged(self, url):
        self.addressLineEdit.setText(url.toString())


def launch_tor_process():
    SOCKS_PORT = 9050
    CONTROL_PORT = 9051
    TOR_PATH = "/usr/bin/tor"
    GEOIPFILE_PATH = os.path.normpath(os.getcwd() + "/geoip")
    try:
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/torproject/tor/main/src/config/geoip",
            GEOIPFILE_PATH,
        )
    except:
        print("[INFO] Unable to update geoip file. Using local copy.")

    tor_process = stem.process.launch_tor_with_config(
        config={
            "SocksPort": str(SOCKS_PORT),
            "ControlPort": str(CONTROL_PORT),
            "ExitNodes": "",
            "StrictNodes": "1",
            "CookieAuthentication": "1",
            "MaxCircuitDirtiness": "60",
            "GeoIPFile": GEOIPFILE_PATH,
        },
        take_ownership=True,
        init_msg_handler=lambda line: (
            print(line) if re.search("Bootstrapped", line) else False
        ),
        tor_cmd=TOR_PATH,
        timeout=300,
    )


if __name__ == "__main__":
    # Launch a Tor process
    launch_tor_process()
    app = QApplication(sys.argv)

    # Proxy all browser requests through the Tor process
    PROXY_PORT = 9050
    PROXY_HOST = "127.0.0.1"
    proxy = QNetworkProxy()
    proxy.setType(QNetworkProxy.Socks5Proxy)
    proxy.setHostName(PROXY_HOST)
    proxy.setPort(PROXY_PORT)
    QNetworkProxy.setApplicationProxy(proxy)
    TOR_CHECK_URL = "https://check.torproject.org/cgi-bin/TorBulkExitList.py?ip=1.1.1.1"
    IPIFY_API_URL = "https://api.ipify.org"

    def check_tor():
        ip = requests.get(IPIFY_API_URL).text
        tor_exit_node_list = requests.get(TOR_CHECK_URL).text
        print(ip in tor_exit_node_list)

    check_tor()

    # Add a request interceptor so we can read all the requests from the browser
    interceptor = RequestInterceptor()

    mainWin = MainWindow()
    mainWin.webEngineView.page().profile().setUrlRequestInterceptor(interceptor)
    availableGeometry = mainWin.screen().availableGeometry()
    mainWin.resize(
        availableGeometry.width() * 2 / 3, availableGeometry.height() * 2 / 3
    )

    # Launch the web browser
    mainWin.show()
    sys.exit(app.exec())
