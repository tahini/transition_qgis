# MIT License

# Copyright (c) 2024 Polytechnique Montréal

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from qgis.PyQt import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt.QtWidgets import QDialog

import os
import requests
from pyTransition import Transition

class LoginDialog(QDialog):
    """
        A dialog to login to a Transition server.
    """
    closeWidget = pyqtSignal()
    transitionInstanceCreated = pyqtSignal(object)
    
    def __init__(self, iface, settings, parent = None) -> None:
        """
            Constructor.
            
            :param iface: The QGIS interface.
            :param settings: The QGIS settings.
            :param parent: The parent widget.
        """
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'login_dialog.ui'), self)
        self.settings = settings
        self.iface = iface
        self.show()

        self.urlEdit.setText("http://localhost:8080")

        self.buttonBox.accepted.connect(self.onConnectButtonClicked)
        self.buttonBox.rejected.connect(self.reject)


    def onConnectButtonClicked(self):
        """
            Connect to the Transition server.

            :return: None
        """
        try:
            if self.usernameEdit.text() == "" or self.passwordEdit.text() == "":
                QMessageBox.warning(self, self.tr("Invalid loggin credentials"), self.tr("Please enter your username and password."))
                return
            
            transition_instance = Transition(self.urlEdit.text(), self.usernameEdit.text(), self.passwordEdit.text())
            self.transitionInstanceCreated.emit(transition_instance)

            self.settings.setValue("username", self.usernameEdit.text())
            self.settings.setValue("url", self.urlEdit.text())
            self.settings.setValue("token", transition_instance.token)
            self.settings.setValue("keepConnection", self.loginCheckbox.isChecked())
            
            self.accept()
            
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, self.tr("Unable to connect to server"), self.tr("Unable to connect to your Transition server.\nMake sure you provided the right server URL and that the server is up."))
            self.close()
            self.closeWidget.emit()
        except requests.exceptions.HTTPError as error:
            self.iface.messageBar().pushCritical('Error', str(error.response.text))
        except Exception as error:
            self.iface.messageBar().pushCritical('Error', str(error))

