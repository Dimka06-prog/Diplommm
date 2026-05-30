from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QMessageBox, QDateEdit, QFrame, QLineEdit, QSizePolicy)
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
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Фильтр результатов...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Results table with fixed max height to leave room for chart
        self.table = QTableWidget()
        self.table.setMinimumHeight(200)
        self.table.setMaximumHeight(300)
        self.table.setStyleSheet("""
            QTableWidget {
                background: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E2E2E0;
                gridline-color: #EFEFEE;
            }
            QTableWidget::item {
                padding: 8px 12px;
            }
            QHeaderView::section {
                background: #F7F7F7;
                color: #3F3D38;
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid #E2E2E0;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, 0)

        # Charts section with explicit minimum size
        self.charts_frame = QFrame()
        self.charts_frame.setObjectName("card_light")
        self.charts_frame.setMinimumHeight(450)
        charts_layout = QVBoxLayout(self.charts_frame)
        charts_layout.setContentsMargins(30, 30, 30, 30)
        charts_layout.setSpacing(20)

        charts_title = QLabel("Графики")
        charts_title.setFont(get_header_font(18))
        charts_title.setStyleSheet("color: #1C1B17;")
        charts_layout.addWidget(charts_title)

        # Create matplotlib figure with larger size
        self.figure = Figure(figsize=(12, 7), dpi=100, facecolor='#FBF8F3')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.setMinimumHeight(400)
        charts_layout.addWidget(self.canvas)

        layout.addWidget(self.charts_frame, 1)
        
    def generate_report(self):
        report_type = self.report_combo.currentText()
        results = []
        
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
                    self.table.setItem(row, 0, QTableWidgetItem(r.get('gos_nomer') or '-'))
                    self.table.setItem(row, 1, QTableWidgetItem(str(r.get('probeg') or 0)))
                    self.table.setItem(row, 2, QTableWidgetItem(r.get('marka_name') or '-'))
                    self.table.setItem(row, 3, QTableWidgetItem(r.get('model_name') or '-'))

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
                    self.table.setItem(row, 0, QTableWidgetItem(str(r.get('date') or '-')))
                    self.table.setItem(row, 1, QTableWidgetItem(r.get('gos_nomer') or '-'))
                    self.table.setItem(row, 2, QTableWidgetItem(str(r.get('amount') or 0)))
                    self.table.setItem(row, 3, QTableWidgetItem(r.get('status') or '-'))

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
                    self.table.setItem(row, 0, QTableWidgetItem(r.get('fio') or '-'))
                    self.table.setItem(row, 1, QTableWidgetItem(str(r.get('ts_count') or 0)))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации отчета: {str(e)}")

        # Update charts
        self.report_results = results  # Store for filtering
        self.current_report_type = report_type
        self.update_charts(report_type, results)

    def filter_table(self, search_text):
        """Фильтрация результатов отчета"""
        if not hasattr(self, 'report_results') or not self.report_results:
            return

        search_text = search_text.lower()
        filtered_results = []

        for r in self.report_results:
            # Check all values in the row
            row_text = ' '.join(str(v or '').lower() for v in r.values())
            if search_text in row_text:
                filtered_results.append(r)

        self.table.setRowCount(len(filtered_results))
        report_type = getattr(self, 'current_report_type', '')

        if report_type == "Пробег по ТС":
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Гос. номер", "Пробег (км)", "Марка", "Модель"])
            for row, r in enumerate(filtered_results):
                self.table.setItem(row, 0, QTableWidgetItem(r.get('gos_nomer') or '-'))
                self.table.setItem(row, 1, QTableWidgetItem(str(r.get('probeg') or 0)))
                self.table.setItem(row, 2, QTableWidgetItem(r.get('marka_name') or '-'))
                self.table.setItem(row, 3, QTableWidgetItem(r.get('model_name') or '-'))
        elif report_type == "Штрафы за период":
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Дата", "ТС", "Сумма (руб)", "Статус"])
            for row, r in enumerate(filtered_results):
                self.table.setItem(row, 0, QTableWidgetItem(str(r.get('date') or '-')))
                self.table.setItem(row, 1, QTableWidgetItem(r.get('gos_nomer') or '-'))
                self.table.setItem(row, 2, QTableWidgetItem(str(r.get('amount') or 0)))
                self.table.setItem(row, 3, QTableWidgetItem(r.get('status') or '-'))
        elif report_type == "ТО по водителям":
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["Водитель", "Кол-во ТС"])
            for row, r in enumerate(filtered_results):
                self.table.setItem(row, 0, QTableWidgetItem(r.get('fio') or '-'))
                self.table.setItem(row, 1, QTableWidgetItem(str(r.get('ts_count') or 0)))

    def update_charts(self, report_type, data):
        """Обновление графиков на странице отчетов"""
        try:
            self.figure.clear()

            if not data:
                ax = self.figure.add_subplot(111)
                ax.set_facecolor('#FBF8F3')
                ax.text(0.5, 0.5, 'Нет данных для отображения', ha='center', va='center',
                       fontsize=14, color='#6F6D38', transform=ax.transAxes)
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
                self.canvas.draw()
                return

            if report_type == "Пробег по ТС":
                ax = self.figure.add_subplot(111)
                ax.set_facecolor('#FBF8F3')
                for spine in ax.spines.values():
                    spine.set_color('#E2E2E0')
                ax.tick_params(colors='#3F3D38')
                ax.title.set_color('#1C1B17')
                vehicles = [f"{d.get('gos_nomer') or '-'}" for d in data[:10]]
                mileage = [d.get('probeg') or 0 for d in data[:10]]

                bars = ax.bar(vehicles, mileage, color='#4A7C59')
                ax.set_xlabel('Гос. номер ТС', fontsize=11, color='#3F3D38')
                ax.set_ylabel('Пробег (км)', fontsize=11, color='#3F3D38')
                ax.set_title('Топ 10 ТС по пробегу', fontsize=13, fontweight='bold', color='#1C1B17', pad=15)
                ax.tick_params(axis='x', rotation=30, labelsize=9)
                ax.tick_params(axis='y', labelsize=9)
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}', ha='center', va='bottom', fontsize=8, color='#1C1B17')
                self.figure.subplots_adjust(bottom=0.2, left=0.1, right=0.95, top=0.9)

            elif report_type == "Штрафы за период":
                ax = self.figure.add_subplot(111)
                ax.set_facecolor('#FBF8F3')
                for spine in ax.spines.values():
                    spine.set_color('#E2E2E0')
                ax.tick_params(colors='#3F3D38')
                ax.title.set_color('#1C1B17')
                dates = [str(d.get('date') or '-') for d in data[:10]]
                amounts = [d.get('amount') or 0 for d in data[:10]]

                ax.plot(dates, amounts, marker='o', color='#e5a00d', linewidth=2.5, markersize=6)
                ax.set_xlabel('Дата', fontsize=11, color='#3F3D38')
                ax.set_ylabel('Сумма (руб)', fontsize=11, color='#3F3D38')
                ax.set_title('Штрафы за период (последние 10)', fontsize=13, fontweight='bold', color='#1C1B17', pad=15)
                ax.tick_params(axis='x', rotation=30, labelsize=9)
                ax.tick_params(axis='y', labelsize=9)
                ax.grid(True, alpha=0.3, color='#E2E2E0')
                self.figure.subplots_adjust(bottom=0.2, left=0.1, right=0.95, top=0.9)

            elif report_type == "ТО по водителям":
                ax = self.figure.add_subplot(111)
                ax.set_facecolor('#FBF8F3')
                for spine in ax.spines.values():
                    spine.set_color('#E2E2E0')
                ax.tick_params(colors='#3F3D38')
                ax.title.set_color('#1C1B17')
                drivers = [d.get('fio') or '-' for d in data[:10]]
                ts_count = [d.get('ts_count') or 0 for d in data[:10]]

                bars = ax.bar(drivers, ts_count, color='#3F3D38')
                ax.set_xlabel('Водитель', fontsize=11, color='#3F3D38')
                ax.set_ylabel('Кол-во ТС', fontsize=11, color='#3F3D38')
                ax.set_title('ТО по водителям (топ 10)', fontsize=13, fontweight='bold', color='#1C1B17', pad=15)
                ax.tick_params(axis='x', rotation=30, labelsize=9)
                ax.tick_params(axis='y', labelsize=9)
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{int(height)}', ha='center', va='bottom', fontsize=8, color='#1C1B17')
                self.figure.subplots_adjust(bottom=0.2, left=0.1, right=0.95, top=0.9)

            self.canvas.draw()
        except Exception as e:
            print(f"Ошибка обновления графиков: {e}")

    def refresh_data(self):
        """Вызывается при открытии страницы"""
        self.generate_report()
