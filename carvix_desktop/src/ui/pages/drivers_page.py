from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QLineEdit, QFormLayout, QComboBox,
                             QMessageBox, QDateEdit, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font
from src.permissions import has_permission, PERMISSION_ADD_DRIVER, PERMISSION_EDIT_DRIVER, PERMISSION_DELETE_DRIVER
from datetime import date
import bcrypt

class DriversPage(QWidget):
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
        title = QLabel("Водители")
        title.setFont(get_header_font(28))
        title.setStyleSheet("color: #1C1B17;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        if has_permission(self.user_data['rol_id'], PERMISSION_ADD_DRIVER):
            add_btn = QPushButton("+ Добавить водителя")
            add_btn.setObjectName("primary_btn")
            add_btn.clicked.connect(self.open_add_driver_dialog)
            header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ФИО", "Логин", "Лицензия", "Телефон", "Роль", "Подразделение"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
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
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)
        
    def refresh_data(self):
        try:
            query = """
                SELECT s.id, s.fio, s.login, s.license_number, s.phone,
                       r.nazvanie as rol_name, p.nazvanie as podrazdelenie_name
                FROM sotrudnik s
                JOIN rol r ON s.rol_id = r.id
                JOIN podrazdelenie p ON s.podrazdelenie_id = p.id
                ORDER BY s.fio
            """
            drivers = Database.execute_query(query)
            self.table.setRowCount(len(drivers))
            
            for row, driver in enumerate(drivers):
                self.table.setItem(row, 0, QTableWidgetItem(driver['fio']))
                self.table.setItem(row, 1, QTableWidgetItem(driver['login']))
                self.table.setItem(row, 2, QTableWidgetItem(driver.get('license_number', '-')))
                self.table.setItem(row, 3, QTableWidgetItem(driver.get('phone', '-')))
                self.table.setItem(row, 4, QTableWidgetItem(driver['rol_name']))
                self.table.setItem(row, 5, QTableWidgetItem(driver['podrazdelenie_name']))
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, driver['id'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")
            
    def open_add_driver_dialog(self):
        dialog = DriverDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            
    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item:
            return

        # Check permissions
        if not has_permission(self.user_data['rol_id'], PERMISSION_EDIT_DRIVER):
            return

        driver_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu()
        if has_permission(self.user_data['rol_id'], PERMISSION_EDIT_DRIVER):
            edit_action = menu.addAction("✏️ Редактировать")
        if has_permission(self.user_data['rol_id'], PERMISSION_DELETE_DRIVER):
            delete_action = menu.addAction("🗑️ Удалить")

        action = menu.exec(self.table.mapToGlobal(position))

        if action == edit_action:
            self.edit_driver(driver_id)
        elif action == delete_action:
            self.delete_driver(driver_id)
            
    def edit_driver(self, driver_id):
        try:
            query = "SELECT * FROM sotrudnik WHERE id = %s"
            result = Database.execute_query(query, (driver_id,))
            if result:
                dialog = DriverDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")
            
    def delete_driver(self, driver_id):
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этого водителя?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                Database.execute_query("DELETE FROM sotrudnik WHERE id = %s", (driver_id,), fetch=False)
                self.refresh_data()
                QMessageBox.information(self, "Успех", "Водитель удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")

class DriverDialog(QDialog):
    def __init__(self, parent=None, driver_data=None):
        super().__init__(parent)
        self.driver_data = driver_data
        self.edit_mode = driver_data is not None
        self.init_ui()
        
        if self.edit_mode:
            self.populate_fields()
        
    def populate_fields(self):
        if not self.driver_data:
            return
            
        self.fio_input.setText(self.driver_data.get('fio', ''))
        self.login_input.setText(self.driver_data.get('login', ''))
        self.license_input.setText(self.driver_data.get('license_number', ''))
        self.phone_input.setText(self.driver_data.get('phone', ''))
        
        role_id = self.driver_data.get('rol_id')
        for i in range(self.role_combo.count()):
            if self.role_combo.itemData(i) == role_id:
                self.role_combo.setCurrentIndex(i)
                break
                
        dept_id = self.driver_data.get('podrazdelenie_id')
        for i in range(self.dept_combo.count()):
            if self.dept_combo.itemData(i) == dept_id:
                self.dept_combo.setCurrentIndex(i)
                break
        
        self.password_input.setPlaceholderText("Оставьте пустым, чтобы не менять пароль")
        
    def init_ui(self):
        self.setWindowTitle("Редактировать водителя" if self.edit_mode else "Добавить водителя")
        self.setFixedSize(550, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        form_layout = QFormLayout()

        self.fio_input = QLineEdit()
        self.fio_input.setPlaceholderText("Иванов Иван Иванович")
        self.fio_input.setMinimumWidth(300)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("ivanov")
        self.login_input.setMinimumWidth(300)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumWidth(300)

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("Номер водительской лицензии")
        self.license_input.setMinimumWidth(300)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+7 (999) 123-45-67")
        self.phone_input.setMinimumWidth(300)

        self.role_combo = QComboBox()
        self.role_combo.addItem("Водитель", 2)
        self.role_combo.addItem("Диспетчер", 1)
        self.role_combo.setMinimumWidth(300)

        self.dept_combo = QComboBox()
        self.dept_combo.setMinimumWidth(300)
        try:
            depts = Database.execute_query("SELECT id, nazvanie FROM podrazdelenie")
            for dept in depts:
                self.dept_combo.addItem(dept['nazvanie'], dept['id'])
        except:
            self.dept_combo.addItem("Основное подразделение", 1)
        
        form_layout.addRow("ФИО:", self.fio_input)
        form_layout.addRow("Логин:", self.login_input)
        form_layout.addRow("Пароль:", self.password_input)
        form_layout.addRow("Лицензия:", self.license_input)
        form_layout.addRow("Телефон:", self.phone_input)
        form_layout.addRow("Роль:", self.role_combo)
        form_layout.addRow("Подразделение:", self.dept_combo)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.save_driver)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
    def save_driver(self):
        fio = self.fio_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        license_num = self.license_input.text().strip()
        phone = self.phone_input.text().strip()
        role_id = self.role_combo.currentData()
        dept_id = self.dept_combo.currentData()
        
        if not fio or not login:
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return
        
        try:
            if self.edit_mode:
                if password:
                    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    query = """UPDATE sotrudnik SET fio = %s, login = %s, parol_hash = %s, rol_id = %s, 
                              podrazdelenie_id = %s, license_number = %s, phone = %s WHERE id = %s"""
                    Database.execute_query(query, (fio, login, password_hash, role_id, dept_id, license_num, phone, self.driver_data['id']), fetch=False)
                else:
                    query = """UPDATE sotrudnik SET fio = %s, login = %s, rol_id = %s, 
                              podrazdelenie_id = %s, license_number = %s, phone = %s WHERE id = %s"""
                    Database.execute_query(query, (fio, login, role_id, dept_id, license_num, phone, self.driver_data['id']), fetch=False)
                QMessageBox.information(self, "Успех", "Водитель успешно обновлен")
            else:
                if not password:
                    QMessageBox.warning(self, "Ошибка", "Введите пароль")
                    return
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                query = """INSERT INTO sotrudnik (fio, login, parol_hash, rol_id, podrazdelenie_id, license_number, phone)
                          VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                Database.execute_query(query, (fio, login, password_hash, role_id, dept_id, license_num, phone), fetch=False)
                QMessageBox.information(self, "Успех", "Водитель успешно добавлен")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")
