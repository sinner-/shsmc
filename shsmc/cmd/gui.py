import click
import sys
from os import listdir
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QListWidget, QTextEdit, QPushButton
from shsmc.common.config import Configuration
from shsmc.client.user import User
from shsmc.client.device import Device
from shsmc.client.key import Key
from shsmc.client.message import Message

class Gui(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self._title = 'shsmc'
        self._width = 640
        self._height = 480
        self._config = config
        self._initUI()

    def _initUI(self):
        self.setWindowTitle(self._title)
        self.resize(self._width, self._height)

        self._contacts = QListWidget(self)
        self._contacts.resize(self._width/4, self._height)
        for username in listdir("%s/contacts/" % self._config.key_dir):
            self._contacts.addItem(username)

        self._message_textbox = QTextEdit(self)
        self._message_textbox.setReadOnly(True)
        self._message_textbox.move(self._width/4, 0)
        self._message_textbox.resize((self._width/4)*3, (self._height/4)*3)

        self._input_textbox = QTextEdit(self)
        self._input_textbox.move(self._width/4, (self._height/4)*3)
        self._input_textbox.resize((self._width/4)*2, self._height/4)

        self._sendmsg_button = QPushButton('Send Message', self)
        self._sendmsg_button.move((self._width/4)*3, (self._height/4)*3)

        self.show()

@click.command()
@click.option('--configdir', required=True)
def main(configdir):
    ''' SHSM GUI Client.
    '''
    config = Configuration("%s/config.ini" % configdir)
    try:
        user = User(config)
    except TypeError:
        print("bad master_verify_key, exiting")
        exit()

    try:
        device = Device(config, user.master_signing_key)
    except TypeError:
        print("bad device_verify_key, exiting")
        exit()

    try:
        key = Key(config, device.device_signing_key)
    except TypeError:
        print("bad device_private_key, exiting")
        exit()

    message = Message(key)

    app = QApplication(sys.argv)
    gui = Gui(config)
    sys.exit(app.exec_())
