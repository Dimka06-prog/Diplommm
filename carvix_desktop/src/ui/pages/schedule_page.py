from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QFormLayout, QComboBox, QMessageBox, QDateEdit, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font
from src.permissions import has_permission, ROLE_DRIVER, PERMISSION_ADD_SCHEDULE, PERMISSION_EDIT_SCHEDULE, PERMISSION_DELETE_SCHEDULE
from datetime import date

class SchedulePage(QWidget):
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
        title = QLabel("График работы")
        title.setFont(get_header_font(28))
        title.setStyleSheet("color: #1C1B17;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        if has_permission(self.user_data['rol_id'], PERMISSION_ADD_SCHEDULE):
            add_btn = QPushButton("+ Добавить смену")
            add_btn.setObjectName("primary_btn")
            add_btn.clicked.connect(self.open_add_schedule_dialog)
            header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Дата", "Водитель", "ТС", "Начало", "Конец", "Статус"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("QTableWidget { background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E2E0; }")
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)
        
    def refresh_data(self):
        try:
            if self.user_data['rol_id'] == ROLE_DRIVER:
                # Drivers only see their own schedule
                query = """SELECT s.id, s.date, s.shift_start, s.shift_end, s.status,
                           d.fio as driver_fio, t.gos_nomer
                           FROM work_schedule s
                           LEFT JOIN sotrudnik d ON s.driver_id = d.id
                           LEFT JOIN transportnoe_sredstvo t ON s.ts_id = t.id
                           WHERE s.driver_id = %s
                           ORDER BY s.date DESC"""
                schedules = Database.execute_query(query, (self.user_data['id'],))
            else:
                # Others see all schedules
                query = """SELECT s.id, s.date, s.shift_start, s.shift_end, s.status,
                           d.fio as driver_fio, t.gos_nomer
                           FROM work_schedule s
                           LEFT JOIN sotrudnik d ON s.driver_id = d.id
                           LEFT JOIN transportnoe_sredstvo t ON s.ts_id = t.id
                           ORDER BY s.date DESC"""
                schedules = Database.execute_query(query)

            self.table.setRowCount(len(schedules))

            for row, sch in enumerate(schedules):
                self.table.setItem(row, 0, QTableWidgetItem(str(sch['date'])))
                self.table.setItem(row, 1, QTableWidgetItem(sch.get('driver_fio', '-')))
                self.table.setItem(row, 2, QTableWidgetItem(sch.get('gos_nomer', '-')))
                self.table.setItem(row, 3, QTableWidgetItem(sch['shift_start']))
                self.table.setItem(row, 4, QTableWidgetItem(sch['shift_end']))
                self.table.setItem(row, 5, QTableWidgetItem(sch['status']))
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, sch['id'])
        except Exception as e:
            pass
            
    def open_add_schedule_dialog(self):
        dialog = ScheduleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            
    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item:
            return

        # Drivers cannot edit/delete schedules
        if not has_permission(self.user_data['rol_id'], PERMISSION_EDIT_SCHEDULE):
            return

        schedule_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu()
        if has_permission(self.user_data['rol_id'], PERMISSION_EDIT_SCHEDULE):
            edit_action = menu.addAction("✏️ Редактировать")
        if has_permission(self.user_data['rol_id'], PERMISSION_DELETE_SCHEDULE):
            delete_action = menu.addAction("🗑️ Удалить")

        action = menu.exec(self.table.mapToGlobal(position))

        if action == edit_action:
            self.edit_schedule(schedule_id)
        elif action == delete_action:
            self.delete_schedule(schedule_id)
            
    def edit_schedule(self, schedule_id):
        try:
            query = "SELECT * FROM work_schedule WHERE id = %s"
            result = Database.execute_query(query, (schedule_id,))
            if result:
                dialog = ScheduleDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")
            
    def delete_schedule(self, schedule_id):
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить эту смену?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                Database.execute_query("DELETE FROM work_schedule WHERE id = %s", (schedule_id,), fetch=False)
                self.refresh_data()
                QMessageBox.information(self, "Успех", "Смена удалена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")

class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule_data=None):
        super().__init__(parent)
        self.schedule_data = schedule_data
        self.edit_mode = schedule_data is not None
        self.init_ui()
        
        if self.edit_mode:
            self.populate_fields()
            
    def populate_fields(self):
        if not self.schedule_data:
            return
            
        from PyQt6.QtCore import QDate
        if self.schedule_data.get('date'):
            date_obj = QDate.fromString(str(self.schedule_data['date']), "yyyy-MM-dd")
            self.date_input.setDate(date_obj)
            
        driver_id = self.schedule_data.get('driver_id')
        for i in range(self.driver_combo.count()):
            if self.driver_combo.itemData(i) == driver_id:
                self.driver_combo.setCurrentIndex(i)
                break
                
        ts_id = self.schedule_data.get('ts_id')
        for i in range(self.ts_combo.count()):
            if self.ts_combo.itemData(i) == ts_id:
                self.ts_combo.setCurrentIndex(i)
                break
                
        start = self.schedule_data.get('shift_start', '08:00')
        for i in range(self.start_input.count()):
            if self.start_input.itemText(i) == start:
                self.start_input.setCurrentIndex(i)
                break
                
        end = self.schedule_data.get('shift_end', '20:00')
        for i in range(self.end_input.count()):
            if self.end_input.itemText(i) == end:
                self.end_input.setCurrentIndex(i)
                break
                
        status = self.schedule_data.get('status', 'Запланирована')
        for i in range(self.status_combo.count()):
            if self.status_combo.itemData(i) == status:
                self.status_combo.setCurrentIndex(i)
                break
        
    def init_ui(self):
        self.setWindowTitle("Редактировать смену" if self.edit_mode else "Добавить смену")
        self.setFixedSize(550, 400)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        form_layout = QFormLayout()
        self.date_input = QDateEdit()
        self.date_input.setDate(date.today())

        self.driver_combo = QComboBox()
        self.driver_combo.setMinimumWidth(300)
        self.ts_combo = QComboBox()
        self.ts_combo.setMinimumWidth(300)
        self.start_input = QComboBox()
        self.start_input.setMinimumWidth(300)
        self.end_input = QComboBox()
        self.end_input.setMinimumWidth(300)
        self.status_combo = QComboBox()
        self.status_combo.setMinimumWidth(300)
        
        try:
            drivers = Database.execute_query("SELECT id, fio FROM sotrudnik WHERE rol_id = 2")
            for driver in drivers:
                self.driver_combo.addItem(driver['fio'], driver['id'])
        except: pass
        
        try:
            vehicles = Database.execute_query("SELECT id, gos_nomer FROM transportnoe_sredstvo")
            for veh in vehicles:
                self.ts_combo.addItem(veh['gos_nomer'], veh['id'])
        except: pass
        
        self.start_input.addItems(["08:00", "09:00", "10:00"])
        self.end_input.addItems(["20:00", "21:00", "22:00"])
        self.status_combo.addItem("Запланирована", "Запланирована")
        self.status_combo.addItem("Выполнена", "Выполнена")
        
        form_layout.addRow("Дата:", self.date_input)
        form_layout.addRow("Водитель:", self.driver_combo)
        form_layout.addRow("ТС:", self.ts_combo)
        form_layout.addRow("Начало:", self.start_input)
        form_layout.addRow("Конец:", self.end_input)
        form_layout.addRow("Статус:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.save_schedule)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
    def save_schedule(self):
        try:
            if self.edit_mode:
                query = """UPDATE work_schedule SET driver_id = %s, ts_id = %s, date = %s, 
                          shift_start = %s, shift_end = %s, status = %s WHERE id = %s"""
                Database.execute_query(query, (
                    self.driver_combo.currentData(), self.ts_combo.currentData(),
                    self.date_input.date().toString("yyyy-MM-dd"),
                    self.start_input.currentText(), self.end_input.currentText(),
                    self.status_combo.currentData(), self.schedule_data['id']
                ), fetch=False)
                QMessageBox.information(self, "Успех", "Смена успешно обновлена")
            else:
                query = """INSERT INTO work_schedule (driver_id, ts_id, date, shift_start, shift_end, status)
                          VALUES (%s, %s, %s, %s, %s, %s)"""
                Database.execute_query(query, (
                    self.driver_combo.currentData(), self.ts_combo.currentData(),
                    self.date_input.date().toString("yyyy-MM-dd"),
                    self.start_input.currentText(), self.end_input.currentText(),
                    self.status_combo.currentData()
                ), fetch=False)
                QMessageBox.information(self, "Успех", "Смена успешно добавлена")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
