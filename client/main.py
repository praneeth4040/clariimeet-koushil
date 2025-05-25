import sys
import asyncio
import websockets
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QCoreApplication, QThread, Signal
from PySide6.QtGui import QFont, QColor

class TranscriptWebSocketClient(QThread):
    transcript_received = Signal(str)
    summary_received = Signal(str)
    chatbot_response_received = Signal(str)
    send_chatbot_question_signal = Signal(str)  # NEW SIGNAL
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url
        self._running = True
        self.ws = None
        self.loop = None
        self.send_chatbot_question_signal.connect(self._handle_send_chatbot_question)
    def run(self):
        print(f"[FRONTEND] TranscriptWebSocketClient thread started, connecting to {self.url}")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.listen())
    async def listen(self):
        try:
            async with websockets.connect(self.url) as ws:
                print(f"[FRONTEND] Connected to transcript websocket at {self.url}")
                self.ws = ws
                while self._running:
                    try:
                        msg = await ws.recv()
                        print(f"[FRONTEND] Raw message: {msg}")
                        try:
                            data = json.loads(msg)
                            print(f"[FRONTEND] Decoded JSON: {data}")
                            if data.get("type") == "transcript":
                                print(f"[FRONTEND] Received transcript: {data.get('text', '')}")
                                self.transcript_received.emit(data.get("text", ""))
                            elif data.get("type") == "summary":
                                print(f"[FRONTEND] Received summary: {data.get('text', '')}")
                                self.summary_received.emit(data.get("text", ""))
                            elif data.get("type") == "chatbot_response":
                                print(f"[FRONTEND] Received chatbot response: {data.get('answer', '')}")
                                self.chatbot_response_received.emit(data.get("answer", ""))
                            else:
                                print(f"[FRONTEND] Received non-transcript message: {data}")
                        except Exception as e:
                            print(f"[FRONTEND] JSON decode error: {e}")
                    except Exception as e:
                        print(f"[FRONTEND] Error receiving/parsing message: {e}")
        except Exception as e:
            print(f"[FRONTEND] WebSocket connection error: {e}")
    async def send_chatbot_question(self, question):
        if hasattr(self, 'ws') and self.ws:
            await self.ws.send(json.dumps({"type": "chatbot_question", "question": question}))
    def _handle_send_chatbot_question(self, question):
        if self.loop and self.ws:
            asyncio.run_coroutine_threadsafe(self.send_chatbot_question(question), self.loop)
    def stop(self):
        self._running = False
        print("[FRONTEND] TranscriptWebSocketClient stopping thread.")

class CommandWebSocketClient(QThread):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.loop = asyncio.new_event_loop()
        self.ws = None
        self._connected = False
        self._running = True

    def run(self):
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        try:
            self.ws = await websockets.connect(self.url)
            self._connected = True
            while self._running:
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Command WebSocket error: {e}")
            self._connected = False

    def send_command(self, command):
        if self._connected and self.ws:
            asyncio.run_coroutine_threadsafe(self.ws.send(json.dumps({"type": "command", "command": command})), self.loop)

    def stop(self):
        self._running = False
        if self.ws:
            self.loop.call_soon_threadsafe(self.loop.stop)

class HoverWidget(QMainWindow):
    def __init__(self, title, label_text, on_close=None, is_chatbot=False, is_summary=False):
        super().__init__()
        self.setWindowTitle(title)
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(30, 30, 60, 180))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        if is_chatbot:
            self.setGeometry(150, 150, 390, 370)
        elif is_summary:
            self.setGeometry(180, 180, 390, 370)
        else:
            self.setGeometry(150, 150, 370, 100)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        # Set new color theme: black, white, and grey
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #232323, stop:1 #444444);
                border-radius: 22px;
                border: 2px solid #888;
            }
        """)
        self._drag_active = False
        self._drag_position = None
        self._on_close = on_close
        font = QFont("Segoe UI", 11)
        self.setFont(font)
        if is_chatbot:
            central_widget = QWidget(self)
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            title_label = QLabel("Clarimeet ChatBot", self)
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("color: #e0e0e0; font-size: 20px; font-weight: 600; margin-top: 12px; margin-bottom: 8px; letter-spacing: 0.5px;")
            layout.addWidget(title_label)
            self.chat_display = QTextEdit(self)
            self.chat_display.setReadOnly(True)
            self.chat_display.setStyleSheet("""
                background: #232323;
                color: #e0e0e0;
                border-radius: 10px;
                font-size: 15px;
                padding: 10px;
                border: 1px solid #444;
                margin-bottom: 8px;
            """)
            layout.addWidget(self.chat_display, stretch=1)
            input_row = QHBoxLayout()
            self.input_box = QLineEdit(self)
            self.input_box.setPlaceholderText("Type your message...")
            self.input_box.setStyleSheet("""
                background: #fff;
                color: #232323;
                border-radius: 8px;
                font-size: 15px;
                padding: 7px 12px;
                border: 1px solid #bbb;
                margin-right: 8px;
            """)
            self.input_box.returnPressed.connect(self.print_message)
            send_btn = QPushButton('Send', self)
            send_btn.setStyleSheet("""
                QPushButton {
                    background: #444;
                    color: #fff;
                    border: none;
                    border-radius: 8px;
                    font-size: 15px;
                    padding: 7px 22px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #888;
                }
                QPushButton:pressed {
                    background: #232323;
                }
            """)
            send_btn.clicked.connect(self.print_message)
            input_row.addWidget(self.input_box, stretch=1)
            input_row.addWidget(send_btn)
            layout.addLayout(input_row)
            close_btn = QPushButton('✕', self)
            close_btn.setGeometry(350, 12, 28, 28)
            close_btn.setStyleSheet("""
                QPushButton {
                    background: #fff;
                    color: #232323;
                    border: none;
                    border-radius: 14px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #bbb;
                }
            """)
            close_btn.clicked.connect(self.close)
            close_btn.setParent(self)
            # --- Add websocket client for chatbot ---
            self.ws_client = TranscriptWebSocketClient("ws://localhost:8765", parent=self)
            self.ws_client.chatbot_response_received.connect(self.display_chatbot_response)
            self.ws_client.start()
        elif is_summary:
            central_widget = QWidget(self)
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            tab_row = QHBoxLayout()
            self.summary_tab_btn = QPushButton('Summary', self)
            self.transcript_tab_btn = QPushButton('Live Transcript', self)
            self.summary_tab_btn.setCheckable(True)
            self.transcript_tab_btn.setCheckable(True)
            self.summary_tab_btn.setChecked(True)
            self.summary_tab_btn.setStyleSheet("""
                QPushButton {
                    background: #fff;
                    color: #232323;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: 500;
                    padding: 6px 18px;
                }
                QPushButton:checked {
                    background: #fff;
                    color: #232323;
                }
            """)
            self.transcript_tab_btn.setStyleSheet("""
                QPushButton {
                    background: #888;
                    color: #fff;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: 500;
                    padding: 6px 18px;
                }
                QPushButton:checked {
                    background: #888;
                    color: #fff;
                }
            """)
            self.summary_tab_btn.clicked.connect(self.show_summary_tab)
            self.transcript_tab_btn.clicked.connect(self.show_transcript_tab)
            tab_row.addWidget(self.summary_tab_btn)
            tab_row.addWidget(self.transcript_tab_btn)
            layout.addLayout(tab_row)
            self.summary_panel = QWidget(self)
            summary_layout = QVBoxLayout(self.summary_panel)
            title_label = QLabel("Clarimeet Summary", self)
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("color: #e0e0e0; font-size: 20px; font-weight: 600; margin-top: 12px; margin-bottom: 8px; letter-spacing: 0.5px;")
            summary_layout.addWidget(title_label)
            self.summary_display = QTextEdit(self)
            self.summary_display.setReadOnly(True)
            self.summary_display.setStyleSheet("""
                background: #232323;
                color: #e0e0e0;
                border-radius: 10px;
                font-size: 15px;
                padding: 10px;
                border: 1px solid #444;
                margin-bottom: 8px;
            """)
            self.summary_display.setText("This is a sample summary. You can update this with real data.")
            summary_layout.addWidget(self.summary_display, stretch=1)
            self.summary_panel.setLayout(summary_layout)
            self.transcript_panel = QWidget(self)
            transcript_layout = QVBoxLayout(self.transcript_panel)
            transcript_label = QLabel("Live Transcript", self)
            transcript_label.setAlignment(Qt.AlignCenter)
            transcript_label.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: 500; margin-top: 12px; margin-bottom: 8px; letter-spacing: 0.5px;")
            transcript_layout.addWidget(transcript_label)
            self.transcript_display = QTextEdit(self)
            self.transcript_display.setReadOnly(True)
            self.transcript_display.setStyleSheet("""
                background: #232323;
                color: #e0e0e0;
                border-radius: 10px;
                font-size: 14px;
                padding: 10px;
                border: 1px solid #444;
                margin-bottom: 8px;
            """)
            self.transcript_display.setText("Live transcript will appear here...")
            transcript_layout.addWidget(self.transcript_display, stretch=1)
            self.transcript_panel.setLayout(transcript_layout)
            layout.addWidget(self.summary_panel)
            layout.addWidget(self.transcript_panel)
            self.transcript_panel.hide()
            close_btn = QPushButton('✕', self)
            close_btn.setGeometry(350, 12, 28, 28)
            close_btn.setStyleSheet("""
                QPushButton {
                    background: #fff;
                    color: #232323;
                    border: none;
                    border-radius: 14px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #bbb;
                }
            """)
            close_btn.clicked.connect(self.close)
            close_btn.setParent(self)
            # WebSocket client for live transcript
            self.ws_client = TranscriptWebSocketClient("ws://localhost:8765", parent=self)
            self.ws_client.transcript_received.connect(self.update_transcript)
            self.ws_client.summary_received.connect(self.update_summary)
            self.ws_client.start()

    def update_transcript(self, text):
        # Append the new transcript text instead of replacing
        current = self.transcript_display.toPlainText()
        if current:
            self.transcript_display.setPlainText(current + '\n' + text)
        else:
            self.transcript_display.setPlainText(text)
        print(f"[FRONTEND] Appended transcript: {text}")

    def update_summary(self, text):
        self.summary_display.setPlainText(text)
        print(f"[FRONTEND] Updated summary: {text}")

    def show_summary_tab(self):
        self.summary_tab_btn.setChecked(True)
        self.transcript_tab_btn.setChecked(False)
        self.summary_panel.show()
        self.transcript_panel.hide()

    def show_transcript_tab(self):
        self.summary_tab_btn.setChecked(False)
        self.transcript_tab_btn.setChecked(True)
        self.summary_panel.hide()
        self.transcript_panel.show()

    def print_message(self):
        msg = self.input_box.text()
        if msg.strip():
            self.chat_display.append(f'<span style="color:#6ec1e4;font-weight:bold;">You:</span> <span style="color:#fff;">{msg}</span>')
            # Send to backend chatbot (only if self.ws_client exists)
            if hasattr(self, 'ws_client') and self.ws_client:
                self.ws_client.send_chatbot_question_signal.emit(msg)
            else:
                self.chat_display.append('<span style="color:#f9d923;font-weight:bold;">AI:</span> <span style="color:#fff;">[Error: Chatbot connection not established]</span>')
            self.input_box.clear()

    def display_chatbot_response(self, answer):
        self.chat_display.append(f'<span style="color:#f9d923;font-weight:bold;">AI:</span> <span style="color:#fff;">{answer}</span>')

    def closeEvent(self, event):
        print("[FRONTEND] HoverWidget closeEvent called.")
        if hasattr(self, 'ws_client'):
            self.ws_client.stop()
            self.ws_client.wait()
        if self._on_close:
            self._on_close()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clarimeet Frontend")
        self.setGeometry(100, 100, 370, 140)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #232323, stop:1 #444444);
                border-radius: 16px;
                border: 1px solid #444;
            }
        """)
        self._drag_active = False
        self._drag_position = None
        font = QFont("Segoe UI", 11)
        self.setFont(font)
        close_btn = QPushButton('✕', self)
        close_btn.setGeometry(330, 10, 28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #fff;
                color: #232323;
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #bbb;
            }
        """)
        close_btn.clicked.connect(self.exit_app)
        self.start_btn = QPushButton('Start', self)
        self.start_btn.setGeometry(30, 70, 70, 38)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: #232323;
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #888;
            }
        """)
        self.start_btn.clicked.connect(self.start_clicked)
        self.stop_btn = QPushButton('Stop', self)
        self.stop_btn.setGeometry(110, 70, 70, 38)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #888;
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:enabled:hover {
                background: #232323;
            }
        """)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_clicked)
        self.chatbot_btn = QPushButton('ChatBot', self)
        self.chatbot_btn.setGeometry(190, 70, 80, 38)
        self.chatbot_btn.setStyleSheet("""
            QPushButton {
                background: #444;
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #888;
            }
        """)
        self.chatbot_btn.clicked.connect(self.open_chatbot)
        self.summary_btn = QPushButton('Summary', self)
        self.summary_btn.setGeometry(280, 70, 80, 38)
        self.summary_btn.setStyleSheet("""
            QPushButton {
                background: #444;
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #fff;
                color: #232323;
            }
        """)
        self.summary_btn.clicked.connect(self.open_summary)
        label = QLabel("Clarimeet Hover Widget", self)
        label.setGeometry(30, 20, 300, 36)
        label.setStyleSheet("color: #e0e0e0; font-size: 18px; font-weight: 600; letter-spacing: 0.5px;")
        self.chatbot_widget = None
        self.summary_widget = None
        self.command_ws_client = CommandWebSocketClient("ws://localhost:8765")
        self.command_ws_client.start()

    def start_clicked(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        if hasattr(self, 'command_ws_client'):
            self.command_ws_client.send_command('start')
        # Show a small status message
        self.show_status_message("Transcription started.")

    def stop_clicked(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if hasattr(self, 'command_ws_client'):
            self.command_ws_client.send_command('stop')
        # Show a small status message
        self.show_status_message("Transcription stopped.")

    def show_status_message(self, message):
        # Show a temporary status label at the bottom of the main window
        if hasattr(self, '_status_label') and self._status_label:
            self._status_label.setText(message)
        else:
            self._status_label = QLabel(message, self)
            self._status_label.setGeometry(20, 120, 330, 22)
            self._status_label.setStyleSheet("color: #232323; background: #fff; border-radius: 8px; padding: 4px 12px; font-size: 14px; font-weight: 500;")
            self._status_label.setAlignment(Qt.AlignCenter)
            self._status_label.show()
        QTimer = __import__('PySide6.QtCore').QtCore.QTimer
        QTimer.singleShot(2000, self._status_label.hide)

    def open_chatbot(self):
        if self.chatbot_widget is None or not self.chatbot_widget.isVisible():
            self.chatbot_widget = HoverWidget("ChatBot", "ChatBot Widget", on_close=self.on_chatbot_closed, is_chatbot=True)
            self.chatbot_widget.show()

    def open_summary(self):
        print("[FRONTEND] MainWindow.open_summary called.")
        if self.summary_widget is None or not self.summary_widget.isVisible():
            self.summary_widget = HoverWidget("Summary", "Summary Widget", on_close=self.on_summary_closed, is_summary=True)
            self.summary_widget.show()

    def on_chatbot_closed(self):
        self.chatbot_widget = None

    def on_summary_closed(self):
        self.summary_widget = None

    def exit_app(self):
        if hasattr(self, 'command_ws_client'):
            self.command_ws_client.stop()
            self.command_ws_client.wait()
        QCoreApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
