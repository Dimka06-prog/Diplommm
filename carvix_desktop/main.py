import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from src.auth.auth_dialog import AuthDialog
from src.ui.main_window import MainWindow
from src.styles import apply_stylesheet

class SplashScreen(QWidget):
    """Экран загрузки приложения"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Carvix")
        title.setFont(QFont('Georgia', 48, QFont.Weight.Bold))
        title.setStyleSheet("color: #1C1B17;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Загрузка...")
        subtitle.setFont(QFont('Arial', 14))
        subtitle.setStyleSheet("color: #6F6D67; margin-top: 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        self.setStyleSheet("background: #FBF8F3; border-radius: 24px;")

class CarvixApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.apply_styles()
        self.main_window = None
        self.splash = SplashScreen()
        self.splash.show()
        # Defer auth dialog to allow splash to render
        QTimer.singleShot(500, self.show_auth_dialog)

    def apply_styles(self):
        apply_stylesheet(self)

    def show_auth_dialog(self):
        self.auth_dialog = AuthDialog()
        self.auth_dialog.authenticated.connect(self.on_authenticated)
        self.auth_dialog.exit_app.connect(self.on_exit_app)
        self.splash.close()
        self.auth_dialog.show()

    def on_authenticated(self, user_data):
        self.auth_dialog.hide()
        self.main_window = MainWindow(user_data)
        self.main_window.logout_requested.connect(self.on_logout)
        self.main_window.show()

    def on_logout(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        self.show_auth_dialog()

    def on_exit_app(self):
        self.quit()

if __name__ == '__main__':
    app = CarvixApp()
    sys.exit(app.exec())
