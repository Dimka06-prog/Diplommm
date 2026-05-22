from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                             QLabel, QPushButton, QFormLayout, QLineEdit,
                             QMessageBox, QDateEdit, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font
from src.permissions import has_permission, ROLE_DRIVER
from src.validation import Validator, ValidationError
import bcrypt

class ProfilePage(QWidget):
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
        title = QLabel("Профиль")
        title.setFont(get_header_font(28))
        title.setStyleSheet("color: #1C1B17;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Profile card
        profile_frame = QFrame()
        profile_frame.setObjectName("card_light")
        profile_layout = QVBoxLayout(profile_frame)
        profile_layout.setContentsMargins(30, 30, 30, 30)
        profile_layout.setSpacing(20)

        # User info
        info_label = QLabel("Личная информация")
        info_label.setFont(get_header_font(18))
        info_label.setStyleSheet("color: #1C1B17;")
        profile_layout.addWidget(info_label)

        form_layout = QFormLayout()

        self.fio_display = QLabel()
        self.fio_display.setFont(get_font(14))
        self.fio_display.setStyleSheet("color: #3F3D38;")

        self.login_display = QLabel()
        self.login_display.setFont(get_font(14))
        self.login_display.setStyleSheet("color: #3F3D38;")

        self.role_display = QLabel()
        self.role_display.setFont(get_font(14))
        self.role_display.setStyleSheet("color: #3F3D38;")

        self.license_display = QLabel()
        self.license_display.setFont(get_font(14))
        self.license_display.setStyleSheet("color: #3F3D38;")

        self.phone_display = QLabel()
        self.phone_display.setFont(get_font(14))
        self.phone_display.setStyleSheet("color: #3F3D38;")

        self.dept_display = QLabel()
        self.dept_display.setFont(get_font(14))
        self.dept_display.setStyleSheet("color: #3F3D38;")

        form_layout.addRow("ФИО:", self.fio_display)
        form_layout.addRow("Логин:", self.login_display)
        form_layout.addRow("Роль:", self.role_display)
        form_layout.addRow("Лицензия:", self.license_display)
        form_layout.addRow("Телефон:", self.phone_display)
        form_layout.addRow("Подразделение:", self.dept_display)

        profile_layout.addLayout(form_layout)

        # Password change section
        if has_permission(self.user_data['rol_id'], 'edit_driver'):
            password_label = QLabel("Сменить пароль")
            password_label.setFont(get_header_font(18))
            password_label.setStyleSheet("color: #1C1B17;")
            profile_layout.addWidget(password_label)

            password_form = QFormLayout()

            self.current_password = QLineEdit()
            self.current_password.setPlaceholderText("Текущий пароль")
            self.current_password.setEchoMode(QLineEdit.EchoMode.Password)

            self.new_password = QLineEdit()
            self.new_password.setPlaceholderText("Новый пароль")
            self.new_password.setEchoMode(QLineEdit.EchoMode.Password)

            self.confirm_password = QLineEdit()
            self.confirm_password.setPlaceholderText("Подтвердите пароль")
            self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

            password_form.addRow("Текущий пароль:", self.current_password)
            password_form.addRow("Новый пароль:", self.new_password)
            password_form.addRow("Подтвердите:", self.confirm_password)

            profile_layout.addLayout(password_form)

            change_password_btn = QPushButton("Сменить пароль")
            change_password_btn.setObjectName("primary_btn")
            change_password_btn.clicked.connect(self.change_password)
            profile_layout.addWidget(change_password_btn)

        layout.addWidget(profile_frame)
        layout.addStretch()

    def refresh_data(self):
        try:
            query = """
                SELECT s.fio, s.login, s.license_number, s.phone,
                       r.nazvanie as rol_name, p.nazvanie as podrazdelenie_name
                FROM sotrudnik s
                JOIN rol r ON s.rol_id = r.id
                LEFT JOIN podrazdelenie p ON s.podrazdelenie_id = p.id
                WHERE s.id = %s
            """
            result = Database.execute_query(query, (self.user_data['id'],))
            if result:
                data = result[0]
                self.fio_display.setText(data['fio'])
                self.login_display.setText(data['login'])
                self.role_display.setText(data['rol_name'])
                self.license_display.setText(data.get('license_number', '-'))
                self.phone_display.setText(data.get('phone', '-'))
                self.dept_display.setText(data.get('podrazdelenie_name', '-'))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def change_password(self):
        current = self.current_password.text().strip()
        new = self.new_password.text().strip()
        confirm = self.confirm_password.text().strip()

        if not current or not new or not confirm:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        if new != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        # Валидация нового пароля
        try:
            Validator.validate_password(new)
        except ValidationError as e:
            QMessageBox.warning(self, "Ошибка валидации", str(e))
            return

        try:
            # Get current password hash
            query = "SELECT parol_hash FROM sotrudnik WHERE id = %s"
            result = Database.execute_query(query, (self.user_data['id'],))
            if not result:
                QMessageBox.critical(self, "Ошибка", "Пользователь не найден")
                return

            current_hash = result[0]['parol_hash']

            # Verify current password
            if not bcrypt.checkpw(current.encode('utf-8'), current_hash.encode('utf-8')):
                QMessageBox.warning(self, "Ошибка", "Неверный текущий пароль")
                return

            # Update password
            new_hash = bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            update_query = "UPDATE sotrudnik SET parol_hash = %s WHERE id = %s"
            Database.execute_query(update_query, (new_hash, self.user_data['id']), fetch=False)

            QMessageBox.information(self, "Успех", "Пароль успешно изменен")
            self.current_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка смены пароля: {str(e)}")
