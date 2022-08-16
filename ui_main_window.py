# -*- coding: utf-8 -*-

import datetime
from PyQt5 import QtCore,QtGui,QtWidgets
import requests
from urllib.parse import urlparse, parse_qs

ORGANIZATION_NAME = 'TexelSoft'
APPLICATION_NAME = 'Bitrix24 Tokens Generator'
PROGRAM_SETTINGS_INI_FILENAME = 'program.ini'

class UiMainWindow(QtWidgets.QMainWindow):

    ''' Класс UI - главное окно приложения '''

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        # Нужно для QSettings
        QtCore.QCoreApplication.setOrganizationName(ORGANIZATION_NAME)
        QtCore.QCoreApplication.setApplicationName(APPLICATION_NAME)

        ui_lb_internet_name = QtWidgets.QLabel('Internet Name')
        self.ui_le_internet_name = QtWidgets.QLineEdit()
        ui_lb_client_id = QtWidgets.QLabel('Client ID')
        self.ui_le_client_id = QtWidgets.QLineEdit()
        ui_lb_client_secret = QtWidgets.QLabel('Client Secret')
        self.ui_le_client_secret = QtWidgets.QLineEdit()
        ui_lb_client_login = QtWidgets.QLabel('Login')
        self.ui_le_client_login = QtWidgets.QLineEdit()
        ui_lb_client_pass = QtWidgets.QLabel('Password')
        self.ui_le_client_pass = QtWidgets.QLineEdit()
        self.ui_le_client_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui_pb_generate = QtWidgets.QPushButton('Generate')
        self.ui_pb_generate.setMinimumHeight(36)
        self.ui_pb_generate.clicked.connect(self.getAccessAndRefreshTokens)
        #ui_pb_generate.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        ui_lt_auth = QtWidgets.QGridLayout()
        ui_lt_auth.setVerticalSpacing(5)
        ui_lt_auth.addWidget(ui_lb_internet_name, 0, 0)
        ui_lt_auth.addWidget(self.ui_le_internet_name, 0, 1)
        ui_lt_auth.addWidget(ui_lb_client_id, 1, 0)
        ui_lt_auth.addWidget(self.ui_le_client_id, 1, 1)
        ui_lt_auth.addWidget(ui_lb_client_secret, 2, 0)
        ui_lt_auth.addWidget(self.ui_le_client_secret, 2, 1)
        ui_lt_auth.addWidget(ui_lb_client_login, 3, 0)
        ui_lt_auth.addWidget(self.ui_le_client_login, 3, 1)
        ui_lt_auth.addWidget(ui_lb_client_pass, 4, 0)
        ui_lt_auth.addWidget(self.ui_le_client_pass, 4, 1)
        ui_lt_auth.addWidget(self.ui_pb_generate, 5, 0, -1, -1)
        # Вывод
        self.ui_te_output = QtWidgets.QTextEdit()
        # Центральный слой
        ui_lt_central = QtWidgets.QVBoxLayout()
        ui_lt_central.addLayout(ui_lt_auth)
        ui_lt_central.addWidget(self.ui_te_output)
        # Центральый виджет
        ui_cw_central = QtWidgets.QWidget()
        ui_cw_central.setLayout(ui_lt_central)
        self.setCentralWidget(ui_cw_central)
        # Размер окна
        self.setMinimumWidth(640)

        # Настройки
        self.loadSettings()


    def saveSettings(self):
        ''' Сохранение настроек главного окна в ini-файл '''

        settings = QtCore.QSettings(PROGRAM_SETTINGS_INI_FILENAME, QtCore.QSettings.IniFormat)
        settings.setValue('InternetName', self.ui_le_internet_name.text())
        settings.setValue('ClientID',     self.ui_le_client_id.text())
        settings.setValue('ClientSecret', self.ui_le_client_secret.text())
        settings.setValue('Login',        self.ui_le_client_login.text())


    def loadSettings(self):
        ''' Загрузка настроек главного окна из ini-файла '''

        settings = QtCore.QSettings(PROGRAM_SETTINGS_INI_FILENAME, QtCore.QSettings.IniFormat)
        if 'InternetName' in settings.allKeys(): self.ui_le_internet_name.setText(settings.value('InternetName'))
        if 'ClientID'     in settings.allKeys(): self.ui_le_client_id.setText(settings.value('ClientID'))
        if 'ClientSecret' in settings.allKeys(): self.ui_le_client_secret.setText(settings.value('ClientSecret'))
        if 'Login'        in settings.allKeys(): self.ui_le_client_login.setText(settings.value('Login'))


    def closeEvent(self, event):
        ''' Закрытие приложения '''

        self.hide()
        self.saveSettings()

        event.accept()


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.getAccessAndRefreshTokens()


    def getAccessAndRefreshTokens(self):
        ''' Получение токенов через логин и пароль '''

        # Отключение кнопки (включается перед выходом из функции)
        self.ui_pb_generate.setEnabled(False)

        # Проверка заданности необходимых членов класса
        if not self.ui_le_internet_name.text() or\
                not self.ui_le_client_id.text() or\
                not self.ui_le_client_login.text() or\
                not self.ui_le_client_secret.text() or\
                not self.ui_le_client_pass.text():
            self.statusBar().showMessage('Ошибка. Не заполнено одно из полей')
            self.ui_pb_generate.setEnabled(True)
            return False

        # Получение кода авторизации (autorization code grant)
        # Проверка по status_code здесь не подходит, т.к даже
        # при успешном редиректе возвращается 404
        # scope (разрешения) выставляются в настройках приложения,
        # передача их через адресную строку почему-то не работает
        url = 'https://'+self.ui_le_internet_name.text()+'/oauth/authorize'
        params =\
            {
                'client_id':self.ui_le_client_id.text(),
                'response_type':'code',
                'redirect_uri':'app_URL'
            }
        auth = requests.auth.HTTPBasicAuth(self.ui_le_client_login.text(), self.ui_le_client_pass.text())
        try:
            r = requests.get(url=url, params=params, auth=auth, timeout=3)
        except (requests.ConnectionError, requests.Timeout):
            self.ui_te_output.append('Ошибка. Истекло ожидание сервера авторизации')
            self.ui_pb_generate.setEnabled(True)
            return False
        redirect_url_parsed = urlparse(r.url)
        redirect_query = parse_qs(redirect_url_parsed.query)
        if 'code' not in redirect_query:
            self.ui_te_output.append('Ошибка. Не найден CODE')
            self.ui_pb_generate.setEnabled(True)
            return False
        code = redirect_query['code'][0]

        # Получение пары токенов access_token и refresh_token
        url = 'https://oauth.bitrix.info/oauth/token'
        params =\
            {
                'grant_type':'authorization_code',
                'client_id':self.ui_le_client_id.text(),
                'client_secret':self.ui_le_client_secret.text(),
                'code':code
            }
        try:
            r = requests.get(url=url, params=params, timeout=3)
        except (requests.ConnectionError, requests.Timeout):
            self.ui_te_output.append('Ошибка. Истекло ожидание сервера обмена CODE на токены')
            self.ui_pb_generate.setEnabled(True)
            return False

        if r.status_code != 200:
            self.ui_te_output.append('Ошибка. Ответ сервера обмена CODE на токены != 200')
            self.ui_pb_generate.setEnabled(True)
            return False
        access_token, refresh_token = r.json()['access_token'], r.json()['refresh_token']
        self.ui_te_output.append(access_token)
        self.ui_te_output.append(refresh_token + '\n')
        self.ui_pb_generate.setEnabled(True)
        return True