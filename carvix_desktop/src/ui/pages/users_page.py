from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QLineEdit, QComboBox,
                             QMessageBox, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font
from src.permissions import has_permission, PERMISSION_MANAGE_USERS
import bcrypt

class UsersPage(QWidget):
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
        title = QLabel("Пользователи")
        title.setFont(get_header_font(28))
        title.setStyleSheet("color: #1C1B17;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        if has_permission(self.user_data['rol_id'], PERMISSION_MANAGE_USERS):
            add_btn = QPushButton("+ Добавить пользователя")
            add_btn.setObjectName("primary_btn")
            add_btn.clicked.connect(self.open_add_user_dialog)
            header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ФИО", "Логин", "Роль", "Лицензия", "Телефон"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

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
            query = """SELECT s.id, s.fio, s.login, s.license_number, s.phone,
                       r.nazvanie as rol_name
                       FROM sotrudnik s
                       JOIN rol r ON s.rol_id = r.id
                       ORDER BY s.fio"""
            users = Database.execute_query(query)
            self.table.setRowCount(len(users))

            for row, user in enumerate(users):
                self.table.setItem(row, 0, QTableWidgetItem(user['fio']))
                self.table.setItem(row, 1, QTableWidgetItem(user['login']))
                self.table.setItem(row, 2, QTableWidgetItem(user['rol_name']))
                self.table.setItem(row, 3, QTableWidgetItem(user.get('license_number', '-')))
                self.table.setItem(row, 4, QTableWidgetItem(user.get('phone', '-')))
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, user['id'])
        except Exception as e:
            pass

    def open_add_user_dialog(self):
        dialog = UserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()

    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item:
            return

        if not has_permission(self.user_data['rol_id'], PERMISSION_MANAGE_USERS):
            return

        user_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu()
        edit_action = menu.addAction("✏️ Редактировать")
        delete_action = menu.addAction("🗑️ Удалить")

        action = menu.exec(self.table.mapToGlobal(position))

        if action == edit_action:
            self.edit_user(user_id)
        elif action == delete_action:
            self.delete_user(user_id)

    def edit_user(self, user_id):
        try:
            query = "SELECT * FROM sotrudnik WHERE id = %s"
            result = Database.execute_query(query, (user_id,))
            if result:
                dialog = UserDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def delete_user(self, user_id):
        # Prevent deleting yourself
        if user_id == self.user_data['id']:
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить текущего пользователя")
            return

        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этого пользователя?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                Database.execute_query("DELETE FROM sotrudnik WHERE id = %s", (user_id,), fetch=False)
                self.refresh_data()
                QMessageBox.information(self, "Успех", "Пользователь удален")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")


class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.edit_mode = user_data is not None
        self.init_ui()

        if self.edit_mode:
            self.populate_fields()

    def populate_fields(self):
        if not self.user_data:
            return

        self.fio_input.setText(self.user_data.get('fio', ''))
        self.login_input.setText(self.user_data.get('login', ''))
        self.license_input.setText(self.user_data.get('license_number', ''))
        self.phone_input.setText(self.user_data.get('phone', ''))

        rol_id = self.user_data.get('rol_id')
        for i in range(self.role_combo.count()):
            if self.role_combo.itemData(i) == rol_id:
                self.role_combo.setCurrentIndex(i)
                break

    def init_ui(self):
        self.setWindowTitle("Редактировать пользователя" if self.edit_mode else "Добавить пользователя")
        self.setFixedSize(500, 400)

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
        self.password_input.setPlaceholderText("Пароль (минимум 3 символа)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumWidth(300)

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("Номер водительской лицензии")
        self.license_input.setMinimumWidth(300)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+7 (999) 123-45-67")
        self.phone_input.setMinimumWidth(300)

        self.role_combo = QComboBox()
        self.role_combo.addItem("Диспетчер", 1)
        self.role_combo.addItem("Водитель", 2)
        self.role_combo.addItem("Механик", 3)
        self.role_combo.addItem("Администратор", 4)
        self.role_combo.setMinimumWidth(300)

        form_layout.addRow("ФИО:", self.fio_input)
        form_layout.addRow("Логин:", self.login_input)
        if not self.edit_mode:
            form_layout.addRow("Пароль:", self.password_input)
        form_layout.addRow("Лицензия:", self.license_input)
        form_layout.addRow("Телефон:", self.phone_input)
        form_layout.addRow("Роль:", self.role_combo)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary_btn")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Сохранить")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.save_user)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def save_user(self):
        try:
            fio = self.fio_input.text().strip()
            login = self.login_input.text().strip()
            password = self.password_input.text().strip() if not self.edit_mode else None
            license_number = self.license_input.text().strip()
            phone = self.phone_input.text().strip()
            rol_id = self.role_combo.currentData()

            if not fio or not login:
                QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
                return

            if not self.edit_mode and not password:
                QMessageBox.warning(self, "Ошибка", "Введите пароль")
                return

            if not self.edit_mode and len(password) < 3:
                QMessageBox.warning(self, "Ошибка", "Пароль должен быть минимум 3 символа")
                return

            if self.edit_mode:
                query = """UPDATE sotrudnik SET fio = %s, login = %s, license_number = %s,
                          phone = %s, rol_id = %s WHERE id = %s"""
                Database.execute_query(query, (fio, login, license_number, phone, rol_id, self.user_data['id']), fetch=False)
                QMessageBox.information(self, "Успех", "Пользователь успешно обновлен")
            else:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                query = """INSERT INTO sotrudnik (fio, login, parol_hash, license_number, phone, rol_id)
                          VALUES (%s, %s, %s, %s, %s, %s)"""
                Database.execute_query(query, (fio, login, password_hash, license_number, phone, rol_id), fetch=False)
                QMessageBox.information(self, "Успех", "Пользователь успешно добавлен")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
