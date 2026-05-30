from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QLineEdit, QComboBox,
                             QMessageBox, QDateEdit, QMenu)
from PyQt6.QtCore import Qt
from src.database import Database
from src.styles import get_header_font, get_font
from src.permissions import has_permission, PERMISSION_ADD_MAINTENANCE, PERMISSION_EDIT_MAINTENANCE, PERMISSION_DELETE_MAINTENANCE
from datetime import date
from src.api.gibdd_api import NotificationSystem

class MaintenancePage(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        # Don't call refresh_data here - it will be called when page is shown
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        title = QLabel("ТО и Страховка")
        title.setFont(get_header_font(28))
        title.setStyleSheet("color: #1C1B17;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        if has_permission(self.user_data['rol_id'], PERMISSION_ADD_MAINTENANCE):
            add_btn = QPushButton("+ Добавить запись")
            add_btn.setObjectName("primary_btn")
            add_btn.clicked.connect(self.open_add_maintenance_dialog)
            header_layout.addWidget(add_btn)
        
        check_btn = QPushButton("Проверить напоминания")
        check_btn.setObjectName("secondary_btn")
        check_btn.clicked.connect(self.check_notifications)
        header_layout.addWidget(check_btn)
        layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите гос. номер или статус...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ТС", "Дата ТО", "Тип", "Результат", "Следующее ТО", "Страховка до", "Статус"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
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
        layout.addWidget(self.table)
        
    def refresh_data(self):
        try:
            query = """SELECT ts.id, ts.gos_nomer, ts.insurance_expiry, ts.to_expiry, ts.tekuschee_sostoyanie
                       FROM transportnoe_sredstvo ts
                       ORDER BY ts.gos_nomer"""
            vehicles = Database.execute_query(query)
            self.vehicles_data = vehicles  # Store for filtering
            self.table.setRowCount(len(vehicles))
            
            for row, veh in enumerate(vehicles):
                self.table.setItem(row, 0, QTableWidgetItem(veh.get('gos_nomer') or '-'))
                self.table.setItem(row, 1, QTableWidgetItem(str(veh.get('to_expiry') or '-')))
                self.table.setItem(row, 2, QTableWidgetItem("ТО-1"))
                self.table.setItem(row, 3, QTableWidgetItem("Пройден"))
                self.table.setItem(row, 4, QTableWidgetItem("-"))
                self.table.setItem(row, 5, QTableWidgetItem(str(veh.get('insurance_expiry') or '-')))
                
                status = "OK"
                insurance_expiry = veh.get('insurance_expiry')
                if insurance_expiry and insurance_expiry < date.today():
                    status = "Истекла"
                self.table.setItem(row, 6, QTableWidgetItem(status))
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, veh.get('id'))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def filter_table(self, search_text):
        """Фильтрация таблицы по поисковому запросу"""
        if not hasattr(self, 'vehicles_data'):
            return

        search_text = search_text.lower()
        filtered_vehicles = []

        for veh in self.vehicles_data:
            gos_nomer = (veh.get('gos_nomer') or '').lower()
            status = "OK"
            insurance_expiry = veh.get('insurance_expiry')
            if insurance_expiry and insurance_expiry < date.today():
                status = "Истекла"
            status = status.lower()

            if search_text in gos_nomer or search_text in status:
                filtered_vehicles.append(veh)

        self.table.setRowCount(len(filtered_vehicles))

        for row, veh in enumerate(filtered_vehicles):
            self.table.setItem(row, 0, QTableWidgetItem(veh.get('gos_nomer') or '-'))
            self.table.setItem(row, 1, QTableWidgetItem(str(veh.get('to_expiry') or '-')))
            self.table.setItem(row, 2, QTableWidgetItem("ТО-1"))
            self.table.setItem(row, 3, QTableWidgetItem("Пройден"))
            self.table.setItem(row, 4, QTableWidgetItem("-"))
            self.table.setItem(row, 5, QTableWidgetItem(str(veh.get('insurance_expiry') or '-')))
            
            status = "OK"
            insurance_expiry = veh.get('insurance_expiry')
            if insurance_expiry and insurance_expiry < date.today():
                status = "Истекла"
            self.table.setItem(row, 6, QTableWidgetItem(status))
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, veh.get('id'))
            
    def open_add_maintenance_dialog(self):
        dialog = MaintenanceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            
    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item:
            return

        # Check permissions
        if not has_permission(self.user_data['rol_id'], PERMISSION_EDIT_MAINTENANCE):
            return

        maintenance_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu()
        if has_permission(self.user_data['rol_id'], PERMISSION_EDIT_MAINTENANCE):
            edit_action = menu.addAction("Редактировать")
        if has_permission(self.user_data['rol_id'], PERMISSION_DELETE_MAINTENANCE):
            delete_action = menu.addAction("Удалить")

        action = menu.exec(self.table.mapToGlobal(position))

        if action == edit_action:
            self.edit_maintenance(maintenance_id)
        elif action == delete_action:
            self.delete_maintenance(maintenance_id)
            
    def check_notifications(self):
        try:
            maintenance_due = NotificationSystem.check_maintenance_due(Database, 30)
            insurance_due = NotificationSystem.check_insurance_due(Database, 30)
            
            message = "Напоминания:\n\n"
            
            if maintenance_due:
                message += f"Требуется ТО ({len(maintenance_due)} ТС):\n"
                for veh in maintenance_due:
                    gos = veh.get('gos_nomer') or 'Неизвестно'
                    expiry = veh.get('to_expiry') or '-'
                    message += f"- {gos}: до {expiry}\n"
                message += "\n"
            else:
                message += "ТО в порядке\n\n"

            if insurance_due:
                message += f"Истекает страховка ({len(insurance_due)} ТС):\n"
                for veh in insurance_due:
                    gos = veh.get('gos_nomer') or 'Неизвестно'
                    expiry = veh.get('insurance_expiry') or '-'
                    message += f"- {gos}: до {expiry}\n"
            else:
                message += "Страховка в порядке"
            
            QMessageBox.information(self, "Напоминания", message)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка проверки: {str(e)}")

class MaintenanceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Обновить ТО/Страховку")
        self.setFixedSize(450, 300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)
        
        form_layout = QFormLayout()
        self.ts_combo = QComboBox()
        self.to_date = QDateEdit()
        self.to_date.setDate(date.today())
        self.insurance_date = QDateEdit()
        self.insurance_date.setDate(date.today())
        
        try:
            vehicles = Database.execute_query("SELECT id, gos_nomer FROM transportnoe_sredstvo")
            for veh in vehicles:
                self.ts_combo.addItem(veh['gos_nomer'], veh['id'])
        except Exception as e:
            print(f"Ошибка загрузки ТС: {e}")
        
        form_layout.addRow("ТС:", self.ts_combo)
        form_layout.addRow("Дата следующего ТО:", self.to_date)
        form_layout.addRow("Страховка до:", self.insurance_date)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.save_maintenance)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
    def save_maintenance(self):
        try:
            query = """UPDATE transportnoe_sredstvo SET to_expiry = %s, insurance_expiry = %s WHERE id = %s"""
            Database.execute_query(query, (
                self.to_date.date().toString("yyyy-MM-dd"),
                self.insurance_date.date().toString("yyyy-MM-dd"),
                self.ts_combo.currentData()
            ), fetch=False)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
