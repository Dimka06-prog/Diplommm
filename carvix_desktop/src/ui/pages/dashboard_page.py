from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                             QLabel, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database import Database
from src.styles import get_header_font, get_font
from src.permissions import has_permission, ROLE_DRIVER, ROLE_MECHANIC, PERMISSION_VIEW_DRIVERS, PERMISSION_VIEW_VEHICLES
from datetime import date

class DashboardPage(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Stats cards (role-based)
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)

        card_count = 0
        # Card 1: Total Vehicles (only for non-drivers)
        if has_permission(self.user_data['rol_id'], PERMISSION_VIEW_VEHICLES):
            self.vehicles_card = self.create_stat_card("Всего ТС", "🚗", "#3F3D38")
            stats_layout.addWidget(self.vehicles_card, 0, card_count)
            card_count += 1

        # Card 2: Total Employees (only for non-drivers)
        if has_permission(self.user_data['rol_id'], PERMISSION_VIEW_DRIVERS):
            self.drivers_card = self.create_stat_card("Всего сотрудников", "👤", "#3F3D38")
            stats_layout.addWidget(self.drivers_card, 0, card_count)
            card_count += 1

        # Card 3: Active Vehicles (only for non-drivers)
        if has_permission(self.user_data['rol_id'], PERMISSION_VIEW_VEHICLES):
            self.active_card = self.create_stat_card("Активные ТС", "✅", "#4A7C59")
            stats_layout.addWidget(self.active_card, 0, card_count)
            card_count += 1

        # Card 4: Maintenance Due (only for mechanics and dispatchers)
        if self.user_data['rol_id'] in [ROLE_MECHANIC, 1, 4]:  # mechanic, dispatcher, admin
            self.maintenance_card = self.create_stat_card("Требуется ТО", "🔧", "#e5a00d")
            stats_layout.addWidget(self.maintenance_card, 0, card_count)
            card_count += 1

        # Driver-specific cards
        if self.user_data['rol_id'] == ROLE_DRIVER:
            self.my_schedule_card = self.create_stat_card("Мои смены", "📅", "#3F3D38")
            stats_layout.addWidget(self.my_schedule_card, 0, 0)

            self.my_fines_card = self.create_stat_card("Мои штрафы", "📋", "#e5a00d")
            stats_layout.addWidget(self.my_fines_card, 0, 1)
        
        layout.addLayout(stats_layout)
        
        # Recent activity section
        activity_frame = QFrame()
        activity_frame.setObjectName("card_light")
        activity_layout = QVBoxLayout(activity_frame)
        activity_layout.setContentsMargins(20, 20, 20, 20)
        
        activity_title = QLabel("Последние изменения")
        activity_title.setFont(get_header_font(20))
        activity_title.setStyleSheet("color: #1C1B17;")
        activity_layout.addWidget(activity_title)
        
        self.activity_label = QLabel("Загрузка...")
        self.activity_label.setFont(get_font(13))
        self.activity_label.setStyleSheet("color: #6F6D67;")
        activity_layout.addWidget(self.activity_label)
        
        layout.addWidget(activity_frame)
        
        layout.addStretch()
        
    def create_stat_card(self, title, icon, color):
        card = QFrame()
        card.setObjectName("card_light")
        card.setFixedHeight(140)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon and title row
        header_row = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(get_header_font(32))
        icon_label.setStyleSheet(f"color: {color};")
        
        title_label = QLabel(title)
        title_label.setFont(get_font(13))
        title_label.setStyleSheet("color: #6F6D67;")
        
        header_row.addWidget(icon_label)
        header_row.addStretch()
        header_row.addWidget(title_label)
        
        card_layout.addLayout(header_row)
        
        # Value
        value_label = QLabel("0")
        value_label.setFont(get_header_font(40))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        card_layout.addWidget(value_label)
        
        # Store reference to update later
        card.value_label = value_label
        
        return card
        
    def refresh_data(self):
        try:
            # Get total vehicles (if card exists)
            if hasattr(self, 'vehicles_card'):
                vehicles_query = "SELECT COUNT(*) as count FROM transportnoe_sredstvo"
                vehicles_result = Database.execute_query(vehicles_query)
                if vehicles_result:
                    self.vehicles_card.value_label.setText(str(vehicles_result[0]['count']))

            # Get total employees (if card exists)
            if hasattr(self, 'drivers_card'):
                drivers_query = "SELECT COUNT(*) as count FROM sotrudnik"
                drivers_result = Database.execute_query(drivers_query)
                if drivers_result:
                    self.drivers_card.value_label.setText(str(drivers_result[0]['count']))

            # Get active vehicles (if card exists)
            if hasattr(self, 'active_card'):
                active_query = "SELECT COUNT(*) as count FROM transportnoe_sredstvo WHERE tekuschee_sostoyanie = 'Активно'"
                active_result = Database.execute_query(active_query)
                if active_result:
                    self.active_card.value_label.setText(str(active_result[0]['count']))

            # Get vehicles needing maintenance (if card exists)
            if hasattr(self, 'maintenance_card'):
                maintenance_query = "SELECT COUNT(*) as count FROM transportnoe_sredstvo WHERE to_expiry IS NOT NULL AND to_expiry > CURRENT_DATE AND to_expiry <= CURRENT_DATE + INTERVAL '30 days'"
                maintenance_result = Database.execute_query(maintenance_query)
                if maintenance_result:
                    self.maintenance_card.value_label.setText(str(maintenance_result[0]['count']))

            # Driver-specific: My schedule count
            if hasattr(self, 'my_schedule_card'):
                schedule_query = "SELECT COUNT(*) as count FROM work_schedule WHERE driver_id = %s"
                schedule_result = Database.execute_query(schedule_query, (self.user_data['id'],))
                if schedule_result:
                    self.my_schedule_card.value_label.setText(str(schedule_result[0]['count']))

            # Driver-specific: My fines count
            if hasattr(self, 'my_fines_card'):
                fines_query = """SELECT COUNT(*) as count FROM fines f
                               LEFT JOIN transportnoe_sredstvo t ON f.ts_id = t.id
                               WHERE t.assigned_driver_id = %s AND f.status = 'Не оплачен'"""
                fines_result = Database.execute_query(fines_query, (self.user_data['id'],))
                if fines_result:
                    self.my_fines_card.value_label.setText(str(fines_result[0]['count']))

            # Get recent activity (simplified)
            activity_text = f"Последнее обновление: {date.today().strftime('%d.%m.%Y')}\n"
            activity_text += f"Пользователь: {self.user_data['fio']}"
            self.activity_label.setText(activity_text)

        except Exception as e:
            self.activity_label.setText(f"Ошибка загрузки данных: {str(e)}")
