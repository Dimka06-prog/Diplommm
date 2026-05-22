from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QMessageBox, QDateEdit, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font
from datetime import date
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class ReportsPage(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        title = QLabel("Отчеты")
        title.setFont(get_header_font(28))
        title.setStyleSheet("color: #1C1B17;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Report type selector
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Тип отчета:"))
        self.report_combo = QComboBox()
        self.report_combo.addItems(["Пробег по ТС", "Штрафы за период", "ТО по водителям"])
        self.report_combo.currentIndexChanged.connect(self.generate_report)
        filter_layout.addWidget(self.report_combo)
        filter_layout.addStretch()
        
        generate_btn = QPushButton("Сформировать")
        generate_btn.setObjectName("primary_btn")
        generate_btn.clicked.connect(self.generate_report)
        filter_layout.addWidget(generate_btn)
        layout.addLayout(filter_layout)
        
        # Results table with increased size
        self.table = QTableWidget()
        self.table.setMinimumHeight(300)
        self.table.setStyleSheet("QTableWidget { background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E2E0; }")
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Charts section
        self.charts_frame = QFrame()
        self.charts_frame.setObjectName("card_light")
        charts_layout = QVBoxLayout(self.charts_frame)
        charts_layout.setContentsMargins(30, 30, 30, 30)
        charts_layout.setSpacing(20)

        charts_title = QLabel("Графики")
        charts_title.setFont(get_header_font(18))
        charts_title.setStyleSheet("color: #1C1B17;")
        charts_layout.addWidget(charts_title)

        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        charts_layout.addWidget(self.canvas)

        layout.addWidget(self.charts_frame)
        
    def generate_report(self):
        report_type = self.report_combo.currentText()
        
        try:
            if report_type == "Пробег по ТС":
                query = """SELECT t.gos_nomer, t.probeg, m.nazvanie as marka_name, mo.nazvanie as model_name
                           FROM transportnoe_sredstvo t
                           LEFT JOIN model mo ON t.model_id = mo.id
                           LEFT JOIN marka m ON mo.marka_id = m.id
                           ORDER BY t.probeg DESC"""
                results = Database.execute_query(query)
                self.table.setColumnCount(4)
                self.table.setHorizontalHeaderLabels(["Гос. номер", "Пробег (км)", "Марка", "Модель"])
                self.table.setRowCount(len(results))
                
                for row, r in enumerate(results):
                    self.table.setItem(row, 0, QTableWidgetItem(r['gos_nomer']))
                    self.table.setItem(row, 1, QTableWidgetItem(str(r['probeg'])))
                    self.table.setItem(row, 2, QTableWidgetItem(r.get('marka_name', '-')))
                    self.table.setItem(row, 3, QTableWidgetItem(r.get('model_name', '-')))
                    
            elif report_type == "Штрафы за период":
                query = """SELECT f.date, t.gos_nomer, f.amount, f.status
                           FROM fines f
                           LEFT JOIN transportnoe_sredstvo t ON f.ts_id = t.id
                           ORDER BY f.date DESC"""
                results = Database.execute_query(query)
                self.table.setColumnCount(4)
                self.table.setHorizontalHeaderLabels(["Дата", "ТС", "Сумма (руб)", "Статус"])
                self.table.setRowCount(len(results))
                
                for row, r in enumerate(results):
                    self.table.setItem(row, 0, QTableWidgetItem(str(r['date'])))
                    self.table.setItem(row, 1, QTableWidgetItem(r.get('gos_nomer', '-')))
                    self.table.setItem(row, 2, QTableWidgetItem(str(r['amount'])))
                    self.table.setItem(row, 3, QTableWidgetItem(r['status']))
                    
            elif report_type == "ТО по водителям":
                query = """SELECT s.fio, COUNT(t.id) as ts_count
                           FROM sotrudnik s
                           LEFT JOIN transportnoe_sredstvo t ON s.id = t.assigned_driver_id
                           WHERE s.rol_id = 2
                           GROUP BY s.id, s.fio"""
                results = Database.execute_query(query)
                self.table.setColumnCount(2)
                self.table.setHorizontalHeaderLabels(["Водитель", "Кол-во ТС"])
                self.table.setRowCount(len(results))
                
                for row, r in enumerate(results):
                    self.table.setItem(row, 0, QTableWidgetItem(r['fio']))
                    self.table.setItem(row, 1, QTableWidgetItem(str(r['ts_count'])))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации отчета: {str(e)}")

        # Update charts
        self.update_charts(report_type, results)

    def update_charts(self, report_type, data):
        """Обновление графиков на странице отчетов"""
        try:
            self.figure.clear()

            if report_type == "Пробег по ТС" and data:
                ax = self.figure.add_subplot(111)
                vehicles = [f"{d['gos_nomer']}" for d in data[:10]]  # Top 10
                mileage = [d['probeg'] for d in data[:10]]

                ax.bar(vehicles, mileage, color='#4A7C59')
                ax.set_xlabel('Гос. номер ТС')
                ax.set_ylabel('Пробег (км)')
                ax.set_title('Топ 10 ТС по пробегу', fontsize=12, fontweight='bold')
                ax.tick_params(axis='x', rotation=45)
                self.figure.tight_layout()

            elif report_type == "Штрафы за период" and data:
                ax = self.figure.add_subplot(111)
                dates = [str(d['date']) for d in data[:10]]
                amounts = [d['amount'] for d in data[:10]]

                ax.plot(dates, amounts, marker='o', color='#e5a00d', linewidth=2)
                ax.set_xlabel('Дата')
                ax.set_ylabel('Сумма (руб)')
                ax.set_title('Штрафы за период (последние 10)', fontsize=12, fontweight='bold')
                ax.tick_params(axis='x', rotation=45)
                self.figure.tight_layout()

            elif report_type == "ТО по водителям" and data:
                ax = self.figure.add_subplot(111)
                drivers = [d['fio'] for d in data[:10]]
                ts_count = [d['ts_count'] for d in data[:10]]

                ax.bar(drivers, ts_count, color='#3F3D38')
                ax.set_xlabel('Водитель')
                ax.set_ylabel('Кол-во ТС')
                ax.set_title('ТО по водителям (топ 10)', fontsize=12, fontweight='bold')
                ax.tick_params(axis='x', rotation=45)
                self.figure.tight_layout()

            self.canvas.draw()
        except Exception as e:
            print(f"Ошибка обновления графиков: {e}")

