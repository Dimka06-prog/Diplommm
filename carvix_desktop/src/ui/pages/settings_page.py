from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                             QLabel, QPushButton, QFormLayout, QLineEdit,
                             QMessageBox, QComboBox, QSpinBox, QCheckBox)
from PyQt6.QtCore import Qt
from src.database import Database
from src.styles import get_header_font, get_font
from src.permissions import has_permission, PERMISSION_SYSTEM_SETTINGS
from src.settings_manager import SettingsManager

class SettingsPage(QWidget):
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
        title = QLabel("Настройки")
        title.setFont(get_header_font(28))
        title.setStyleSheet("color: #1C1B17;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # System settings card
        settings_frame = QFrame()
        settings_frame.setObjectName("card_light")
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(30, 30, 30, 30)
        settings_layout.setSpacing(20)

        settings_label = QLabel("Системные настройки")
        settings_label.setFont(get_header_font(18))
        settings_label.setStyleSheet("color: #1C1B17;")
        settings_layout.addWidget(settings_label)

        form_layout = QFormLayout()

        # Company name
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("Название компании")
        self.company_name_input.setMinimumWidth(300)
        form_layout.addRow("Название компании:", self.company_name_input)

        # Maintenance reminder days
        self.maintenance_days_input = QSpinBox()
        self.maintenance_days_input.setRange(1, 365)
        self.maintenance_days_input.setValue(30)
        self.maintenance_days_input.setMinimumWidth(300)
        form_layout.addRow("Напоминание о ТО (дней):", self.maintenance_days_input)

        # Insurance reminder days
        self.insurance_days_input = QSpinBox()
        self.insurance_days_input.setRange(1, 365)
        self.insurance_days_input.setValue(30)
        self.insurance_days_input.setMinimumWidth(300)
        form_layout.addRow("Напоминание о страховке (дней):", self.insurance_days_input)

        # Auto-sync with GIBDD
        self.auto_sync_checkbox = QCheckBox("Автоматическая синхронизация с ГИБДД")
        form_layout.addRow("", self.auto_sync_checkbox)

        settings_layout.addLayout(form_layout)

        save_btn = QPushButton("Сохранить настройки")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_btn)

        layout.addWidget(settings_frame)

        # Database info card
        db_frame = QFrame()
        db_frame.setObjectName("card_light")
        db_layout = QVBoxLayout(db_frame)
        db_layout.setContentsMargins(30, 30, 30, 30)
        db_layout.setSpacing(20)

        db_label = QLabel("Информация о базе данных")
        db_label.setFont(get_header_font(18))
        db_label.setStyleSheet("color: #1C1B17;")
        db_layout.addWidget(db_label)

        self.db_info_label = QLabel("Загрузка...")
        self.db_info_label.setFont(get_font(14))
        self.db_info_label.setStyleSheet("color: #3F3D38;")
        db_layout.addWidget(self.db_info_label)

        refresh_db_btn = QPushButton("Обновить информацию")
        refresh_db_btn.setObjectName("secondary_btn")
        refresh_db_btn.clicked.connect(self.refresh_db_info)
        db_layout.addWidget(refresh_db_btn)

        layout.addWidget(db_frame)

        layout.addStretch()

    def refresh_data(self):
        """Загрузка настроек из базы данных"""
        try:
            # Load settings from database
            company_name = SettingsManager.get_setting('company_name', 'Carvix')
            maintenance_days = SettingsManager.get_setting('maintenance_reminder_days', '30')
            insurance_days = SettingsManager.get_setting('insurance_reminder_days', '30')
            auto_sync = SettingsManager.get_setting('auto_sync_gibdd', 'false')

            # Set values to inputs
            self.company_name_input.setText(company_name)
            self.maintenance_days_input.setValue(int(maintenance_days))
            self.insurance_days_input.setValue(int(insurance_days))
            self.auto_sync_checkbox.setChecked(auto_sync == 'true')

            self.refresh_db_info()
        except Exception as e:
            self.db_info_label.setText(f"Ошибка загрузки настроек: {str(e)}")

    def refresh_db_info(self):
        try:
            # Get database statistics
            vehicles_query = "SELECT COUNT(*) as count FROM transportnoe_sredstvo"
            vehicles_result = Database.execute_query(vehicles_query)

            drivers_query = "SELECT COUNT(*) as count FROM sotrudnik"
            drivers_result = Database.execute_query(drivers_query)

            schedules_query = "SELECT COUNT(*) as count FROM work_schedule"
            schedules_result = Database.execute_query(schedules_query)

            fines_query = "SELECT COUNT(*) as count FROM fines"
            fines_result = Database.execute_query(fines_query)

            info_text = f"Транспортные средства: {vehicles_result[0]['count']}\n"
            info_text += f"Сотрудники: {drivers_result[0]['count']}\n"
            info_text += f"Смены: {schedules_result[0]['count']}\n"
            info_text += f"Штрафы: {fines_result[0]['count']}"

            self.db_info_label.setText(info_text)
        except Exception as e:
            self.db_info_label.setText(f"Ошибка загрузки: {str(e)}")

    def save_settings(self):
        try:
            company_name = self.company_name_input.text().strip()
            maintenance_days = self.maintenance_days_input.value()
            insurance_days = self.insurance_days_input.value()
            auto_sync = self.auto_sync_checkbox.isChecked()

            # Save settings to database
            SettingsManager.set_setting('company_name', company_name)
            SettingsManager.set_setting('maintenance_reminder_days', str(maintenance_days))
            SettingsManager.set_setting('insurance_reminder_days', str(insurance_days))
            SettingsManager.set_setting('auto_sync_gibdd', str(auto_sync).lower())

            QMessageBox.information(self, "Успех",
                f"Настройки сохранены:\n"
                f"Компания: {company_name}\n"
                f"Напоминание о ТО: {maintenance_days} дней\n"
                f"Напоминание о страховке: {insurance_days} дней\n"
                f"Авто-синхронизация: {'Включена' if auto_sync else 'Выключена'}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")
