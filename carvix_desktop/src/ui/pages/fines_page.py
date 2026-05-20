from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QLineEdit, QComboBox,
                             QMessageBox, QDateEdit, QMenu, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font
from src.permissions import has_permission, ROLE_DRIVER, PERMISSION_ADD_FINE, PERMISSION_EDIT_FINE, PERMISSION_DELETE_FINE
from datetime import date
from src.api.gibdd_api import GibddAPI

class FinesPage(QWidget):
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
        title = QLabel("Штрафы")
        title.setFont(get_header_font(28))
        title.setStyleSheet("color: #1C1B17;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        if has_permission(self.user_data['rol_id'], PERMISSION_ADD_FINE):
            add_btn = QPushButton("+ Добавить штраф")
            add_btn.setObjectName("primary_btn")
            add_btn.clicked.connect(self.open_add_fine_dialog)
            header_layout.addWidget(add_btn)

        if has_permission(self.user_data['rol_id'], 'view_reports'):
            sync_btn = QPushButton("🔄 Синхронизировать с ГИБДД")
            sync_btn.setObjectName("secondary_btn")
            sync_btn.clicked.connect(self.sync_with_gibdd)
            header_layout.addWidget(sync_btn)
        layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ТС", "Дата", "Сумма", "Описание", "Постановление", "Статус"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("QTableWidget { background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E2E0; }")
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)
        
    def refresh_data(self):
        try:
            if self.user_data['rol_id'] == ROLE_DRIVER:
                # Drivers only see fines for vehicles assigned to them
                query = """SELECT f.id, f.ts_id, f.date, f.amount, f.description, f.status, f.postanovlenie_number, t.gos_nomer
                           FROM fines f
                           LEFT JOIN transportnoe_sredstvo t ON f.ts_id = t.id
                           WHERE t.assigned_driver_id = %s
                           ORDER BY f.date DESC"""
                fines = Database.execute_query(query, (self.user_data['id'],))
            else:
                # Others see all fines
                query = """SELECT f.id, f.ts_id, f.date, f.amount, f.description, f.status, f.postanovlenie_number, t.gos_nomer
                           FROM fines f
                           LEFT JOIN transportnoe_sredstvo t ON f.ts_id = t.id
                           ORDER BY f.date DESC"""
                fines = Database.execute_query(query)

            self.table.setRowCount(len(fines))

            for row, fine in enumerate(fines):
                self.table.setItem(row, 0, QTableWidgetItem(fine.get('gos_nomer', '-')))
                self.table.setItem(row, 1, QTableWidgetItem(str(fine['date'])))
                self.table.setItem(row, 2, QTableWidgetItem(str(fine['amount']) + " руб."))
                self.table.setItem(row, 3, QTableWidgetItem(fine['description']))
                self.table.setItem(row, 4, QTableWidgetItem(fine.get('postanovlenie_number', '-')))
                self.table.setItem(row, 5, QTableWidgetItem(fine['status']))
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, fine['id'])
        except Exception as e:
            pass
            
    def open_add_fine_dialog(self):
        dialog = FineDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            
    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item:
            return

        # Drivers cannot edit/delete fines
        if not has_permission(self.user_data['rol_id'], PERMISSION_EDIT_FINE):
            return

        fine_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu()
        if has_permission(self.user_data['rol_id'], PERMISSION_EDIT_FINE):
            edit_action = menu.addAction("✏️ Редактировать")
        if has_permission(self.user_data['rol_id'], PERMISSION_DELETE_FINE):
            delete_action = menu.addAction("🗑️ Удалить")

        action = menu.exec(self.table.mapToGlobal(position))

        if action == edit_action:
            self.edit_fine(fine_id)
        elif action == delete_action:
            self.delete_fine(fine_id)
            
    def edit_fine(self, fine_id):
        try:
            query = "SELECT * FROM fines WHERE id = %s"
            result = Database.execute_query(query, (fine_id,))
            if result:
                dialog = FineDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")
            
    def delete_fine(self, fine_id):
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот штраф?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                Database.execute_query("DELETE FROM fines WHERE id = %s", (fine_id,), fetch=False)
                self.refresh_data()
                QMessageBox.information(self, "Успех", "Штраф удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")
            
    def sync_with_gibdd(self):
        try:
            api = GibddAPI()
            vehicles = Database.execute_query("SELECT id, gos_nomer FROM transportnoe_sredstvo")
            synced_total = 0
            
            for vehicle in vehicles:
                synced = api.sync_fines_to_db(Database, vehicle['id'], vehicle['gos_nomer'])
                synced_total += synced
            
            if synced_total > 0:
                QMessageBox.information(self, "Успех", f"Синхронизировано {synced_total} штрафов")
                self.refresh_data()
            else:
                QMessageBox.information(self, "Информация", "Новых штрафов не найдено")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка синхронизации: {str(e)}")

class FineDialog(QDialog):
    def __init__(self, parent=None, fine_data=None):
        super().__init__(parent)
        self.fine_data = fine_data
        self.edit_mode = fine_data is not None
        self.init_ui()
        
        if self.edit_mode:
            self.populate_fields()
            
    def populate_fields(self):
        if not self.fine_data:
            return
            
        from PyQt6.QtCore import QDate
        if self.fine_data.get('date'):
            date_obj = QDate.fromString(str(self.fine_data['date']), "yyyy-MM-dd")
            self.date_input.setDate(date_obj)
            
        ts_id = self.fine_data.get('ts_id')
        for i in range(self.ts_combo.count()):
            if self.ts_combo.itemData(i) == ts_id:
                self.ts_combo.setCurrentIndex(i)
                break
                
        self.amount_input.setValue(self.fine_data.get('amount', 0))
        
        desc = self.fine_data.get('description', 'Другое')
        for i in range(self.desc_input.count()):
            if self.desc_input.itemText(i) == desc:
                self.desc_input.setCurrentIndex(i)
                break
                
        status = self.fine_data.get('status', 'Не оплачен')
        for i in range(self.status_combo.count()):
            if self.status_combo.itemData(i) == status:
                self.status_combo.setCurrentIndex(i)
                break
        
    def init_ui(self):
        self.setWindowTitle("Редактировать штраф" if self.edit_mode else "Добавить штраф")
        self.setFixedSize(450, 350)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)
        
        form_layout = QFormLayout()
        self.ts_combo = QComboBox()
        self.date_input = QDateEdit()
        self.date_input.setDate(date.today())
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 100000)
        self.amount_input.setValue(0)
        self.desc_input = QComboBox()
        self.desc_input.addItems(["Превышение скорости", "Неправильная парковка", "Проезд на красный", "Другое"])
        self.post_input = QComboBox()
        self.status_combo = QComboBox()
        self.status_combo.addItem("Не оплачен", "Не оплачен")
        self.status_combo.addItem("Оплачен", "Оплачен")
        
        try:
            vehicles = Database.execute_query("SELECT id, gos_nomer FROM transportnoe_sredstvo")
            for veh in vehicles:
                self.ts_combo.addItem(veh['gos_nomer'], veh['id'])
        except: pass
        
        form_layout.addRow("ТС:", self.ts_combo)
        form_layout.addRow("Дата:", self.date_input)
        form_layout.addRow("Сумма (руб):", self.amount_input)
        form_layout.addRow("Описание:", self.desc_input)
        form_layout.addRow("Статус:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.save_fine)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
    def save_fine(self):
        try:
            if self.edit_mode:
                query = """UPDATE fines SET ts_id = %s, date = %s, amount = %s, description = %s, status = %s WHERE id = %s"""
                Database.execute_query(query, (
                    self.ts_combo.currentData(),
                    self.date_input.date().toString("yyyy-MM-dd"),
                    self.amount_input.value(),
                    self.desc_input.currentText(),
                    self.status_combo.currentData(),
                    self.fine_data['id']
                ), fetch=False)
                QMessageBox.information(self, "Успех", "Штраф успешно обновлен")
            else:
                query = """INSERT INTO fines (ts_id, date, amount, description, status)
                          VALUES (%s, %s, %s, %s, %s)"""
                Database.execute_query(query, (
                    self.ts_combo.currentData(),
                    self.date_input.date().toString("yyyy-MM-dd"),
                    self.amount_input.value(),
                    self.desc_input.currentText(),
                    self.status_combo.currentData()
                ), fetch=False)
                QMessageBox.information(self, "Успех", "Штраф успешно добавлен")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
