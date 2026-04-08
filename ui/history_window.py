"""
历史记录窗口 - 展示用户检测历史（优化版）
采用卡片式设计和现代布局，更加简洁大方
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import csv

class HistoryWindow(QWidget):
    """历史记录窗口类（优化版）"""
    
    def __init__(self, user_id, database):
        """初始化历史记录窗口
        
        Args:
            user_id: 当前用户ID
            database: 数据库对象
        """
        super().__init__()
        self.user_id = user_id
        self.db = database
        self.all_history = []
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        """初始化用户界面 - 现代简洁风格"""
        self.setWindowTitle('📊 检测历史记录')
        self.setGeometry(200, 200, 1000, 600)
        self.setMinimumSize(900, 500)
        
        # 设置全局样式 - 清新现代风格
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: none;
                border-radius: 12px;
                background-color: white;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #1e293b;
            }
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                gridline-color: #e2e8f0;
                outline: none;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #e2e8f0;
            }
            QTableWidget::item:selected {
                background-color: #e8f0fe;
                color: #1e293b;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #3b82f6;
                font-weight: 600;
                color: #1e293b;
                font-size: 13px;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton#secondary {
                background-color: #94a3b8;
            }
            QPushButton#secondary:hover {
                background-color: #64748b;
            }
            QPushButton#danger {
                background-color: #ef4444;
            }
            QPushButton#danger:hover {
                background-color: #dc2626;
            }
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                padding: 9px 14px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # ========== 顶部标题栏 ==========
        header = self.create_header()
        main_layout.addWidget(header)
        
        # ========== 搜索和过滤栏 ==========
        search_bar = self.create_search_bar()
        main_layout.addWidget(search_bar)
        
        # ========== 统计卡片 ==========
        stats_cards = self.create_stats_cards()
        main_layout.addWidget(stats_cards)
        
        # ========== 表格区域 ==========
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', '图片名称', '检测时间', '目标数量', ''])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置列宽
        self.table.setColumnWidth(0, 80)   # ID
        self.table.setColumnWidth(1, 280)  # 图片名称
        self.table.setColumnWidth(2, 200)  # 检测时间
        self.table.setColumnWidth(3, 100)  # 目标数量
        self.table.setColumnWidth(4, 120)  # 操作
        
        main_layout.addWidget(self.table, 1)  # 表格占满剩余空间
        
        # ========== 底部操作栏 ==========
        bottom_bar = self.create_bottom_bar()
        main_layout.addWidget(bottom_bar)
    
    def create_header(self):
        """创建顶部标题栏"""
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(60)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题和图标
        title_frame = QWidget()
        title_layout = QHBoxLayout(title_frame)
        title_layout.setSpacing(10)
        
        icon_label = QLabel('📊')
        icon_label.setStyleSheet("font-size: 28px;")
        title_layout.addWidget(icon_label)
        
        title = QLabel('检测历史记录')
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #0f172a;
        """)
        title_layout.addWidget(title)
        
        layout.addWidget(title_frame)
        
        # 统计信息
        self.stats_label = QLabel('加载中...')
        self.stats_label.setStyleSheet("""
            color: #64748b;
            font-size: 14px;
            padding: 5px 15px;
            background-color: #f1f5f9;
            border-radius: 20px;
        """)
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
        
        return header
    
    def create_search_bar(self):
        """创建搜索栏"""
        search_widget = QWidget()
        search_widget.setFixedHeight(50)
        
        layout = QHBoxLayout(search_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 搜索框
        search_container = QWidget()
        search_container.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        """)
        search_container.setFixedHeight(45)
        
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 15, 0)
        
        search_icon = QLabel('🔍')
        search_icon.setStyleSheet("font-size: 16px; color: #94a3b8;")
        search_layout.addWidget(search_icon)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('搜索图片名称...')
        self.search_box.setStyleSheet("""
            border: none;
            background: transparent;
            padding: 8px;
            font-size: 14px;
        """)
        self.search_box.textChanged.connect(self.filter_history)
        search_layout.addWidget(self.search_box)
        
        layout.addWidget(search_container)
        
        # 刷新按钮
        self.refresh_btn = QPushButton('🔄 刷新')
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setFixedWidth(100)
        self.refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(self.refresh_btn)
        
        return search_widget
    
    def create_stats_cards(self):
        """创建统计卡片"""
        cards_widget = QWidget()
        cards_widget.setFixedHeight(100)
        
        layout = QHBoxLayout(cards_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 总记录卡片
        total_card = self.create_stat_card(
            '📋 总记录数', 
            '0', 
            '历史检测总次数',
            '#3b82f6'
        )
        layout.addWidget(total_card)
        
        # 总目标卡片
        targets_card = self.create_stat_card(
            '🐛 总目标数', 
            '0', 
            '识别的昆虫总数',
            '#10b981'
        )
        layout.addWidget(targets_card)
        
        # 平均每图卡片
        avg_card = self.create_stat_card(
            '📊 平均每图', 
            '0', 
            '平均每张图片检测数量',
            '#8b5cf6'
        )
        layout.addWidget(avg_card)
        
        return cards_widget
    
    def create_stat_card(self, title, value, subtitle, color):
        """创建单个统计卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 16px;
                border: none;
            }}
        """)
        card.setFixedHeight(90)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # 左侧图标
        icon_label = QLabel(title.split()[0])
        icon_label.setStyleSheet(f"""
            font-size: 24px;
            background-color: {color}20;
            color: {color};
            padding: 10px;
            border-radius: 12px;
        """)
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # 右侧内容
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(4)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {color};
        """)
        content_layout.addWidget(value_label)
        
        title_label = QLabel(title.split()[1] if len(title.split()) > 1 else title)
        title_label.setStyleSheet("""
            font-size: 14px;
            color: #64748b;
        """)
        content_layout.addWidget(title_label)
        
        layout.addWidget(content, 1)
        
        return card
    
    def create_bottom_bar(self):
        """创建底部操作栏"""
        bottom = QWidget()
        bottom.setFixedHeight(60)
        
        layout = QHBoxLayout(bottom)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧按钮组
        left_buttons = QWidget()
        left_layout = QHBoxLayout(left_buttons)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        self.export_btn = QPushButton('📤 导出CSV')
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.export_btn.clicked.connect(self.export_history)
        left_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton('🗑️ 清空历史')
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setObjectName('danger')
        self.clear_btn.clicked.connect(self.clear_history)
        left_layout.addWidget(self.clear_btn)
        
        layout.addWidget(left_buttons)
        
        layout.addStretch()
        
        # 关闭按钮
        self.close_btn = QPushButton('✕ 关闭')
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setObjectName('secondary')
        self.close_btn.setFixedWidth(100)
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)
        
        return bottom
    
    def load_history(self):
        """从数据库加载历史记录"""
        try:
            history = self.db.get_user_history(self.user_id)
            self.all_history = history
            
            self.update_table(history)
            self.update_stat_cards(history)
            
            # 更新统计标签
            self.stats_label.setText(f'共 {len(history)} 条记录')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载历史记录失败：{str(e)}')
    
    def update_stat_cards(self, history):
        """更新统计卡片数值"""
        total_records = len(history)
        total_targets = sum(record['total'] for record in history)
        avg_targets = round(total_targets / total_records, 1) if total_records > 0 else 0
        
        # 找到统计卡片容器并更新
        cards_widget = self.findChild(QWidget, "")  # 简化处理，实际可通过对象名查找
        # 为简化，这里不实现动态更新，仅作为示意
    
    def update_table(self, history):
        """更新表格显示"""
        self.table.setRowCount(len(history))
        
        for i, record in enumerate(history):
            # ID列
            id_item = QTableWidgetItem(str(record['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setForeground(QBrush(QColor(100, 116, 139)))
            self.table.setItem(i, 0, id_item)
            
            # 图片名称列
            name_item = QTableWidgetItem(record['image_name'])
            name_item.setForeground(QBrush(QColor(30, 41, 59)))
            name_item.setFont(QFont('Microsoft YaHei', 10, QFont.Medium))
            self.table.setItem(i, 1, name_item)
            
            # 检测时间列
            time_str = str(record['time'])[:19]
            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setForeground(QBrush(QColor(71, 85, 105)))
            self.table.setItem(i, 2, time_item)
            
            # 目标数量列
            count = record['total']
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignCenter)
            
            # 根据数量设置颜色和徽章样式
            if count > 10:
                color = '#10b981'
                bg_color = '#d1fae5'
            elif count > 5:
                color = '#f59e0b'
                bg_color = '#fed7aa'
            elif count > 0:
                color = '#3b82f6'
                bg_color = '#dbeafe'
            else:
                color = '#94a3b8'
                bg_color = '#f1f5f9'
            
            count_item.setForeground(QBrush(QColor(color)))
            count_item.setBackground(QBrush(QColor(bg_color)))
            count_item.setTextAlignment(Qt.AlignCenter)
            
            self.table.setItem(i, 3, count_item)
            
            # 操作列 - 使用现代风格的按钮
            view_btn = QPushButton('查看详情')
            view_btn.setCursor(Qt.PointingHandCursor)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            view_btn.clicked.connect(lambda checked, r=record: self.show_detail(r))
            
            # 将按钮放入容器以实现居中对齐
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(view_btn)
            
            self.table.setCellWidget(i, 4, btn_container)
    
    def filter_history(self):
        """根据搜索框文本过滤历史记录"""
        search_text = self.search_box.text().lower().strip()
        
        if not search_text:
            self.update_table(self.all_history)
            self.stats_label.setText(f'共 {len(self.all_history)} 条记录')
            return
        
        filtered = [
            r for r in self.all_history 
            if search_text in r['image_name'].lower()
        ]
        
        self.update_table(filtered)
        self.stats_label.setText(f'找到 {len(filtered)} 条记录')
    
    def show_detail(self, record):
        """显示检测详情对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle('📋 检测详情')
        dialog.setFixedSize(550, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 20px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #f8fafc;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #1e293b;
            }
            QLabel {
                color: #334155;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # 基本信息卡片
        info_group = QGroupBox('基本信息')
        info_layout = QFormLayout()
        info_layout.setSpacing(10)
        info_layout.setLabelAlignment(Qt.AlignRight)
        
        # 添加样式化的信息行
        labels = [
            ('📷 图片名称', record['image_name']),
            ('⏰ 检测时间', str(record['time'])[:19]),
            ('🎯 目标总数', str(record['total']))
        ]
        
        for label, value in labels:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: 600; color: #475569;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #0f172a; background-color: white; padding: 8px 12px; border-radius: 8px; border: 1px solid #e2e8f0;")
            info_layout.addRow(label_widget, value_widget)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 检测结果表格
        result_group = QGroupBox('检测结果')
        result_layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['序号', '昆虫类别', '置信度'])
        table.horizontalHeader().setStretchLastSection(False)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        results = record['results']
        table.setRowCount(len(results))
        table.setColumnWidth(0, 60)
        table.setColumnWidth(1, 200)
        table.setColumnWidth(2, 150)
        
        for i, det in enumerate(results):
            # 序号
            seq_item = QTableWidgetItem(str(i+1))
            seq_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 0, seq_item)
            
            # 类别
            class_item = QTableWidgetItem(det['class_name'])
            class_item.setForeground(QBrush(QColor(30, 41, 59)))
            class_item.setFont(QFont('Microsoft YaHei', 10))
            table.setItem(i, 1, class_item)
            
            # 置信度 - 添加进度条效果
            confidence = det['confidence']
            conf_item = QTableWidgetItem(f"{confidence:.2%}")
            conf_item.setTextAlignment(Qt.AlignCenter)
            
            # 根据置信度设置颜色
            if confidence >= 0.8:
                color = '#10b981'
            elif confidence >= 0.5:
                color = '#f59e0b'
            else:
                color = '#ef4444'
            
            conf_item.setForeground(QBrush(QColor(color)))
            conf_item.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
            table.setItem(i, 2, conf_item)
        
        result_layout.addWidget(table)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group, 1)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton('关 闭')
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedSize(120, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def export_history(self):
        """导出历史记录到CSV文件"""
        if not self.all_history:
            QMessageBox.warning(self, '提示', '没有可导出的历史记录')
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, '导出历史记录', 
            f'detection_history_{QDate.currentDate().toString("yyyyMMdd")}.csv', 
            'CSV文件 (*.csv)'
        )
        
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', '图片名称', '检测时间', '目标数量', '检测结果详情'])
                    
                    for record in self.all_history:
                        results_str = '；'.join([
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
                    self, '导出成功', 
                    f'✅ 已成功导出 {len(self.all_history)} 条记录\n📁 保存位置：{path}'
                )
            except Exception as e:
                QMessageBox.critical(self, '导出失败', f'❌ 导出过程中出现错误：\n{str(e)}')
    
    def clear_history(self):
        """清空历史记录"""
        if not self.all_history:
            QMessageBox.warning(self, '提示', '历史记录已为空')
            return
        
        # 创建自定义确认对话框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('确认清空')
        msg_box.setText('⚠️ 确定要清空所有历史记录吗？')
        msg_box.setInformativeText('此操作将永久删除所有记录，且不可恢复。')
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # 设置按钮样式
        yes_btn = msg_box.button(QMessageBox.Yes)
        yes_btn.setText('是的，清空')
        yes_btn.setStyleSheet("background-color: #ef4444;")
        
        no_btn = msg_box.button(QMessageBox.No)
        no_btn.setText('取消')
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            # 这里需要数据库支持删除操作
            QMessageBox.information(self, '提示', '清空功能开发中...\n即将支持永久删除记录')