from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFrame, QGridLayout,
                             QMessageBox, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font
from src.logger import logger
from src.error_handler import ErrorHandler
from config import APP_NAME
import bcrypt

class AuthDialog(QDialog):
    authenticated = pyqtSignal(dict)
    exit_app = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.user_data = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(APP_NAME)
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main container with card styling
        self.main_widget = QWidget()
        self.main_widget.setObjectName("auth_dialog")
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Logo/Title section
        title_layout = QVBoxLayout()
        
        logo_label = QLabel("Carvix")
        logo_label.setFont(get_header_font(48))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("color: #1C1B17; margin-bottom: 10px;")
        
        subtitle = QLabel("Учет водителей и транспортных средств")
        subtitle.setFont(get_font(13))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #6F6D67;")
        
        title_layout.addWidget(logo_label)
        title_layout.addWidget(subtitle)
        layout.addLayout(title_layout)
        
        # Form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)
        
        # Login field
        login_label = QLabel("Логин")
        login_label.setFont(get_font(12))
        login_label.setStyleSheet("color: #9A9892;")
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.setFixedHeight(50)
        self.login_input.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF;
                border: 1px solid #E2E2E0;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #1C1B17;
            }
        """)
        
        form_layout.addWidget(login_label)
        form_layout.addWidget(self.login_input)
        
        # Password field
        password_label = QLabel("Пароль")
        password_label.setFont(get_font(12))
        password_label.setStyleSheet("color: #9A9892;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF;
                border: 1px solid #E2E2E0;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #1C1B17;
            }
        """)
        
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)

        layout.addLayout(form_layout)
        
        # Login button
        self.login_btn = QPushButton("Войти")
        self.login_btn.setFixedHeight(54)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: #1C1B17;
                color: #FFFFFF;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #3F3D38;
            }
            QPushButton:pressed {
                background: #6F6D67;
            }
        """)
        self.login_btn.clicked.connect(self.authenticate)
        layout.addWidget(self.login_btn)
        
        # Exit button
        exit_btn = QPushButton("Выход")
        exit_btn.setFixedHeight(40)
        exit_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6F6D67;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #1C1B17;
            }
        """)
        exit_btn.clicked.connect(self.exit_app.emit)
        layout.addWidget(exit_btn)
        
        # Add main widget to dialog
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Enter key support
        self.password_input.returnPressed.connect(self.authenticate)
        
    def authenticate(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            # Query employee from database
            query = """
                SELECT s.id, s.fio, s.login, s.parol_hash,
                       s.rol_id, r.nazvanie as rol_name,
                       s.podrazdelenie_id, p.nazvanie as podrazdelenie_name
                FROM sotrudnik s
                JOIN rol r ON s.rol_id = r.id
                JOIN podrazdelenie p ON s.podrazdelenie_id = p.id
                WHERE s.login = %s
            """
            result = Database.execute_query(query, (login,))

            if not result:
                logger.log_login(0, login, "Unknown", False)
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
                return

            user = result[0]

            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), user['parol_hash'].encode('utf-8')):
                # Роль берется из базы данных
                self.user_data = {
                    'id': user['id'],
                    'fio': user['fio'],
                    'login': user['login'],
                    'rol_id': user['rol_id'],
                    'rol_name': user['rol_name'],
                    'podrazdelenie_id': user['podrazdelenie_id'],
                    'podrazdelenie_name': user['podrazdelenie_name']
                }

                self.authenticated.emit(self.user_data)
                logger.log_login(user['id'], user['login'], user['rol_name'], True)
                self.accept()
            else:
                logger.log_login(user['id'], login, user['rol_name'], False)

        except Exception as e:
            logger.log_error(0, str(e), "Authentication")
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к базе данных: {str(e)}")
