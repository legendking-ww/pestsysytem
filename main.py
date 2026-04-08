

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

        self.app.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #333333;
            }
            QMessageBox QLabel {
                color: #333333;
                background-color: transparent;
                font-size: 14px;
                padding: 5px;
            }
            QMessageBox QPushButton {
                background-color: #7cb342;
                color: white;
                border: none;
                padding: 10px 25px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 90px;
                min-height: 36px;
            }
            QMessageBox QPushButton:hover {
                background-color: #8bc34a;
            }
        """)

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
        self.register.back_to_login.connect(self.on_back_to_login)
        self.register.show()
    
    def on_register(self, username, password):
        self.register.close()
        self.show_login()
    
    def on_back_to_login(self):
        self.register.close()
        self.login.show()
    
    def on_login(self, user_info):
        self.login.close()
        self.main = MainWindow(user_info)
        self.main.show()
    
    def run(self):
        return self.app.exec_()

if __name__ == '__main__':
    # 确保目录存在
    os.makedirs('models', exist_ok=True)
    os.makedirs('images', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    
    app = App()
    sys.exit(app.run())
