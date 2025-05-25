import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import subprocess

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clarimeet Dashboard")
        self.setGeometry(200, 200, 500, 320)
        # Remove full screen to restore window controls
        self.showNormal()
        self.dark_mode = True
        self.hover_process = None
        self.setStyleSheet(self.get_stylesheet())
        font = QFont("Segoe UI", 12)
        self.setFont(font)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # Sidebar
        sidebar = QFrame(self)
        sidebar.setFixedWidth(120)  # Reduced width
        sidebar.setFixedHeight(750)  # Decreased height for floating effect
        sidebar.setStyleSheet("""
            background: #181818;
            border-radius: 32px;
            /* Floating effect */
            box-shadow: 0px 8px 32px 0px rgba(0,0,0,0.18);
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignTop)
        sidebar_layout.setContentsMargins(0, 40, 0, 0)
        sidebar_title = QLabel("Clarimeet", self)
        # Always use the sidebar color for the label, regardless of theme
        sidebar_title.setStyleSheet("color: #e0e0e0 !important; font-size: 18px; font-weight: 600; margin: 0 0 30px 0;")
        sidebar_title.setAlignment(Qt.AlignHCenter)
        sidebar_layout.addWidget(sidebar_title)
        self.mode_btn = QPushButton("🌙", self)
        self.mode_btn.setToolTip("Switch to Bright Mode")
        self.mode_btn.setFixedSize(48, 48)
        self.mode_btn.setStyleSheet("""
            QPushButton {
                background: #444;
                color: #fff;
                border: none;
                border-radius: 24px;
                font-size: 26px;
                font-weight: 500;
                margin-bottom: 18px;
                min-width: 48px;
                min-height: 48px;
                max-width: 48px;
                max-height: 48px;
            }
            QPushButton:hover {
                background: #888;
            }
        """)
        self.mode_btn.clicked.connect(self.toggle_mode)
        sidebar_layout.addWidget(self.mode_btn, alignment=Qt.AlignHCenter)
        sidebar_layout.addStretch(1)
        main_layout.addWidget(sidebar)
        # Main content
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Clarimeet Dashboard", self)
        title.setStyleSheet("color: #e0e0e0; font-size: 32px; font-weight: 600; margin-bottom: 24px;")
        title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title)
        desc = QLabel("Welcome to Clarimeet! Launch the hover widget to get started.", self)
        desc.setStyleSheet("color: #bbb; font-size: 18px; margin-bottom: 40px;")
        desc.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(desc)
        self.launch_btn = QPushButton("Launch Hover Widget", self)
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background: #444;
                color: #fff;
                border: none;
                border-radius: 10px;
                font-size: 20px;
                font-weight: 500;
                padding: 16px 48px;
            }
            QPushButton:hover {
                background: #888;
            }
        """)
        self.launch_btn.setFixedWidth(320)
        self.launch_btn.clicked.connect(self.launch_hover)
        content_layout.addWidget(self.launch_btn, alignment=Qt.AlignHCenter)
        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("color: #bbb; font-size: 16px; margin-top: 32px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.status_label)
        main_layout.addWidget(content_widget, stretch=1)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, False)

        # Move sidebar right and down by adding margins to main_layout and sidebar
        main_layout.setContentsMargins(64, 32, 0, 32)  # Left, Top, Right, Bottom

    def get_stylesheet(self):
        if self.dark_mode:
            # Use a solid color background for dark mode
            return """
                QMainWindow {
                    background: #232323;
                    border-radius: 16px;
                    border: 1px solid #444;
                }
            """
        else:
            return """
                QMainWindow { background: #f5f5f5; border-radius: 16px; border: 1px solid #bbb; }
                QLabel { color: #232323; }
            """

    def get_dark_bg_path(self):
        import os
        # Save the image as 'dark_bg.jpg' in the client folder or use the path as needed
        return os.path.abspath(os.path.join(os.path.dirname(__file__), 'dark_bg.jpg')).replace('\\', '/')

    def toggle_mode(self):
        self.dark_mode = not self.dark_mode
        self.setStyleSheet(self.get_stylesheet())
        if self.dark_mode:
            self.mode_btn.setText("🌙")
            self.mode_btn.setToolTip("Switch to Bright Mode")
            self.mode_btn.setStyleSheet("""
                QPushButton { background: #444; color: #fff; border: none; border-radius: 24px; font-size: 26px; font-weight: 500; margin-bottom: 18px; min-width: 48px; min-height: 48px; max-width: 48px; max-height: 48px; }
                QPushButton:hover { background: #888; }
            """)
            # Set all text to white
            self.set_text_color("#e0e0e0")
        else:
            self.mode_btn.setText("☀️")
            self.mode_btn.setToolTip("Switch to Dark Mode")
            self.mode_btn.setStyleSheet("""
                QPushButton { background: #eee; color: #232323; border: none; border-radius: 24px; font-size: 26px; font-weight: 500; margin-bottom: 18px; min-width: 48px; min-height: 48px; max-width: 48px; max-height: 48px; }
                QPushButton:hover { background: #bbb; }
            """)
            # Set all text to black
            self.set_text_color("#232323")

    def set_text_color(self, color):
        # Sidebar title should always be #e0e0e0
        sidebar_title = self.findChildren(QLabel)[0]
        sidebar_title.setStyleSheet("color: #e0e0e0 !important; font-size: 18px; font-weight: 600; margin: 0 0 30px 0;")
        # Main title and other labels
        for widget in self.findChildren(QLabel):
            if widget.text() == "Clarimeet Dashboard":
                widget.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 600; margin-bottom: 24px;")
            elif widget.text().startswith("Welcome to Clarimeet"):
                widget.setStyleSheet(f"color: {color if color == '#232323' else '#bbb'}; font-size: 18px; margin-bottom: 40px;")
            elif widget is self.status_label:
                widget.setStyleSheet(f"color: #bbb; font-size: 16px; margin-top: 32px;")

    def launch_hover(self):
        # Only allow one hover widget at a time
        if self.hover_process is not None and self.hover_process.poll() is None:
            self.status_label.setText("Hover widget is already running.")
            return
        try:
            import os
            hover_path = os.path.join(os.path.dirname(__file__), "main.py")
            self.hover_process = subprocess.Popen([sys.executable, hover_path])
            self.status_label.setText("Hover widget launched!")
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def closeEvent(self, event):
        # Optionally terminate the hover widget when dashboard closes
        if self.hover_process is not None and self.hover_process.poll() is None:
            self.hover_process.terminate()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())
