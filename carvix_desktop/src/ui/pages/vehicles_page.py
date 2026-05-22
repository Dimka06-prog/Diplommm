from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QLineEdit, QFormLayout, QComboBox,
                             QMessageBox, QDateEdit, QSpinBox, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font
from src.permissions import has_permission, PERMISSION_ADD_VEHICLE, PERMISSION_EDIT_VEHICLE, PERMISSION_DELETE_VEHICLE
from src.validation import Validator, ValidationError

class VehiclesPage(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        title = QLabel("Транспортные средства")
        title.setFont(get_header_font(28))
        title.setStyleSheet("color: #1C1B17;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        if has_permission(self.user_data['rol_id'], PERMISSION_ADD_VEHICLE):
            add_btn = QPushButton("+ Добавить ТС")
            add_btn.setObjectName("primary_btn")
            add_btn.clicked.connect(self.open_add_vehicle_dialog)
            header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите гос. номер или VIN...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Гос. номер", "Инв. номер", "Марка", "Модель", "VIN", "Пробег", "Состояние", "Водитель"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        
        self.table.setStyleSheet("""
            QTableWidget { background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E2E0; }
            QTableWidget::item { padding: 8px 12px; }
            QHeaderView::section { background: #F7F7F7; color: #3F3D38; padding: 10px 12px; font-weight: 600; font-size: 13px; }
        """)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)
        
    def refresh_data(self):
        try:
            query = """SELECT t.id, t.gos_nomer, t.invent_nomer, t.probeg, t.vin,
                       t.tekuschee_sostoyanie, m.nazvanie as marka_name,
                       mo.nazvanie as model_name, s.fio as driver_fio
                       FROM transportnoe_sredstvo t
                       LEFT JOIN model mo ON t.model_id = mo.id
                       LEFT JOIN marka m ON mo.marka_id = m.id
                       LEFT JOIN sotrudnik s ON t.assigned_driver_id = s.id
                       ORDER BY t.gos_nomer"""
            vehicles = Database.execute_query(query)
            self.vehicles_data = vehicles  # Store for filtering
            self.table.setRowCount(len(vehicles))

            for row, veh in enumerate(vehicles):
                self.table.setItem(row, 0, QTableWidgetItem(veh['gos_nomer']))
                self.table.setItem(row, 1, QTableWidgetItem(veh['invent_nomer']))
                self.table.setItem(row, 2, QTableWidgetItem(veh.get('marka_name', '-')))
                self.table.setItem(row, 3, QTableWidgetItem(veh.get('model_name', '-')))
                self.table.setItem(row, 4, QTableWidgetItem(veh['vin']))
                self.table.setItem(row, 5, QTableWidgetItem(str(veh['probeg'])))
                self.table.setItem(row, 6, QTableWidgetItem(veh['tekuschee_sostoyanie']))
                self.table.setItem(row, 7, QTableWidgetItem(veh.get('driver_fio', '-')))
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, veh['id'])
        except Exception as e:
            pass

    def filter_table(self, search_text):
        """Фильтрация таблицы по поисковому запросу"""
        if not hasattr(self, 'vehicles_data'):
            return

        search_text = search_text.lower()
        filtered_vehicles = []

        for veh in self.vehicles_data:
            gos_nomer = veh['gos_nomer'].lower()
            vin = veh['vin'].lower()
            invent_nomer = veh['invent_nomer'].lower()
            marka = veh.get('marka_name', '').lower()

            if search_text in gos_nomer or search_text in vin or search_text in invent_nomer or search_text in marka:
                filtered_vehicles.append(veh)

        self.table.setRowCount(len(filtered_vehicles))

        for row, veh in enumerate(filtered_vehicles):
            self.table.setItem(row, 0, QTableWidgetItem(veh['gos_nomer']))
            self.table.setItem(row, 1, QTableWidgetItem(veh['invent_nomer']))
            self.table.setItem(row, 2, QTableWidgetItem(veh.get('marka_name', '-')))
            self.table.setItem(row, 3, QTableWidgetItem(veh.get('model_name', '-')))
            self.table.setItem(row, 4, QTableWidgetItem(veh['vin']))
            self.table.setItem(row, 5, QTableWidgetItem(str(veh['probeg'])))
            self.table.setItem(row, 6, QTableWidgetItem(veh['tekuschee_sostoyanie']))
            self.table.setItem(row, 7, QTableWidgetItem(veh.get('driver_fio', '-')))
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, veh['id'])

    def open_add_vehicle_dialog(self):
        dialog = VehicleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            
    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item:
            return

        # Check permissions
        if not has_permission(self.user_data['rol_id'], PERMISSION_EDIT_VEHICLE):
            return

        vehicle_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu()
        if has_permission(self.user_data['rol_id'], PERMISSION_EDIT_VEHICLE):
            edit_action = menu.addAction("✏️ Редактировать")
        if has_permission(self.user_data['rol_id'], PERMISSION_DELETE_VEHICLE):
            delete_action = menu.addAction("🗑️ Удалить")

        action = menu.exec(self.table.mapToGlobal(position))

        if action == edit_action:
            self.edit_vehicle(vehicle_id)
        elif action == delete_action:
            self.delete_vehicle(vehicle_id)
            
    def edit_vehicle(self, vehicle_id):
        try:
            query = "SELECT * FROM transportnoe_sredstvo WHERE id = %s"
            result = Database.execute_query(query, (vehicle_id,))
            if result:
                dialog = VehicleDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")
            
    def delete_vehicle(self, vehicle_id):
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить это ТС?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                Database.execute_query("DELETE FROM transportnoe_sredstvo WHERE id = %s", (vehicle_id,), fetch=False)
                self.refresh_data()
                QMessageBox.information(self, "Успех", "ТС удалено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")

class VehicleDialog(QDialog):
    def __init__(self, parent=None, vehicle_data=None):
        super().__init__(parent)
        self.vehicle_data = vehicle_data
        self.edit_mode = vehicle_data is not None
        self.init_ui()
        
        if self.edit_mode:
            self.populate_fields()
            
    def populate_fields(self):
        if not self.vehicle_data:
            return
            
        self.gos_nomer_input.setText(self.vehicle_data.get('gos_nomer', ''))
        self.invent_nomer_input.setText(self.vehicle_data.get('invent_nomer', ''))
        self.vin_input.setText(self.vehicle_data.get('vin', ''))
        self.probeg_input.setValue(self.vehicle_data.get('probeg', 0))
        
        marka_id = self.vehicle_data.get('model_id', 1)
        for i in range(self.marka_combo.count()):
            if self.marka_combo.itemData(i) == marka_id:
                self.marka_combo.setCurrentIndex(i)
                break
                
        dept_id = self.vehicle_data.get('podrazdelenie_id')
        for i in range(self.dept_combo.count()):
            if self.dept_combo.itemData(i) == dept_id:
                self.dept_combo.setCurrentIndex(i)
                break
                
        driver_id = self.vehicle_data.get('assigned_driver_id')
        for i in range(self.driver_combo.count()):
            if self.driver_combo.itemData(i) == driver_id:
                self.driver_combo.setCurrentIndex(i)
                break
                
        status = self.vehicle_data.get('tekuschee_sostoyanie', 'Активное')
        for i in range(self.status_combo.count()):
            if self.status_combo.itemData(i) == status:
                self.status_combo.setCurrentIndex(i)
                break
        
    def init_ui(self):
        self.setWindowTitle("Редактировать ТС" if self.edit_mode else "Добавить транспортное средство")
        self.setFixedSize(600, 500)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        form_layout = QFormLayout()
        self.gos_nomer_input = QLineEdit()
        self.invent_nomer_input = QLineEdit()
        self.vin_input = QLineEdit()
        self.probeg_input = QSpinBox()
        self.probeg_input.setRange(0, 10000000)
        self.marka_combo = QComboBox()
        self.marka_combo.setMinimumWidth(300)
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(300)
        self.dept_combo = QComboBox()
        self.dept_combo.setMinimumWidth(300)
        self.driver_combo = QComboBox()
        self.driver_combo.setMinimumWidth(300)
        self.status_combo = QComboBox()
        self.status_combo.setMinimumWidth(300)
        
        try:
            markas = Database.execute_query("SELECT id, nazvanie FROM marka")
            for marka in markas:
                self.marka_combo.addItem(marka['nazvanie'], marka['id'])
        except: self.marka_combo.addItem("Toyota", 1)
        
        try:
            depts = Database.execute_query("SELECT id, nazvanie FROM podrazdelenie")
            for dept in depts:
                self.dept_combo.addItem(dept['nazvanie'], dept['id'])
        except: self.dept_combo.addItem("Основное", 1)
        
        self.driver_combo.addItem("Не назначен", None)
        try:
            drivers = Database.execute_query("SELECT id, fio FROM sotrudnik WHERE rol_id = 2")
            for driver in drivers:
                self.driver_combo.addItem(driver['fio'], driver['id'])
        except: pass
        
        self.status_combo.addItem("Активное", "Активное")
        self.status_combo.addItem("В ремонте", "В ремонте")
        
        form_layout.addRow("Гос. номер:", self.gos_nomer_input)
        form_layout.addRow("Инв. номер:", self.invent_nomer_input)
        form_layout.addRow("VIN:", self.vin_input)
        form_layout.addRow("Пробег:", self.probeg_input)
        form_layout.addRow("Марка:", self.marka_combo)
        form_layout.addRow("Подразделение:", self.dept_combo)
        form_layout.addRow("Водитель:", self.driver_combo)
        form_layout.addRow("Состояние:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.save_vehicle)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
    def save_vehicle(self):
        try:
            gos_nomer = self.gos_nomer_input.text().strip()
            invent_nomer = self.invent_nomer_input.text().strip()
            vin = self.vin_input.text().strip()
            probeg = self.probeg_input.value()
            model_id = self.model_combo.currentData()
            podrazdelenie_id = self.dept_combo.currentData()
            driver_id = self.driver_combo.currentData()
            status = self.status_combo.currentData()

            # Валидация
            try:
                Validator.validate_gos_nomer(gos_nomer)
                Validator.validate_vin(vin)
                Validator.validate_probeg(probeg)
            except ValidationError as e:
                QMessageBox.warning(self, "Ошибка валидации", str(e))
                return

            if self.edit_mode:
                query = """UPDATE transportnoe_sredstvo SET gos_nomer = %s, invent_nomer = %s, vin = %s,
                          probeg = %s, model_id = %s, podrazdelenie_id = %s, assigned_driver_id = %s,
                          tekuschee_sostoyanie = %s WHERE id = %s"""
                Database.execute_query(query, (gos_nomer, invent_nomer, vin, probeg, model_id,
                                               podrazdelenie_id, driver_id, status, self.vehicle_data['id']), fetch=False)
                QMessageBox.information(self, "Успех", "ТС успешно обновлено")
            else:
                query = """INSERT INTO transportnoe_sredstvo (gos_nomer, invent_nomer, vin, probeg, model_id,
                          podrazdelenie_id, assigned_driver_id, tekuschee_sostoyanie)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                Database.execute_query(query, (gos_nomer, invent_nomer, vin, probeg, model_id,
                                               podrazdelenie_id, driver_id, status), fetch=False)
                QMessageBox.information(self, "Успех", "ТС успешно добавлено")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
