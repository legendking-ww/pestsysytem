"""
主窗口 - 左中右三栏布局（使用背景图和角标）
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
        self.bg_image_path = os.path.join('resources', 'background', 'bkg.jpg')
        self.icon_image_path = os.path.join('resources', 'icons', 'icon.png')

        self.camera = None
        self.is_camera_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)
        self.frame_counter = 0

        self.resource_monitor = ResourceMonitor()
        self.resource_monitor.start_monitoring(interval=1)

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_bar)
        self.status_timer.start(2000)

        self.history_records = []
        self.current_record_index = -1

        self.init_ui()
        self.init_menu_bar()
        self.statusBar().showMessage(f'Welcome, {user_info["username"]} | Model Ready')

    def init_ui(self):
        self.setWindowTitle(f'Pest Identification System | {self.user_info["username"]}')
        self.setFixedSize(1400, 800)
        self.setMinimumSize(1400, 800)
        
        # 设置窗口图标
        icon = QIcon(self.icon_image_path)
        self.setWindowIcon(icon)

        # 创建主窗口部件
        main_widget = QWidget()
        
        # 创建背景标签
        bg_label = QLabel()
        bg_label.setFixedSize(1400, 800)
        bg_pixmap = QPixmap(self.bg_image_path)
        if not bg_pixmap.isNull():
            bg_label.setPixmap(bg_pixmap.scaled(1400, 800, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            bg_label.setStyleSheet("background-color: #f0f4f0;")

        # 创建内容容器
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 左侧面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # 中间面板
        middle_panel = self.create_middle_panel()
        main_layout.addWidget(middle_panel, 3)

        # 右侧面板
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)

        # 使用堆叠布局，背景在下，内容在上
        stacked_layout = QStackedLayout()
        stacked_layout.setStackingMode(QStackedLayout.StackAll)
        stacked_layout.addWidget(bg_label)
        stacked_layout.addWidget(container)
        
        main_widget.setLayout(stacked_layout)
        self.setCentralWidget(main_widget)

    def create_left_panel(self):
        left_panel = QFrame()
        left_panel.setFixedWidth(240)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(200, 200, 200, 0.5);
                border-radius: 16px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(18, 22, 18, 22)
        left_layout.setSpacing(14)

        # 图标
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(56, 56)
        icon_pixmap = QPixmap(self.icon_image_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setText('LOGO')
            icon_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #7cb342; background-color: rgba(124, 179, 66, 0.2); padding: 8px; border-radius: 28px;")
        left_layout.addWidget(icon_label)

        # 用户名
        username_label = QLabel(self.user_info['username'])
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setStyleSheet("font-size: 17px; font-weight: bold; color: #333333; background-color: transparent;")
        left_layout.addWidget(username_label)

        # 角色
        role_label = QLabel('Standard User')
        role_label.setAlignment(Qt.AlignCenter)
        role_label.setStyleSheet("color: #888888; font-size: 11px; background-color: transparent;")
        left_layout.addWidget(role_label)

        left_layout.addSpacing(22)

        # 操作标题
        section_title = QLabel('ACTIONS')
        section_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #666666; letter-spacing: 2px; background-color: transparent;")
        left_layout.addWidget(section_title)

        # 选择图片按钮 - 蓝色
        self.select_btn = QPushButton('Select Image')
        self.select_btn.setMinimumHeight(48)
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(59, 130, 246, 0.9);
                color: white;
                border: none;
                padding: 12px 18px;
                border-radius: 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(37, 99, 235, 1.0);
            }
            QPushButton:disabled {
                background-color: rgba(200, 200, 200, 0.8);
                color: #888888;
            }
        """)
        self.select_btn.clicked.connect(self.select_image)
        left_layout.addWidget(self.select_btn)

        # 开始检测按钮 - 绿色
        self.detect_btn = QPushButton('Start Detection')
        self.detect_btn.setEnabled(False)
        self.detect_btn.setMinimumHeight(48)
        self.detect_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(124, 179, 66, 0.9);
                color: white;
                border: none;
                padding: 12px 18px;
                border-radius: 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(104, 159, 56, 1.0);
            }
            QPushButton:disabled {
                background-color: rgba(200, 200, 200, 0.8);
                color: #888888;
            }
        """)
        self.detect_btn.clicked.connect(self.detect_image)
        left_layout.addWidget(self.detect_btn)

        # 实时检测按钮 - 橙色
        self.camera_btn = QPushButton('Real-time Detection')
        self.camera_btn.setMinimumHeight(48)
        self.camera_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(245, 158, 11, 0.9);
                color: white;
                border: none;
                padding: 12px 18px;
                border-radius: 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(217, 119, 6, 1.0);
            }
            QPushButton:disabled {
                background-color: rgba(200, 200, 200, 0.8);
                color: #888888;
            }
        """)
        self.camera_btn.clicked.connect(self.toggle_camera)
        left_layout.addWidget(self.camera_btn)

        # 历史记录按钮 - 紫色
        self.history_btn = QPushButton('History Records')
        self.history_btn.setMinimumHeight(48)
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(139, 92, 246, 0.9);
                color: white;
                border: none;
                padding: 12px 18px;
                border-radius: 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(124, 58, 237, 1.0);
            }
            QPushButton:disabled {
                background-color: rgba(200, 200, 200, 0.8);
                color: #888888;
            }
        """)
        self.history_btn.clicked.connect(self.show_history)
        left_layout.addWidget(self.history_btn)

        left_layout.addStretch()

        # 提示
        help_title = QLabel('TIPS')
        help_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #666666; letter-spacing: 2px; background-color: transparent;")
        left_layout.addWidget(help_title)

        help_text = QLabel('1. Select image\n2. Start detection\n3. View results')
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #999999; font-size: 11px; line-height: 1.6; background-color: transparent;")
        left_layout.addWidget(help_text)

        return left_panel

    def create_middle_panel(self):
        middle_panel = QFrame()
        middle_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(200, 200, 200, 0.5);
                border-radius: 16px;
            }
        """)
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.setContentsMargins(18, 18, 18, 18)
        middle_layout.setSpacing(15)

        # 图片显示区域
        self.image_label = QLabel()
        self.image_label.setMinimumSize(700, 480)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText('Please select an image or start camera')
        self.image_label.setStyleSheet("""
            background-color: rgba(250, 250, 250, 0.95);
            border: 2px dashed #cccccc;
            border-radius: 12px;
            font-size: 18px;
            color: #999999;
        """)
        middle_layout.addWidget(self.image_label, 8)

        # 信息栏
        info_bar = QFrame()
        info_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(220, 220, 220, 0.5);
                border-radius: 10px;
            }
        """)
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(15, 10, 15, 10)

        self.file_name_label = QLabel('No file selected')
        self.file_name_label.setStyleSheet("color: #666666; font-size: 13px; font-weight: 500; background-color: transparent;")

        self.image_size_label = QLabel('0x0')
        self.image_size_label.setStyleSheet("color: #999999; font-size: 13px; background-color: transparent;")

        info_layout.addWidget(self.file_name_label)
        info_layout.addStretch()
        info_layout.addWidget(self.image_size_label)

        middle_layout.addWidget(info_bar, 1)

        return middle_panel

    def create_right_panel(self):
        right_panel = QFrame()
        right_panel.setFixedWidth(380)
        right_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(200, 200, 200, 0.5);
                border-radius: 16px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(18, 18, 18, 18)
        right_layout.setSpacing(15)

        # 统计卡片
        stats_card = QFrame()
        stats_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(220, 220, 220, 0.5);
                border-radius: 12px;
            }
        """)
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setSpacing(15)

        # 检测数量
        total_widget = QWidget()
        total_widget.setStyleSheet("background-color: transparent;")
        total_layout = QVBoxLayout(total_widget)
        total_layout.setSpacing(5)
        total_layout.setAlignment(Qt.AlignCenter)

        total_label = QLabel('DETECTIONS')
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("color: #7cb342; font-size: 11px; font-weight: bold; letter-spacing: 1px; background-color: transparent;")

        self.total_value = QLabel('0')
        self.total_value.setAlignment(Qt.AlignCenter)
        self.total_value.setStyleSheet("font-size: 34px; font-weight: bold; color: #7cb342; background-color: transparent;")

        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_value)
        stats_layout.addWidget(total_widget)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("background-color: #e0e0e0; width: 2px;")
        stats_layout.addWidget(line)

        # 处理时间
        time_widget = QWidget()
        time_widget.setStyleSheet("background-color: transparent;")
        time_layout = QVBoxLayout(time_widget)
        time_layout.setSpacing(5)
        time_layout.setAlignment(Qt.AlignCenter)

        time_label = QLabel('PROCESS TIME')
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setStyleSheet("color: #3b82f6; font-size: 11px; font-weight: bold; letter-spacing: 1px; background-color: transparent;")

        self.time_value = QLabel('0ms')
        self.time_value.setAlignment(Qt.AlignCenter)
        self.time_value.setStyleSheet("font-size: 22px; color: #3b82f6; font-weight: bold; background-color: transparent;")

        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_value)
        stats_layout.addWidget(time_widget)

        right_layout.addWidget(stats_card)

        # 结果标签页
        self.result_tab = QTabWidget()
        self.result_tab.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(200, 200, 200, 0.5);
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QTabBar::tab {
                background-color: rgba(240, 244, 240, 0.9);
                border: 1px solid rgba(200, 200, 200, 0.5);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 18px;
                margin-right: 2px;
                font-size: 13px;
                color: #666666;
            }
            QTabBar::tab:selected {
                background-color: rgba(255, 255, 255, 0.95);
                border-bottom: 2px solid #7cb342;
                color: #333333;
            }
            QTabBar::tab:hover {
                background-color: rgba(232, 245, 224, 0.9);
                color: #333333;
            }
        """)

        # 历史标签
        history_widget = QWidget()
        history_widget.setStyleSheet("background-color: transparent;")
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(8, 8, 8, 8)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(2)
        self.history_table.setHorizontalHeaderLabels(['No.', 'Image Name'])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.verticalHeader().setDefaultSectionSize(36)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(200, 200, 200, 0.3);
                border-radius: 8px;
                gridline-color: rgba(240, 240, 240, 0.8);
                font-size: 13px;
                color: #333333;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(240, 240, 240, 0.8);
            }
            QTableWidget::item:selected {
                background-color: rgba(124, 179, 66, 0.2);
                color: #333333;
            }
            QHeaderView::section {
                background-color: rgba(240, 244, 240, 0.95);
                padding: 12px;
                border: none;
                border-bottom: 2px solid #7cb342;
                font-weight: bold;
                color: #333333;
                font-size: 12px;
            }
        """)
        self.history_table.cellClicked.connect(self.on_history_clicked)

        history_layout.addWidget(self.history_table)
        self.result_tab.addTab(history_widget, "History")

        # 详情标签
        detail_widget = QWidget()
        detail_widget.setStyleSheet("background-color: transparent;")
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(8, 8, 8, 8)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(['No.', 'Insect Category', 'Confidence'])

        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)

        self.result_table.setColumnWidth(0, 45)
        self.result_table.setColumnWidth(2, 85)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.verticalHeader().setDefaultSectionSize(38)
        self.result_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(200, 200, 200, 0.3);
                border-radius: 8px;
                gridline-color: rgba(240, 240, 240, 0.8);
                font-size: 13px;
                color: #333333;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(240, 240, 240, 0.8);
            }
            QTableWidget::item:selected {
                background-color: rgba(124, 179, 66, 0.2);
                color: #333333;
            }
            QHeaderView::section {
                background-color: rgba(240, 244, 240, 0.95);
                padding: 12px;
                border: none;
                border-bottom: 2px solid #7cb342;
                font-weight: bold;
                color: #333333;
                font-size: 12px;
            }
        """)

        detail_layout.addWidget(self.result_table)
        self.result_tab.addTab(detail_widget, "Detection Details")

        right_layout.addWidget(self.result_tab, 1)

        return right_panel

    def add_to_history(self, record):
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

        self.history_table.selectRow(row)
        self.current_record_index = row
        self.load_history_record(record)
        self.result_tab.setCurrentIndex(1)

    def load_history_record(self, record):
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
            class_item.setForeground(QBrush(QColor(51, 51, 51)))
            class_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(i, 1, class_item)

            conf_item = QTableWidgetItem(f"{det['confidence']:.2%}")
            conf_item.setForeground(QBrush(QColor(124, 179, 66)))
            conf_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(i, 2, conf_item)

        self.file_name_label.setText(os.path.basename(record['image_path']))

    def on_history_clicked(self, row, col):
        if 0 <= row < len(self.history_records):
            record = self.history_records[row]
            self.current_record_index = row
            self.load_history_record(record)
            self.result_tab.setCurrentIndex(1)

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

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Select Image', '', 'Image Files (*.jpg *.jpeg *.png *.bmp)'
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
        self.detect_btn.setText('Detecting...')

        result = self.model_service.detect_image(self.current_image)

        if 'error' in result:
            QMessageBox.critical(self, 'Error', result['error'])
        else:
            record = {
                'image_path': self.current_image,
                'result_path': result['image_path'],
                'detections': result['detections'],
                'total_count': result['total_count'],
                'process_time': result['process_time']
            }
            self.add_to_history(record)

            self.db.save_detection(
                self.user_info['id'],
                os.path.basename(self.current_image),
                result['image_path'],
                result['detections'],
                result['total_count']
            )

        self.detect_btn.setEnabled(True)
        self.detect_btn.setText('Start Detection')

    def start_camera(self):
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                QMessageBox.critical(self, 'Error', 'Cannot open camera')
                return

            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

            self.is_camera_running = True
            self.camera_btn.setText('Stop Detection')
            self.select_btn.setEnabled(False)
            self.detect_btn.setEnabled(False)

            self.timer.start(100)

            self.frame_counter = 0

            self.file_name_label.setText('Real-time Detection Mode')
            self.image_size_label.setText('480x360')
            self.result_table.setRowCount(0)

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Cannot open camera: {str(e)}')

    def stop_camera(self):
        self.timer.stop()
        if self.camera:
            self.camera.release()
            self.camera = None
        self.is_camera_running = False
        self.camera_btn.setText('Real-time Detection')
        self.select_btn.setEnabled(True)
        if self.current_image:
            self.detect_btn.setEnabled(True)

    def toggle_camera(self):
        if not self.is_camera_running:
            self.start_camera()
        else:
            self.stop_camera()

    def update_camera_frame(self):
        if not self.camera:
            return

        ret, frame = self.camera.read()
        if not ret:
            return

        self.frame_counter += 1
        if self.frame_counter % 3 != 0:
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

        frame, detections = self.model_service.detect_camera_frame(frame)

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
        self.time_value.setText('Real-time')

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

        del frame

    def save_result(self):
        if not hasattr(self, 'current_image') or not self.current_image:
            QMessageBox.warning(self, 'Warning', 'No result to save')
            return

        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Result', 'detection_result.jpg', 'JPEG (*.jpg);;PNG (*.png)'
        )
        if path and os.path.exists('images/'):
            import shutil
            latest = 'images/result_latest.jpg'
            if os.path.exists(latest):
                shutil.copy(latest, path)
                QMessageBox.information(self, 'Success', 'Result saved successfully')

    def show_history(self):
        self.history_window = HistoryWindow(self.user_info['id'], self.db)
        self.history_window.show()

    def show_about(self):
        QMessageBox.about(
            self,
            'About System',
            'PEST IDENTIFICATION SYSTEM\n\n'
            'Version: 1.0.0\n'
            'Author: Kai Liu\n'
            'Major: Intelligent Science and Technology\n'
            'Mentors: Jihua Ming, Lin Tian\n\n'
            'Based on YOLOv8 Deep Learning Model\n'
            'Supports 102 types of agricultural and forestry insect recognition'
        )

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def update_status_bar(self):
        stats = self.resource_monitor.get_current_stats()
        if stats['timestamp']:
            status_text = f"CPU: {stats['cpu_percent']}% | Memory: {stats['memory_used_mb']} MB"
            if stats['gpu_used_mb'] > 0:
                status_text += f" | GPU: {stats['gpu_used_mb']} MB"
            self.statusBar().showMessage(status_text)

    def init_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: rgba(240, 244, 240, 0.95);
                color: #333333;
                border: none;
            }
            QMenuBar::item:selected {
                background-color: rgba(232, 245, 224, 0.9);
            }
            QMenu {
                background-color: rgba(255, 255, 255, 0.98);
                color: #333333;
                border: 1px solid rgba(200, 200, 200, 0.5);
            }
            QMenu::item:selected {
                background-color: rgba(124, 179, 66, 0.2);
            }
        """)

        file_menu = menubar.addMenu('File')
        open_action = QAction('Open Image', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.select_image)
        file_menu.addAction(open_action)

        save_action = QAction('Save Result', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_result)
        file_menu.addAction(save_action)

        file_menu.addSeparator()
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu('View')
        full_action = QAction('Fullscreen', self)
        full_action.setShortcut('F11')
        full_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(full_action)

        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def closeEvent(self, event):
        self.resource_monitor.stop_monitoring()
        if self.is_camera_running:
            self.timer.stop()
            if self.camera:
                self.camera.release()
        event.accept()
