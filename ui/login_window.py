"""
登录注册窗口 - 简洁大气版
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class LoginWindow(QWidget):
    """登录窗口类"""
    
    # 定义信号
    login_success = pyqtSignal(dict)  # 登录成功信号，传递用户信息
    register_request = pyqtSignal()    # 注册请求信号
    
    def __init__(self, database):
        """初始化登录窗口
        
        Args:
            database: 数据库对象
        """
        super().__init__()
        self.db = database
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('农林昆虫识别系统 - 登录')
        self.setFixedSize(480, 620)  # 加大窗口（宽480，高620）
        
        # 设置全局样式表
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;  /* 浅灰色背景 */
                font-family: 'Microsoft YaHei', sans-serif;  /* 字体 */
            }
            QLineEdit {
                padding: 14px;  /* 加大内边距 */
                border: 2px solid #e0e0e0;  /* 边框 */
                border-radius: 10px;  /* 加大圆角 */
                font-size: 15px;  /* 加大字体 */
                background-color: white;  /* 白色背景 */
                min-height: 20px;  /* 最小高度 */
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;  /* 焦点时绿色边框 */
            }
            QPushButton {
                padding: 14px;  /* 加大内边距 */
                border: none;  /* 无边框 */
                border-radius: 10px;  /* 加大圆角 */
                font-size: 16px;  /* 加大字体 */
                font-weight: bold;  /* 粗体 */
                min-height: 30px;  /* 最小高度 */
            }
            QLabel {
                color: #2c3e50;  /* 深灰色文字 */
                font-size: 15px;  /* 加大字体 */
            }
        """)
        
        # 主布局（垂直布局）
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)  # 加大外边距
        layout.setSpacing(25)  # 加大控件间距
        
        # ========== Logo和标题区域 ==========
        title_layout = QVBoxLayout()
        title_layout.setSpacing(15)  # 加大内部控件间距
        
        # 图标（Emoji）
        icon_label = QLabel('🌾')
        icon_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        icon_label.setStyleSheet("font-size: 70px; color: #4CAF50;")  # 加大图标
        title_layout.addWidget(icon_label)
        
        # 主标题
        title = QLabel('农林昆虫识别系统')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e3c72;")  # 加大标题
        title_layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel('智慧农业 · 智能识别')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #7f8c8d;")  # 加大副标题
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addSpacing(30)  # 加大空白间距
        
        # ========== 输入区域 ==========
        input_layout = QVBoxLayout()
        input_layout.setSpacing(20)  # 加大内部控件间距
        
        # 用户名输入
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)  # 加大标签和输入框间距
        
        username_label = QLabel('用户名')
        username_label.setStyleSheet("font-size: 15px; font-weight: 500;")
        username_layout.addWidget(username_label)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText('请输入您的用户名')  # 占位文本
        self.username.setMinimumHeight(45)  # 设置最小高度
        self.username.setStyleSheet("""
            QLineEdit {
                padding: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 15px;
            }
        """)
        username_layout.addWidget(self.username)
        input_layout.addLayout(username_layout)
        
        # 密码输入
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)
        
        password_label = QLabel('密码')
        password_label.setStyleSheet("font-size: 15px; font-weight: 500;")
        password_layout.addWidget(password_label)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText('请输入您的密码')
        self.password.setEchoMode(QLineEdit.Password)  # 密码模式（显示圆点）
        self.password.setMinimumHeight(45)  # 设置最小高度
        self.password.setStyleSheet("""
            QLineEdit {
                padding: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 15px;
            }
        """)
        password_layout.addWidget(self.password)
        input_layout.addLayout(password_layout)
        
        layout.addLayout(input_layout)
        layout.addSpacing(20)  # 加大空白间距
        
        # ========== 按钮区域 ==========
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(15)  # 加大按钮间距
        
        # 登录按钮
        self.login_btn = QPushButton('登 录')
        self.login_btn.setMinimumHeight(50)  # 设置最小高度
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* 绿色背景 */
                color: white;
                font-size: 18px;  /* 加大字体 */
                padding: 14px;  /* 加大内边距 */
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;  /* 悬停深绿色 */
            }
            QPushButton:pressed {
                background-color: #3d8b40;  /* 按下更深的绿色 */
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        btn_layout.addWidget(self.login_btn)
        
        # 注册按钮
        self.register_btn = QPushButton('注册新账号')
        self.register_btn.setMinimumHeight(50)  # 设置最小高度
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: white;  /* 白色背景 */
                color: #4CAF50;  /* 绿色文字 */
                font-size: 16px;
                padding: 14px;
                border: 2px solid #4CAF50;  /* 绿色边框 */
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f9f0;  /* 悬停浅绿色背景 */
            }
        """)
        self.register_btn.clicked.connect(self.register_request.emit)  # 发射注册请求信号
        btn_layout.addWidget(self.register_btn)
        
        layout.addLayout(btn_layout)
        
        # 状态提示标签
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(40)  # 设置最小高度
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # 底部版权信息
        copyright_label = QLabel('© 2026 智能科学与技术专业 · 毕业设计')
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setMinimumHeight(30)  # 设置最小高度
        copyright_label.setStyleSheet("color: #95a5a6; font-size: 12px; margin-top: 20px;")
        layout.addWidget(copyright_label)
        
        # 回车键登录（密码框按回车触发登录）
        self.password.returnPressed.connect(self.handle_login)
        
        self.setLayout(layout)
    
    def handle_login(self):
        """处理登录逻辑"""
        username = self.username.text().strip()  # 获取用户名并去除空格
        password = self.password.text().strip()  # 获取密码并去除空格
        
        # 验证输入
        if not username or not password:
            self.status_label.setText('请输入用户名和密码')
            return
        
        # 调用数据库登录方法
        success, result = self.db.login_user(username, password)
        
        if success:
            self.login_success.emit(result)  # 登录成功，发射信号
        else:
            self.status_label.setText(result)  # 显示错误信息
            self.password.clear()  # 清空密码框


class RegisterWindow(QWidget):
    """注册窗口类"""
    
    register_success = pyqtSignal(str, str)  # 注册成功信号，传递用户名和密码
    
    def __init__(self, database):
        """初始化注册窗口
        
        Args:
            database: 数据库对象
        """
        super().__init__()
        self.db = database
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('农林昆虫识别系统 - 注册')
        self.setFixedSize(480, 680)  # 加大窗口（宽480，高680）
        
        # 设置全局样式表
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Microsoft YaHei', sans-serif;
            }
            QLineEdit {
                padding: 14px;  /* 加大内边距 */
                border: 2px solid #e0e0e0;
                border-radius: 10px;  /* 加大圆角 */
                font-size: 15px;  /* 加大字体 */
                background-color: white;
                min-height: 20px;  /* 最小高度 */
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QPushButton {
                padding: 14px;  /* 加大内边距 */
                border: none;
                border-radius: 10px;  /* 加大圆角 */
                font-size: 16px;  /* 加大字体 */
                font-weight: bold;
                min-height: 30px;  /* 最小高度 */
            }
            QLabel {
                font-size: 15px;  /* 加大字体 */
            }
        """)
        
        # 主布局（垂直布局）
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)  # 加大外边距
        layout.setSpacing(20)  # 加大控件间距
        
        # 标题
        title = QLabel('创建新账号')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #1e3c72; margin-bottom: 15px;")  # 加大标题
        layout.addWidget(title)
        
        # 用户名输入
        layout.addWidget(QLabel('用户名'))
        self.username = QLineEdit()
        self.username.setPlaceholderText('4-20位字符，字母或数字')
        self.username.setMinimumHeight(45)  # 设置最小高度
        layout.addWidget(self.username)
        
        # 密码输入
        layout.addWidget(QLabel('密码'))
        self.password = QLineEdit()
        self.password.setPlaceholderText('6-20位字符')
        self.password.setEchoMode(QLineEdit.Password)  # 密码模式
        self.password.setMinimumHeight(45)  # 设置最小高度
        layout.addWidget(self.password)
        
        # 确认密码输入
        layout.addWidget(QLabel('确认密码'))
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText('请再次输入密码')
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setMinimumHeight(45)  # 设置最小高度
        layout.addWidget(self.confirm_password)
        
        layout.addSpacing(20)  # 加大空白间距
        
        # 注册按钮
        self.register_btn = QPushButton('注 册')
        self.register_btn.setMinimumHeight(50)  # 设置最小高度
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;  /* 加大字体 */
                padding: 14px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)
        
        # 返回登录按钮
        self.back_btn = QPushButton('返回登录')
        self.back_btn.setMinimumHeight(40)  # 设置最小高度
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;  /* 透明背景 */
                color: #7f8c8d;  /* 灰色文字 */
                font-size: 15px;
                padding: 10px;  /* 加大内边距 */
                border: none;
            }
            QPushButton:hover {
                color: #4CAF50;  /* 悬停绿色文字 */
            }
        """)
        self.back_btn.clicked.connect(self.close)  # 点击关闭窗口
        layout.addWidget(self.back_btn)
        
        # 状态提示标签
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(40)  # 设置最小高度
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; padding: 5px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()  # 添加伸缩因子，将控件推向上方
        self.setLayout(layout)
    
    def handle_register(self):
        """处理注册逻辑"""
        username = self.username.text().strip()
        password = self.password.text().strip()
        confirm = self.confirm_password.text().strip()
        
        # 验证用户名长度
        if len(username) < 4:
            self.status_label.setText('用户名至少4位')
            return
        
        # 验证密码长度
        if len(password) < 6:
            self.status_label.setText('密码至少6位')
            return
        
        # 验证两次密码是否一致
        if password != confirm:
            self.status_label.setText('两次密码不一致')
            return
        
        # 调用数据库注册方法
        success, result = self.db.register_user(username, password)
        
        if success:
            # 注册成功提示
            QMessageBox.information(self, '注册成功', '账号创建成功！请登录')
            self.register_success.emit(username, password)  # 发射注册成功信号
            self.close()  # 关闭注册窗口
        else:
            self.status_label.setText(result)  # 显示错误信息