"""
历史记录窗口 - 使用背景图和角标
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import csv
import os


class HistoryWindow(QWidget):
    """历史记录窗口类"""

    def __init__(self, user_id, database):
        super().__init__()
        self.user_id = user_id
        self.db = database
        self.all_history = []
        self.bg_image_path = os.path.join('resources', 'background', 'bkg.jpg')
        self.icon_image_path = os.path.join('resources', 'icons', 'icon.png')
        self.init_ui()
        self.load_history()

    def init_ui(self):
        self.setWindowTitle('Detection History Records')
        self.setFixedSize(1000, 650)
        self.setMinimumSize(1000, 650)
        
        # 设置窗口图标
        icon = QIcon(self.icon_image_path)
        self.setWindowIcon(icon)

        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QPushButton {
                background-color: #7cb342;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 22px;
                font-size: 13px;
                font-weight: bold;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #8bc34a;
            }
            QPushButton#secondary {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton#secondary:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton#danger {
                background-color: #e94560;
            }
            QPushButton#danger:hover {
                background-color: #d63651;
            }
            QPushButton#blue {
                background-color: #3b82f6;
            }
            QPushButton#blue:hover {
                background-color: #2563eb;
            }
            QLineEdit {
                padding: 12px 18px;
                border: 2px solid rgba(200, 200, 200, 0.5);
                border-radius: 22px;
                font-size: 14px;
                background-color: rgba(255, 255, 255, 0.93);
                color: #333333;
            }
            QLineEdit:focus {
                border: 3px solid #7cb342;
                background-color: rgba(255, 255, 255, 0.95);
            }
            QLineEdit::placeholder {
                color: #999999;
            }
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.93);
                border: 1px solid rgba(200, 200, 200, 0.5);
                border-radius: 10px;
                gridline-color: rgba(240, 240, 240, 0.8);
                font-size: 14px;
                color: #333333;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid rgba(240, 240, 240, 0.8);
            }
            QTableWidget::item:selected {
                background-color: rgba(124, 179, 66, 0.25);
                color: #333333;
            }
            QHeaderView::section {
                background-color: rgba(240, 244, 240, 0.95);
                padding: 14px 8px;
                border: none;
                border-bottom: 2px solid #7cb342;
                font-weight: bold;
                color: #333333;
                font-size: 13px;
            }
            QFrame#panel {
                background-color: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(200, 200, 200, 0.5);
                border-radius: 12px;
            }
            QFrame#card {
                background-color: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(220, 220, 220, 0.5);
                border-radius: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(245, 245, 245, 0.8);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(192, 192, 192, 0.8);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(160, 160, 160, 0.8);
            }

        """)

        main_layout = QStackedLayout()
        main_layout.setStackingMode(QStackedLayout.StackAll)

        bg_label = QLabel()
        bg_pixmap = QPixmap(self.bg_image_path)
        if not bg_pixmap.isNull():
            bg_label.setPixmap(bg_pixmap.scaled(1000, 650, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            bg_label.setStyleSheet("background-color: #1a2e1a;")
        bg_label.setFixedSize(1000, 650)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(18)

        header = self.create_header()
        container_layout.addWidget(header)

        search_bar = self.create_search_bar()
        container_layout.addWidget(search_bar)

        self.table = self.create_table()
        container_layout.addWidget(self.table, 1)

        bottom_bar = self.create_bottom_bar()
        container_layout.addWidget(bottom_bar)

        main_layout.addWidget(bg_label)
        main_layout.addWidget(container)

        self.setLayout(main_layout)

    def create_header(self):
        header = QFrame()
        header.setObjectName("panel")
        header.setFixedHeight(70)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 15, 20, 15)

        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_pixmap = QPixmap(self.icon_image_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setText('LOGO')
            icon_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #ffffff; background-color: rgba(124, 179, 66, 0.9); padding: 5px; border-radius: 20px;")
        layout.addWidget(icon_label)

        title = QLabel('DETECTION HISTORY RECORDS')
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #333333;
            letter-spacing: 3px;
        """)
        layout.addWidget(title)

        self.stats_label = QLabel('Total: 0 records')
        self.stats_label.setStyleSheet("""
            color: #666666;
            font-size: 13px;
            padding: 6px 16px;
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(200, 200, 200, 0.5);
            border-radius: 20px;
        """)
        layout.addWidget(self.stats_label)

        layout.addStretch()

        return header

    def create_search_bar(self):
        search_widget = QFrame()
        search_widget.setObjectName("panel")
        search_widget.setFixedHeight(60)

        layout = QHBoxLayout(search_widget)
        layout.setContentsMargins(15, 10, 15, 10)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Search by image name...')
        self.search_box.textChanged.connect(self.filter_history)
        layout.addWidget(self.search_box, 1)

        self.refresh_btn = QPushButton('Refresh')
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setFixedWidth(100)
        self.refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(self.refresh_btn)

        return search_widget

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['ID', 'Image Name', 'Detection Time', 'Target Count', 'Actions'])
        table.horizontalHeader().setStretchLastSection(False)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 300)
        table.setColumnWidth(2, 180)
        table.setColumnWidth(3, 100)
        table.setColumnWidth(4, 200)

        return table

    def create_bottom_bar(self):
        bottom = QFrame()
        bottom.setObjectName("panel")
        bottom.setFixedHeight(60)

        layout = QHBoxLayout(bottom)
        layout.setContentsMargins(15, 10, 15, 10)

        left_buttons = QWidget()
        left_layout = QHBoxLayout(left_buttons)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        self.export_btn = QPushButton('Export CSV')
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setObjectName('blue')
        self.export_btn.setFixedWidth(120)
        self.export_btn.clicked.connect(self.export_history)
        left_layout.addWidget(self.export_btn)

        self.clear_btn = QPushButton('Clear All')
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setObjectName('danger')
        self.clear_btn.setFixedWidth(120)
        self.clear_btn.clicked.connect(self.clear_history)
        left_layout.addWidget(self.clear_btn)

        layout.addWidget(left_buttons)

        layout.addStretch()

        self.close_btn = QPushButton('Close')
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setObjectName('secondary')
        self.close_btn.setFixedWidth(100)
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        return bottom

    def load_history(self):
        try:
            history = self.db.get_user_history(self.user_id)
            self.all_history = history
            self.update_table(history)
            self.stats_label.setText(f'Total: {len(history)} records')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load history: {str(e)}')

    def update_table(self, history):
        self.table.setRowCount(len(history))

        for i, record in enumerate(history):
            id_item = QTableWidgetItem(str(record['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setForeground(QBrush(QColor(160, 160, 160)))
            self.table.setItem(i, 0, id_item)

            name_item = QTableWidgetItem(record['image_name'])
            name_item.setForeground(QBrush(QColor(234, 234, 234)))
            name_item.setFont(QFont('Segoe UI', 10, QFont.Medium))
            self.table.setItem(i, 1, name_item)

            time_str = str(record['time'])[:19]
            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setForeground(QBrush(QColor(160, 160, 160)))
            self.table.setItem(i, 2, time_item)

            count = record['total']
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignCenter)

            if count > 10:
                color = '#10b981'
            elif count > 5:
                color = '#f59e0b'
            elif count > 0:
                color = '#3b82f6'
            else:
                color = '#7f8c8d'

            count_item.setForeground(QBrush(QColor(color)))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, count_item)

            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setSpacing(8)

            view_btn = QPushButton('View')
            view_btn.setCursor(Qt.PointingHandCursor)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    padding: 6px 14px;
                    border-radius: 18px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            view_btn.clicked.connect(lambda checked, r=record: self.show_detail(r))
            btn_layout.addWidget(view_btn)

            delete_btn = QPushButton('Delete')
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e94560;
                    color: white;
                    border: none;
                    padding: 6px 14px;
                    border-radius: 18px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #d63651;
                }
            """)
            delete_btn.clicked.connect(lambda checked, r=record: self.delete_record(r))
            btn_layout.addWidget(delete_btn)

            self.table.setCellWidget(i, 4, btn_container)

    def filter_history(self):
        search_text = self.search_box.text().lower().strip()

        if not search_text:
            self.update_table(self.all_history)
            self.stats_label.setText(f'Total: {len(self.all_history)} records')
            return

        filtered = [
            r for r in self.all_history
            if search_text in r['image_name'].lower()
        ]

        self.update_table(filtered)
        self.stats_label.setText(f'Found: {len(filtered)} records')

    def show_detail(self, record):
        dialog = QDialog(self)
        dialog.setWindowTitle('Detection Details')
        dialog.setFixedSize(550, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: transparent;
            }
            QWidget {
                background-color: transparent;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
        """)

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        bg_label = QLabel(dialog)
        bg_pixmap = QPixmap(self.bg_image_path)
        if not bg_pixmap.isNull():
            bg_label.setPixmap(bg_pixmap.scaled(550, 500, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            bg_label.setStyleSheet("background-color: #1a2e1a;")
        bg_label.setFixedSize(550, 500)

        stacked_layout = QStackedLayout()
        stacked_layout.setStackingMode(QStackedLayout.StackAll)
        stacked_layout.addWidget(bg_label)

        container = QWidget(dialog)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(15)

        info_card = QFrame()
        info_card.setObjectName("card")
        info_layout = QFormLayout(info_card)
        info_layout.setSpacing(12)
        info_layout.setLabelAlignment(Qt.AlignRight)

        labels = [
            ('Image Name', record['image_name']),
            ('Detection Time', str(record['time'])[:19]),
            ('Total Targets', str(record['total']))
        ]

        for label, value in labels:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: 600; color: #a0a0a0;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #ffffff; background-color: rgba(26, 26, 46, 0.9); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.1);")
            info_layout.addRow(label_widget, value_widget)

        container_layout.addWidget(info_card)

        result_card = QFrame()
        result_card.setObjectName("card")
        result_layout = QVBoxLayout(result_card)

        result_label = QLabel('Detection Results')
        result_label.setStyleSheet("font-weight: bold; color: #7cb342; font-size: 14px; margin-bottom: 8px;")
        result_layout.addWidget(result_label)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['No.', 'Insect Category', 'Confidence'])
        table.horizontalHeader().setStretchLastSection(False)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                background-color: rgba(26, 26, 46, 0.9);
                color: #eaeaea;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        results = record['results']
        table.setRowCount(len(results))
        table.setColumnWidth(0, 50)
        table.setColumnWidth(1, 200)
        table.setColumnWidth(2, 150)

        for i, det in enumerate(results):
            seq_item = QTableWidgetItem(str(i+1))
            seq_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 0, seq_item)

            class_item = QTableWidgetItem(det['class_name'])
            class_item.setForeground(QBrush(QColor(234, 234, 234)))
            class_item.setFont(QFont('Segoe UI', 10))
            table.setItem(i, 1, class_item)

            confidence = det['confidence']
            conf_item = QTableWidgetItem(f"{confidence:.2%}")
            conf_item.setTextAlignment(Qt.AlignCenter)

            if confidence >= 0.8:
                color = '#10b981'
            elif confidence >= 0.5:
                color = '#f59e0b'
            else:
                color = '#e94560'

            conf_item.setForeground(QBrush(QColor(color)))
            conf_item.setFont(QFont('Segoe UI', 10, QFont.Bold))
            table.setItem(i, 2, conf_item)

        result_layout.addWidget(table)
        container_layout.addWidget(result_card, 1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        close_btn = QPushButton('Close')
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(120, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #7cb342;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #8bc34a;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)

        container_layout.addLayout(btn_layout)

        stacked_layout.addWidget(container)
        main_layout.addLayout(stacked_layout)

        dialog.exec_()

    def export_history(self):
        if not self.all_history:
            QMessageBox.warning(self, 'Notice', 'No history records to export')
            return

        path, _ = QFileDialog.getSaveFileName(
            self, 'Export History',
            f'detection_history_{QDate.currentDate().toString("yyyyMMdd")}.csv',
            'CSV Files (*.csv)'
        )

        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Image Name', 'Detection Time', 'Target Count', 'Detection Details'])

                    for record in self.all_history:
                        results_str = '; '.join([
                            f"{d['class_name']}({d['confidence']:.1%})"
                            for d in record['results']
                        ])
                        writer.writerow([
                            record['id'],
                            record['image_name'],
                            str(record['time'])[:19],
                            record['total'],
                            results_str
                        ])

                QMessageBox.information(
                    self, 'Success',
                    f'Successfully exported {len(self.all_history)} records'
                )
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Export failed: {str(e)}')

    def clear_history(self):
        if not self.all_history:
            QMessageBox.warning(self, 'Notice', 'History is already empty')
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('Confirm Clear')
        msg_box.setText('Are you sure you want to clear all history records?')
        msg_box.setInformativeText('This action will permanently delete all records and cannot be undone.')
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        yes_btn = msg_box.button(QMessageBox.Yes)
        yes_btn.setText('Yes, Clear')
        yes_btn.setStyleSheet("background-color: #e94560;")

        no_btn = msg_box.button(QMessageBox.No)
        no_btn.setText('Cancel')

        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            try:
                deleted_count = self.db.clear_user_history(self.user_id)
                self.load_history()
                QMessageBox.information(
                    self, 'Success',
                    f'Successfully cleared {deleted_count} records'
                )
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to clear history: {str(e)}')

    def delete_record(self, record):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('Confirm Delete')
        msg_box.setText('Are you sure you want to delete this record?')
        msg_box.setInformativeText(f'Image: {record["image_name"]}\nTime: {str(record["time"])[:19]}')
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        yes_btn = msg_box.button(QMessageBox.Yes)
        yes_btn.setText('Yes, Delete')
        yes_btn.setStyleSheet("background-color: #e94560;")

        no_btn = msg_box.button(QMessageBox.No)
        no_btn.setText('Cancel')

        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            try:
                success = self.db.delete_history_record(record['id'], self.user_id)

                if success:
                    self.load_history()
                    QMessageBox.information(
                        self, 'Success',
                        'Record deleted successfully'
                    )
                else:
                    QMessageBox.warning(
                        self, 'Failed',
                        'Delete failed, record may not exist or no permission'
                    )
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to delete record: {str(e)}')