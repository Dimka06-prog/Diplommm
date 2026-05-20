from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QMessageBox, QDateEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font
from datetime import date

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
        
        # Results table
        self.table = QTableWidget()
        self.table.setStyleSheet("QTableWidget { background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E2E0; }")
        layout.addWidget(self.table)
        
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
