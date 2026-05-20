import sys
from PyQt6.QtWidgets import QApplication
from src.auth.auth_dialog import AuthDialog
from src.ui.main_window import MainWindow
from src.styles import apply_stylesheet

class CarvixApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.apply_styles()
        self.show_auth_dialog()
        
    def apply_styles(self):
        apply_stylesheet(self)
        
    def show_auth_dialog(self):
        self.auth_dialog = AuthDialog()
        self.auth_dialog.authenticated.connect(self.on_authenticated)
        self.auth_dialog.show()
        
    def on_authenticated(self, user_data):
        self.auth_dialog.close()
        self.main_window = MainWindow(user_data)
        self.main_window.show()
        
    def show_auth_dialog(self):
        self.auth_dialog = AuthDialog()
        self.auth_dialog.authenticated.connect(self.on_authenticated)
        self.auth_dialog.show()

if __name__ == '__main__':
    app = CarvixApp()
    sys.exit(app.exec())
