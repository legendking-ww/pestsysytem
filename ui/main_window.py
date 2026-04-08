"""
主窗口 - 左中右三栏布局（CPU优化版）
左边：功能按钮
中间：图片显示
右边：结果展示
"""

from backend.resource_monitor import ResourceMonitor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import cv2
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.model_service import ModelService
from backend.database import Database
from ui.history_window import HistoryWindow


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.model_service = ModelService()
        self.db = Database()

        self.camera = None
        self.is_camera_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)
        self.frame_counter = 0  # 跳帧计数器

        # 初始化资源监控
        self.resource_monitor = ResourceMonitor()
        self.resource_monitor.start_monitoring(interval=1)

        # 添加定时器更新状态栏显示
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_bar)
        self.status_timer.start(2000)  # 每2秒更新一次

        # 存储历史记录（每次手动检测）
        self.history_records = []          # 记录列表
        self.current_record_index = -1     # 当前选中的记录索引

        self.init_ui()
        self.init_menu_bar()
        self.statusBar().showMessage(f'欢迎回来，{user_info["username"]} · 模型已就绪')

    def init_ui(self):
        self.setWindowTitle(f'农林昆虫识别系统 · {self.user_info["username"]}')
        self.setGeometry(100, 100, 1500, 850)

        # 让窗口居中显示
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

        # 样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QPushButton#secondary {
                background-color: #2196F3;
            }
            QPushButton#secondary:hover {
                background-color: #1976D2;
            }
            QPushButton#warning {
                background-color: #ff9800;
            }
            QPushButton#warning:hover {
                background-color: #f57c00;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px dashed #cccccc;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
                color: #2c3e50;
                background-color: white;
            }
            QTableWidget {
                border: 2px dashed #cccccc;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #4CAF50;
                font-weight: bold;
                color: #2c3e50;
                font-size: 13px;
            }
            QLabel#imageLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: white;
            }
            QFrame {
                background-color: white;
                border: 2px dashed #cccccc;
                border-radius: 10px;
            }
            QFrame#noBorder {
                border: none;
                background-color: transparent;
            }
            QTabWidget::pane {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: white;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 15px;
                margin-right: 2px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #4CAF50;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(25)

        # ========== 左侧面板：功能按钮 ==========
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setFixedWidth(260)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(20)

        # 用户信息卡片
        user_card = QFrame()
        user_card.setObjectName("noBorder")
        user_card.setStyleSheet("QFrame#noBorder { background-color: transparent; border: none; }")
        user_layout = QVBoxLayout(user_card)
        user_layout.setSpacing(10)

        avatar = QLabel('👤')
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("font-size: 60px; background-color: transparent; border: none;")
        user_layout.addWidget(avatar)

        username_label = QLabel(self.user_info['username'])
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; border: none;")
        user_layout.addWidget(username_label)

        role_label = QLabel('普通用户')
        role_label.setAlignment(Qt.AlignCenter)
        role_label.setStyleSheet("color: #7f8c8d; font-size: 14px; border: none;")
        user_layout.addWidget(role_label)

        left_layout.addWidget(user_card)
        left_layout.addSpacing(15)

        # 功能按钮组
        btn_group = QFrame()
        btn_group.setObjectName("noBorder")
        btn_group.setStyleSheet("QFrame#noBorder { background-color: transparent; border: none; }")
        btn_layout = QVBoxLayout(btn_group)
        btn_layout.setContentsMargins(5, 0, 5, 0)
        btn_layout.setSpacing(15)

        group_label = QLabel('⚡ 快速操作')
        group_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 5px; border: none;")
        btn_layout.addWidget(group_label)

        self.select_btn = QPushButton('📁 选择图片')
        self.select_btn.setObjectName('secondary')
        self.select_btn.setMinimumHeight(48)
        self.select_btn.clicked.connect(self.select_image)
        btn_layout.addWidget(self.select_btn)

        self.detect_btn = QPushButton('🔍 开始识别')
        self.detect_btn.setEnabled(False)
        self.detect_btn.setMinimumHeight(48)
        self.detect_btn.clicked.connect(self.detect_image)
        btn_layout.addWidget(self.detect_btn)

        self.camera_btn = QPushButton('📷 实时识别')
        self.camera_btn.setObjectName('warning')
        self.camera_btn.setMinimumHeight(48)
        self.camera_btn.clicked.connect(self.toggle_camera)
        btn_layout.addWidget(self.camera_btn)

        self.history_btn = QPushButton('📋 历史记录')
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 12px 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                min-height: 48px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        self.history_btn.setMinimumHeight(48)
        self.history_btn.clicked.connect(self.show_history)
        btn_layout.addWidget(self.history_btn)

        btn_layout.addSpacing(25)

        help_label = QLabel('ℹ️ 帮助')
        help_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; border: none;")
        btn_layout.addWidget(help_label)

        help_text = QLabel('1. 选择图片后点击识别\n2. 支持jpg/png格式\n3. 实时识别需连接摄像头')
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 8px; line-height: 1.6; border: none;")
        btn_layout.addWidget(help_text)

        left_layout.addWidget(btn_group)
        left_layout.addStretch()

        # ========== 中间面板：图片显示 ==========
        middle_panel = QFrame()
        middle_panel.setObjectName("middlePanel")
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.setContentsMargins(15, 15, 15, 15)
        middle_layout.setSpacing(15)

        self.image_label = QLabel()
        self.image_label.setObjectName('imageLabel')
        self.image_label.setMinimumSize(750, 550)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText('⚡ 请选择图片或打开摄像头')
        self.image_label.setStyleSheet("""
            QLabel#imageLabel {
                background-color: white;
                border: 2px dashed #cccccc;
                border-radius: 10px;
                font-size: 18px;
                color: #95a5a6;
            }
        """)
        middle_layout.addWidget(self.image_label, 8)

        info_bar = QFrame()
        info_bar.setObjectName("infoBar")
        info_bar.setStyleSheet("""
            QFrame#infoBar {
                background-color: white;
                border: 2px dashed #cccccc;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(15, 8, 15, 8)

        self.file_name_label = QLabel('未选择文件')
        self.file_name_label.setStyleSheet("color: #2c3e50; font-size: 14px; font-weight: 500; border: none;")

        self.image_size_label = QLabel('0x0')
        self.image_size_label.setStyleSheet("color: #7f8c8d; font-size: 14px; border: none;")

        info_layout.addWidget(self.file_name_label)
        info_layout.addStretch()
        info_layout.addWidget(self.image_size_label)

        middle_layout.addWidget(info_bar, 1)

        # ========== 右侧面板：结果显示 ==========
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_panel.setFixedWidth(450)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(20)

        # 统计卡片
        stats_card = QFrame()
        stats_card.setObjectName("statsCard")
        stats_card.setStyleSheet("""
            QFrame#statsCard {
                background-color: white;
                border: 2px dashed #cccccc;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setSpacing(20)

        total_widget = QWidget()
        total_widget.setStyleSheet("border: none;")
        total_layout = QVBoxLayout(total_widget)
        total_layout.setSpacing(8)

        total_label = QLabel('检测目标')
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("color: #7f8c8d; font-size: 15px; font-weight: 500; border: none;")

        self.total_value = QLabel('0')
        self.total_value.setAlignment(Qt.AlignCenter)
        self.total_value.setStyleSheet("font-size: 40px; font-weight: bold; color: #4CAF50; border: none;")

        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_value)
        stats_layout.addWidget(total_widget)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("background-color: #e0e0e0; width: 2px; border: none;")
        stats_layout.addWidget(line)

        time_widget = QWidget()
        time_widget.setStyleSheet("border: none;")
        time_layout = QVBoxLayout(time_widget)
        time_layout.setSpacing(8)

        time_label = QLabel('处理时间')
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setStyleSheet("color: #7f8c8d; font-size: 15px; font-weight: 500; border: none;")

        self.time_value = QLabel('0ms')
        self.time_value.setAlignment(Qt.AlignCenter)
        self.time_value.setStyleSheet("font-size: 28px; color: #2196F3; font-weight: bold; border: none;")

        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_value)
        stats_layout.addWidget(time_widget)

        right_layout.addWidget(stats_card)

        # 标签页控件
        self.result_tab = QTabWidget()
        self.result_tab.setStyleSheet("""
            QTabWidget::pane {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: white;
            }
        """)

        # 标签页1：历史记录列表
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(10, 10, 10, 10)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(2)
        self.history_table.setHorizontalHeaderLabels(['序号', '图片名'])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f9f9f9;
                border: none;
            }
        """)
        self.history_table.verticalHeader().setDefaultSectionSize(35)
        self.history_table.cellClicked.connect(self.on_history_clicked)

        history_layout.addWidget(self.history_table)
        self.result_tab.addTab(history_widget, "📋 历史记录")

        # 标签页2：检测详情
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(10, 10, 10, 10)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(['序号', '昆虫类别', '置信度'])

        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)

        self.result_table.setColumnWidth(0, 70)
        self.result_table.setColumnWidth(2, 100)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f9f9f9;
                border: none;
            }
        """)
        self.result_table.verticalHeader().setDefaultSectionSize(45)

        detail_layout.addWidget(self.result_table)
        self.result_tab.addTab(detail_widget, "🔍 检测详情")

        right_layout.addWidget(self.result_tab, 1)

        # 将三栏添加到主布局
        main_layout.addWidget(left_panel)
        main_layout.addWidget(middle_panel, 3)
        main_layout.addWidget(right_panel, 1)

        self.current_image = None

    def init_menu_bar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()

        file_menu = menubar.addMenu('文件')
        open_action = QAction('打开图片', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.select_image)
        file_menu.addAction(open_action)

        save_action = QAction('保存结果', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_result)
        file_menu.addAction(save_action)

        file_menu.addSeparator()
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu('视图')
        full_action = QAction('全屏', self)
        full_action.setShortcut('F11')
        full_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(full_action)

        help_menu = menubar.addMenu('帮助')
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    # ---------- 历史记录管理 ----------
    def add_to_history(self, record):
        """添加一条检测记录到历史列表"""
        record_id = len(self.history_records) + 1
        record['id'] = record_id
        self.history_records.append(record)

        row = self.history_table.rowCount()
        self.history_table.insertRow(row)

        seq_item = QTableWidgetItem(str(record_id))
        seq_item.setTextAlignment(Qt.AlignCenter)
        seq_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.history_table.setItem(row, 0, seq_item)

        file_name = os.path.basename(record['image_path'])
        name_item = QTableWidgetItem(file_name)
        name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.history_table.setItem(row, 1, name_item)

        # 自动选中新记录并切换到详情页
        self.history_table.selectRow(row)
        self.current_record_index = row
        self.load_history_record(record)
        self.result_tab.setCurrentIndex(1)

    def load_history_record(self, record):
        """加载历史记录到界面"""
        if os.path.exists(record['result_path']):
            pixmap = QPixmap(record['result_path'])
            available_width = self.image_label.width() - 20
            available_height = self.image_label.height() - 20
            if available_width > 0 and available_height > 0:
                scaled = pixmap.scaled(available_width, available_height,
                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled)

        self.total_value.setText(str(record['total_count']))
        self.time_value.setText(f"{record['process_time']*1000:.0f}ms")

        detections = record['detections']
        self.result_table.setRowCount(len(detections))
        for i, det in enumerate(detections):
            seq_item = QTableWidgetItem(str(i+1))
            seq_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(i, 0, seq_item)

            class_item = QTableWidgetItem(det['class_name'])
            class_item.setForeground(QBrush(QColor(44, 62, 80)))
            class_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(i, 1, class_item)

            conf_item = QTableWidgetItem(f"{det['confidence']:.2%}")
            conf_item.setForeground(QBrush(QColor(76, 175, 80)))
            conf_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(i, 2, conf_item)

        self.file_name_label.setText(os.path.basename(record['image_path']))

    def on_history_clicked(self, row, col):
        """点击历史记录行"""
        if 0 <= row < len(self.history_records):
            record = self.history_records[row]
            self.current_record_index = row
            self.load_history_record(record)
            self.result_tab.setCurrentIndex(1)

    # ---------- 原有功能方法 ----------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'current_image') and self.current_image:
            pixmap = QPixmap(self.current_image)
            available_width = self.image_label.width() - 20
            available_height = self.image_label.height() - 20
            if available_width > 0 and available_height > 0:
                scaled = pixmap.scaled(available_width, available_height,
                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled)
        elif hasattr(self, 'is_camera_running') and self.is_camera_running:
            pass

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, '选择图片', '', '图片文件 (*.jpg *.jpeg *.png *.bmp)'
        )
        if path:
            self.current_image = path
            pixmap = QPixmap(path)
            available_width = self.image_label.width() - 20
            available_height = self.image_label.height() - 20
            if available_width > 0 and available_height > 0:
                scaled = pixmap.scaled(available_width, available_height,
                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled)
            self.detect_btn.setEnabled(True)

            self.file_name_label.setText(os.path.basename(path))
            self.image_size_label.setText(f"{pixmap.width()}x{pixmap.height()}")

    def detect_image(self):
        if not self.current_image:
            return

        self.detect_btn.setEnabled(False)
        self.detect_btn.setText('识别中...')

        result = self.model_service.detect_image(self.current_image)

        if 'error' in result:
            QMessageBox.critical(self, '错误', result['error'])
        else:
            # 创建记录并添加到历史
            record = {
                'image_path': self.current_image,
                'result_path': result['image_path'],
                'detections': result['detections'],
                'total_count': result['total_count'],
                'process_time': result['process_time']
            }
            self.add_to_history(record)

            # 保存到数据库
            self.db.save_detection(
                self.user_info['id'],
                os.path.basename(self.current_image),
                result['image_path'],
                result['detections'],
                result['total_count']
            )

        self.detect_btn.setEnabled(True)
        self.detect_btn.setText('🔍 开始识别')

    def start_camera(self):
        """启动摄像头（CPU优化版）"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                QMessageBox.critical(self, '错误', '无法打开摄像头')
                return

            # CPU优化：降低摄像头分辨率
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

            self.is_camera_running = True
            self.camera_btn.setText('⏹️ 停止识别')
            self.select_btn.setEnabled(False)
            self.detect_btn.setEnabled(False)

            # CPU优化：降低帧率（100ms = 10 FPS）
            self.timer.start(100)

            self.frame_counter = 0

            self.file_name_label.setText('实时识别模式')
            self.image_size_label.setText('480x360')
            self.result_table.setRowCount(0)

        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法打开摄像头: {str(e)}')

    def stop_camera(self):
        """停止摄像头"""
        self.timer.stop()
        if self.camera:
            self.camera.release()
            self.camera = None
        self.is_camera_running = False
        self.camera_btn.setText('📷 实时识别')
        self.select_btn.setEnabled(True)
        if self.current_image:
            self.detect_btn.setEnabled(True)

    def toggle_camera(self):
        if not self.is_camera_running:
            self.start_camera()
        else:
            self.stop_camera()

    def update_camera_frame(self):
        """更新摄像头帧（CPU优化版 - 跳帧处理）"""
        if not self.camera:
            return

        ret, frame = self.camera.read()
        if not ret:
            return

        # CPU优化：每3帧才推理一次
        self.frame_counter += 1
        if self.frame_counter % 3 != 0:
            # 不推理，直接显示原画面
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            available_width = self.image_label.width() - 20
            available_height = self.image_label.height() - 20
            if available_width > 0 and available_height > 0:
                scaled = pixmap.scaled(available_width, available_height,
                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled)
            return

        # 推理帧
        frame, detections = self.model_service.detect_camera_frame(frame)

        # 显示
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_image)
        available_width = self.image_label.width() - 20
        available_height = self.image_label.height() - 20
        if available_width > 0 and available_height > 0:
            scaled = pixmap.scaled(available_width, available_height,
                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)

        self.total_value.setText(str(len(detections)))
        self.time_value.setText('实时')

        # 更新检测详情表格（限制显示数量）
        max_display = 50
        self.result_table.setRowCount(min(len(detections), max_display))
        for i, det in enumerate(detections[:max_display]):
            seq_item = QTableWidgetItem(str(i+1))
            seq_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(i, 0, seq_item)

            class_item = QTableWidgetItem(det['class_name'])
            class_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(i, 1, class_item)

            conf_item = QTableWidgetItem(f"{det['confidence']:.2%}")
            conf_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(i, 2, conf_item)

        # 释放帧内存
        del frame

    def save_result(self):
        if not hasattr(self, 'current_image') or not self.current_image:
            QMessageBox.warning(self, '警告', '没有可保存的结果')
            return

        path, _ = QFileDialog.getSaveFileName(
            self, '保存结果', 'detection_result.jpg', 'JPEG (*.jpg);;PNG (*.png)'
        )
        if path and os.path.exists('images/'):
            import shutil
            latest = 'images/result_latest.jpg'
            if os.path.exists(latest):
                shutil.copy(latest, path)
                QMessageBox.information(self, '完成', '结果已保存')

    def show_history(self):
        self.history_window = HistoryWindow(self.user_info['id'], self.db)
        self.history_window.show()

    def show_about(self):
        QMessageBox.about(
            self,
            '关于系统',
            '🌾 农林昆虫识别系统\n\n'
            '版本: 1.0.0\n'
            '作者: 刘凯\n'
            '专业: 智能科学与技术\n'
            '指导老师: 明吉花、田霖\n\n'
            '基于YOLOv8深度学习模型\n'
            '支持102种农林昆虫识别'
        )

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def update_status_bar(self):
        """更新状态栏显示资源占用"""
        stats = self.resource_monitor.get_current_stats()
        if stats['timestamp']:
            status_text = f"CPU: {stats['cpu_percent']}% | 内存: {stats['memory_used_mb']} MB"
            if stats['gpu_used_mb'] > 0:
                status_text += f" | GPU: {stats['gpu_used_mb']} MB"
            self.statusBar().showMessage(status_text)

    def closeEvent(self, event):
        self.resource_monitor.stop_monitoring()
        if self.is_camera_running:
            self.timer.stop()
            if self.camera:
                self.camera.release()
        event.accept()