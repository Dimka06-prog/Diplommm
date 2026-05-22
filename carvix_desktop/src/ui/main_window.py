from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                             QLabel, QPushButton, QStackedWidget, QSizePolicy, QMainWindow)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font, STYLESHEET
from src.permissions import get_menu_items, get_role_name
from src.settings_manager import SettingsManager
from src.logger import logger
from config import APP_NAME, COLORS

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.inactivity_timer = QTimer()
        self.inactivity_timer.timeout.connect(self.handle_session_timeout)
        self.reset_inactivity_timer()
        self.init_ui()

    def reset_inactivity_timer(self):
        """Сброс таймера бездействия"""
        timeout_minutes = int(SettingsManager.get_setting('session_timeout_minutes', '60'))
        timeout_ms = timeout_minutes * 60 * 1000  # Convert to milliseconds
        self.inactivity_timer.stop()
        self.inactivity_timer.start(timeout_ms)

    def handle_session_timeout(self):
        """Обработка тайм-аута сессии"""
        logger.log_logout(self.user_data['id'], self.user_data['login'])
        QMessageBox.warning(self, "Тайм-аут сессии",
                          "Вы были автоматически вышли из-за бездействия.")
        self.logout()

    def mousePressEvent(self, event):
        """Обработка нажатия мыши для сброса таймера"""
        self.reset_inactivity_timer()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """Обработка нажатия клавиши для сброса таймера"""
        self.reset_inactivity_timer()
        super().keyPressEvent(event)
        
    def init_ui(self):
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.create_sidebar()
        
        # Content area
        self.create_content_area()
        
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(8)
        
        # Logo
        logo_label = QLabel("Carvix")
        logo_label.setFont(get_header_font(28))
        logo_label.setStyleSheet("color: #1C1B17; margin-bottom: 20px;")
        sidebar_layout.addWidget(logo_label)
        
        # Navigation buttons (role-based)
        self.nav_buttons = {}

        nav_items = get_menu_items(self.user_data['rol_id'])
        
        for key, text, icon in nav_items:
            btn = QPushButton(f"{icon}  {text}")
            btn.setObjectName("sidebar_btn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self.navigate_to(k))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn
        
        sidebar_layout.addStretch()
        
        # User info
        user_frame = QFrame()
        user_frame.setStyleSheet("background: rgba(255,255,255,0.5); border-radius: 12px; padding: 12px;")
        user_layout = QVBoxLayout(user_frame)
        user_layout.setSpacing(4)
        
        user_name = QLabel(self.user_data['fio'])
        user_name.setFont(get_font(13, QFont.Weight.Bold))
        user_name.setStyleSheet("color: #1C1B17;")
        user_name.setWordWrap(True)
        
        user_role = QLabel(get_role_name(self.user_data['rol_id']))
        user_role.setFont(get_font(11))
        user_role.setStyleSheet("color: #6F6D67;")
        
        user_layout.addWidget(user_name)
        user_layout.addWidget(user_role)
        sidebar_layout.addWidget(user_frame)
        
        # Logout button
        logout_btn = QPushButton("🚪  Выйти")
        logout_btn.setObjectName("sidebar_btn")
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        self.main_layout.addWidget(sidebar)
        
    def create_content_area(self):
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(70)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        self.page_title = QLabel("Дашборд")
        self.page_title.setObjectName("header_title")
        header_layout.addWidget(self.page_title)
        
        header_layout.addStretch()
        
        content_layout.addWidget(header)
        
        # Stacked widget for pages
        self.pages = QStackedWidget()
        content_layout.addWidget(self.pages)
        
        self.main_layout.addWidget(content_area)
        
        # Initialize pages
        self.init_pages()
        
    def init_pages(self):
        from src.ui.pages.dashboard_page import DashboardPage
        from src.ui.pages.drivers_page import DriversPage
        from src.ui.pages.vehicles_page import VehiclesPage
        from src.ui.pages.schedule_page import SchedulePage
        from src.ui.pages.maintenance_page import MaintenancePage
        from src.ui.pages.fines_page import FinesPage
        from src.ui.pages.reports_page import ReportsPage
        from src.ui.pages.profile_page import ProfilePage
        from src.ui.pages.users_page import UsersPage
        from src.ui.pages.settings_page import SettingsPage

        self.dashboard_page = DashboardPage(self.user_data)
        self.drivers_page = DriversPage(self.user_data)
        self.vehicles_page = VehiclesPage(self.user_data)
        self.schedule_page = SchedulePage(self.user_data)
        self.maintenance_page = MaintenancePage(self.user_data)
        self.fines_page = FinesPage(self.user_data)
        self.reports_page = ReportsPage(self.user_data)
        self.profile_page = ProfilePage(self.user_data)
        self.users_page = UsersPage(self.user_data)
        self.settings_page = SettingsPage(self.user_data)

        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.drivers_page)
        self.pages.addWidget(self.vehicles_page)
        self.pages.addWidget(self.schedule_page)
        self.pages.addWidget(self.maintenance_page)
        self.pages.addWidget(self.fines_page)
        self.pages.addWidget(self.reports_page)
        self.pages.addWidget(self.profile_page)
        self.pages.addWidget(self.users_page)
        self.pages.addWidget(self.settings_page)
        
        # Set default page
        self.navigate_to("dashboard")
        
    def navigate_to(self, page_key):
        # Update navigation buttons
        for key, btn in self.nav_buttons.items():
            btn.setChecked(key == page_key)
        
        # Update page title
        titles = {
            "dashboard": "Дашборд",
            "drivers": "Водители",
            "vehicles": "Транспорт",
            "schedule": "График работы",
            "maintenance": "ТО и Страховка",
            "fines": "Штрафы",
            "reports": "Отчеты",
            "profile": "Профиль",
            "users": "Пользователи",
            "settings": "Настройки"
        }
        self.page_title.setText(titles.get(page_key, ""))

        # Show page
        page_index = {
            "dashboard": 0,
            "drivers": 1,
            "vehicles": 2,
            "schedule": 3,
            "maintenance": 4,
            "fines": 5,
            "reports": 6,
            "profile": 7,
            "users": 8,
            "settings": 9
        }
        self.pages.setCurrentIndex(page_index.get(page_key, 0))
        
        # Refresh page data
        current_widget = self.pages.currentWidget()
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
            
    def logout(self):
        # Emit signal to let main.py handle logout
        self.inactivity_timer.stop()
        logger.log_logout(self.user_data['id'], self.user_data['login'])
        self.logout_requested.emit()

    def closeEvent(self, event):
        from src.database import Database
        Database.close_all_connections()
        event.accept()
