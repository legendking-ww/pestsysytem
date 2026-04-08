

import sys
import os
from PyQt5.QtWidgets import QApplication

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import Database
from ui.login_window import LoginWindow, RegisterWindow
from ui.main_window import MainWindow

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.db = Database()
        self.show_login()
    
    def show_login(self):
        self.login = LoginWindow(self.db)
        self.login.login_success.connect(self.on_login)
        self.login.register_request.connect(self.show_register)
        self.login.show()
    
    def show_register(self):
        self.login.hide()
        self.register = RegisterWindow(self.db)
        self.register.register_success.connect(self.on_register)
        self.register.show()
    
    def on_login(self, user_info):
        self.login.close()
        self.main = MainWindow(user_info)
        self.main.show()
    
    def on_register(self, username, password):
        self.register.close()
        self.show_login()
    
    def run(self):
        return self.app.exec_()

if __name__ == '__main__':
    # 确保目录存在
    os.makedirs('models', exist_ok=True)
    os.makedirs('images', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    
    app = App()
    sys.exit(app.run())
