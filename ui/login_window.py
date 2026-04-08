"""
登录注册窗口 - 使用背景图和图标
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os


class LoginWindow(QWidget):
    """登录窗口类"""

    login_success = pyqtSignal(dict)
    register_request = pyqtSignal()

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.bg_image_path = os.path.join('resources', 'background', 'bkg.jpg')
        self.icon_image_path = os.path.join('resources', 'icons', 'icon.png')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Pest Identification System - Login')
        self.setFixedSize(520, 680)
        
        # 设置窗口图标
        icon = QIcon(self.icon_image_path)
        self.setWindowIcon(icon)

        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
            QLineEdit {
                padding: 16px 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 25px;
                font-size: 16px;
                background-color: rgba(255, 255, 255, 0.9);
                color: #333333;
                selection-background-color: #4a7c4a;
            }
            QLineEdit:focus {
                border: 3px solid #7cb342;
                background-color: rgba(255, 255, 255, 0.95);
            }
            QLineEdit::placeholder {
                color: #999999;
            }
            QPushButton {
                padding: 16px;
                border: none;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
                min-height: 30px;
            }

        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        bg_label = QLabel()
        bg_label.setFixedSize(520, 680)
        bg_pixmap = QPixmap(self.bg_image_path)
        if not bg_pixmap.isNull():
            bg_label.setPixmap(bg_pixmap.scaled(520, 680, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            bg_label.setStyleSheet("background-color: #2d4a2d;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(0)

        top_spacer = QWidget()
        top_spacer.setFixedHeight(100)
        container_layout.addWidget(top_spacer)

        main_title = QLabel('PEST IDENTIFICATION')
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #ffffff;
            letter-spacing: 5px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            background-color: transparent;
        """)
        container_layout.addWidget(main_title)

        sub_title = QLabel('Agricultural and Forestry Insect Recognition')
        sub_title.setAlignment(Qt.AlignCenter)
        sub_title.setStyleSheet("""
            font-size: 13px;
            color: #e0e0e0;
            letter-spacing: 1px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
            background-color: transparent;
            margin-top: 5px;
        """)
        container_layout.addWidget(sub_title)

        spacer2 = QWidget()
        spacer2.setFixedHeight(50)
        container_layout.addWidget(spacer2)

        input_container = QWidget()
        input_container.setStyleSheet("background-color: transparent; border: none;")
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(20, 0, 20, 0)
        input_layout.setSpacing(20)

        self.username = QLineEdit()
        self.username.setPlaceholderText('Username')
        self.username.setMinimumHeight(55)
        self.username.setStyleSheet("""
            padding: 16px 24px;
            border: 2px solid rgba(255, 255, 255, 0.4);
            border-radius: 27px;
            font-size: 16px;
            background-color: rgba(255, 255, 255, 0.95);
            color: #333333;
        """)
        input_layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText('Password')
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumHeight(55)
        self.password.setStyleSheet("""
            padding: 16px 24px;
            border: 2px solid rgba(255, 255, 255, 0.4);
            border-radius: 27px;
            font-size: 16px;
            background-color: rgba(255, 255, 255, 0.95);
            color: #333333;
        """)
        input_layout.addWidget(self.password)

        container_layout.addWidget(input_container)

        spacer3 = QWidget()
        spacer3.setFixedHeight(35)
        container_layout.addWidget(spacer3)

        btn_container = QWidget()
        btn_container.setStyleSheet("background-color: transparent; border: none;")
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(20, 0, 20, 0)
        btn_layout.setSpacing(15)

        self.login_btn = QPushButton('LOGIN')
        self.login_btn.setMinimumHeight(55)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #7cb342;
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 2px;
                border-radius: 27px;
                border: none;
            }
            QPushButton:hover {
                background-color: #8bc34a;
            }
            QPushButton:pressed {
                background-color: #689f38;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        btn_layout.addWidget(self.login_btn)

        self.register_btn = QPushButton('CREATE ACCOUNT')
        self.register_btn.setMinimumHeight(50)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: #ffffff;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 1px;
                border-radius: 25px;
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.7);
            }
        """)
        self.register_btn.clicked.connect(self.register_request.emit)
        btn_layout.addWidget(self.register_btn)

        container_layout.addWidget(btn_container)

        spacer4 = QWidget()
        spacer4.setFixedHeight(25)
        container_layout.addWidget(spacer4)

        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #ff6b6b;
            font-size: 14px;
            font-weight: bold;
            background-color: transparent;
        """)
        container_layout.addWidget(self.status_label)

        container_layout.addStretch()

        footer = QLabel('Intelligent Science and Technology')
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            color: #cccccc;
            font-size: 11px;
            letter-spacing: 1px;
            background-color: transparent;
        """)
        container_layout.addWidget(footer)

        stacked_layout = QStackedLayout()
        stacked_layout.setStackingMode(QStackedLayout.StackAll)
        stacked_layout.addWidget(bg_label)
        stacked_layout.addWidget(container)

        main_layout.addLayout(stacked_layout)

        self.password.returnPressed.connect(self.handle_login)

    def handle_login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            self.status_label.setText('Please enter username and password')
            return

        success, result = self.db.login_user(username, password)

        if success:
            self.login_success.emit(result)
        else:
            self.status_label.setText(result)
            self.password.clear()


class RegisterWindow(QWidget):
    """注册窗口类"""

    register_success = pyqtSignal(str, str)
    back_to_login = pyqtSignal()

    def __init__(self, database):
        super().__init__()
        self.db = database
        self.bg_image_path = os.path.join('resources', 'background', 'bkg.jpg')
        self.icon_image_path = os.path.join('resources', 'icons', 'icon.png')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Pest Identification System - Register')
        self.setFixedSize(520, 750)
        
        # 设置窗口图标
        icon = QIcon(self.icon_image_path)
        self.setWindowIcon(icon)

        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        bg_label = QLabel()
        bg_label.setFixedSize(520, 750)
        bg_pixmap = QPixmap(self.bg_image_path)
        if not bg_pixmap.isNull():
            bg_label.setPixmap(bg_pixmap.scaled(520, 750, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            bg_label.setStyleSheet("background-color: #2d4a2d;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(0)

        top_spacer = QWidget()
        top_spacer.setFixedHeight(50)
        container_layout.addWidget(top_spacer)

        title_icon_label = QLabel()
        title_icon_label.setAlignment(Qt.AlignCenter)
        title_icon_label.setFixedSize(90, 90)
        title_icon_label.setStyleSheet("background-color: transparent; border: none;")
        icon_pixmap = QPixmap(self.icon_image_path)
        if not icon_pixmap.isNull():
            icon_scaled = icon_pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            title_icon_label.setPixmap(icon_scaled)
        else:
            title_icon_label.setText('ICON')
        container_layout.addWidget(title_icon_label)

        spacer1 = QWidget()
        spacer1.setFixedHeight(20)
        container_layout.addWidget(spacer1)

        main_title = QLabel('CREATE ACCOUNT')
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #ffffff;
            letter-spacing: 4px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            background-color: transparent;
        """)
        container_layout.addWidget(main_title)

        sub_title = QLabel('Join our pest identification platform')
        sub_title.setAlignment(Qt.AlignCenter)
        sub_title.setStyleSheet("""
            font-size: 12px;
            color: #e0e0e0;
            letter-spacing: 1px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
            background-color: transparent;
            margin-top: 5px;
        """)
        container_layout.addWidget(sub_title)

        spacer2 = QWidget()
        spacer2.setFixedHeight(35)
        container_layout.addWidget(spacer2)

        input_container = QWidget()
        input_container.setStyleSheet("background-color: transparent; border: none;")
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(20, 0, 20, 0)
        input_layout.setSpacing(18)

        self.username = QLineEdit()
        self.username.setPlaceholderText('Username (4-20 characters)')
        self.username.setMinimumHeight(52)
        self.username.setStyleSheet("""
            padding: 14px 24px;
            border: 2px solid rgba(255, 255, 255, 0.4);
            border-radius: 26px;
            font-size: 15px;
            background-color: rgba(255, 255, 255, 0.95);
            color: #333333;
        """)
        input_layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText('Password (6-20 characters)')
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumHeight(52)
        self.password.setStyleSheet("""
            padding: 14px 24px;
            border: 2px solid rgba(255, 255, 255, 0.4);
            border-radius: 26px;
            font-size: 15px;
            background-color: rgba(255, 255, 255, 0.95);
            color: #333333;
        """)
        input_layout.addWidget(self.password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText('Confirm Password')
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setMinimumHeight(52)
        self.confirm_password.setStyleSheet("""
            padding: 14px 24px;
            border: 2px solid rgba(255, 255, 255, 0.4);
            border-radius: 26px;
            font-size: 15px;
            background-color: rgba(255, 255, 255, 0.95);
            color: #333333;
        """)
        input_layout.addWidget(self.confirm_password)

        container_layout.addWidget(input_container)

        spacer3 = QWidget()
        spacer3.setFixedHeight(30)
        container_layout.addWidget(spacer3)

        btn_container = QWidget()
        btn_container.setStyleSheet("background-color: transparent; border: none;")
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(20, 0, 20, 0)
        btn_layout.setSpacing(12)

        self.register_btn = QPushButton('REGISTER')
        self.register_btn.setMinimumHeight(52)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #7cb342;
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 2px;
                border-radius: 26px;
                border: none;
            }
            QPushButton:hover {
                background-color: #8bc34a;
            }
            QPushButton:pressed {
                background-color: #689f38;
            }
        """)
        self.register_btn.clicked.connect(self.handle_register)
        btn_layout.addWidget(self.register_btn)

        self.back_btn = QPushButton('BACK TO LOGIN')
        self.back_btn.setMinimumHeight(48)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 1px;
                border-radius: 24px;
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.7);
            }
        """)
        self.back_btn.clicked.connect(self.back_to_login.emit)
        btn_layout.addWidget(self.back_btn)

        container_layout.addWidget(btn_container)

        spacer4 = QWidget()
        spacer4.setFixedHeight(20)
        container_layout.addWidget(spacer4)

        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #ff6b6b;
            font-size: 14px;
            font-weight: bold;
            background-color: transparent;
        """)
        container_layout.addWidget(self.status_label)

        container_layout.addStretch()

        footer = QLabel('Intelligent Science and Technology')
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            color: #cccccc;
            font-size: 11px;
            letter-spacing: 1px;
            background-color: transparent;
        """)
        container_layout.addWidget(footer)

        stacked_layout = QStackedLayout()
        stacked_layout.setStackingMode(QStackedLayout.StackAll)
        stacked_layout.addWidget(bg_label)
        stacked_layout.addWidget(container)

        main_layout.addLayout(stacked_layout)

    def handle_register(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        confirm = self.confirm_password.text().strip()

        if len(username) < 4:
            self.status_label.setText('Username must be at least 4 characters')
            return

        if len(password) < 6:
            self.status_label.setText('Password must be at least 6 characters')
            return

        if password != confirm:
            self.status_label.setText('Passwords do not match')
            return

        success, result = self.db.register_user(username, password)

        if success:
            QMessageBox.information(self, 'Success', 'Account created successfully! Please login.')
            self.register_success.emit(username, password)
            self.close()
        else:
            self.status_label.setText(result)