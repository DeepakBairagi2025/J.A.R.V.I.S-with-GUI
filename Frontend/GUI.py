from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget,QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QDialog, QScrollArea, QSpacerItem
from PyQt5.QtGui import QIcon, QPainter, QColor, QMovie, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QTimer, QSize
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"
DataDirPath = rf"{current_dir}\Data"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):

    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"

    else:
        if query_words[-1][-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding="utf-8") as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding="utf-8") as file:
        status = file.read()
    return status

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding="utf-8") as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding="utf-8") as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    Path = rf"{GraphicsDirPath}\{Filename}"
    return Path

def TempDirectoryPath(Filename):
    Path = rf"{TempDirPath}\{Filename}"
    return Path

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding="utf-8") as file:
        file.write(Text)

# ------------- Web Links Persistence Helpers -------------
def _links_file_path():
    try:
        os.makedirs(DataDirPath, exist_ok=True)
    except Exception:
        pass
    return os.path.join(DataDirPath, 'WebLinks.json')

def LoadWebLinks():
    import json
    path = _links_file_path()
    if not os.path.exists(path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('[]')
        except Exception:
            return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []

def SaveWebLinks(items: list):
    import json
    path = _links_file_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# Resolve images whether they are kept at the project root or inside Frontend/Graphics
def ResourcePath(filename: str) -> str:
    root_path = os.path.join(current_dir, filename)
    if os.path.exists(root_path):
        return root_path
    gfx_path = os.path.join(GraphicsDirPath, filename)
    return gfx_path

# Seed Data/WebLinks.json by parsing Backend/AUTOMATION/Automation.py website_keywords
def SeedLinksFromAutomationIfEmpty():
    items = LoadWebLinks()
    if items:
        return False
    try:
        auto_path = os.path.join(current_dir, 'Backend', 'AUTOMATION', 'Automation.py')
        if not os.path.exists(auto_path):
            return False
        with open(auto_path, 'r', encoding='utf-8') as f:
            src = f.read()
        # Locate the website_keywords dict block
        start = src.find('website_keywords = {')
        if start == -1:
            return False
        end = src.find('\n    }', start)
        if end == -1:
            end = src.find('\n}', start)
        block = src[start:end]
        # Extract 'key': 'url' pairs with simple parsing
        import re as _re
        pairs = _re.findall(r"['\"]([^'\"]+)['\"]\s*:\s*['\"](https?://[^'\"]+)['\"]", block)
        seen = set()
        result = []
        for k, u in pairs:
            k_low = k.strip().lower()
            if '.' in k_low or k_low in seen:
                continue
            seen.add(k_low)
            result.append({'name': k_low, 'url': u})
        if result:
            SaveWebLinks(result)
            return True
    except Exception:
        return False
    return False

class ChatSection(QWidget):

    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction) # No text interaction
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        
        # Create bottom section for GIF and status
        bottom_layout = QHBoxLayout()
        
        # Add stretch to push GIF to right
        bottom_layout.addStretch()
        
        # Create right section for GIF and status text
        right_section = QVBoxLayout()
        
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        self.gif_label.setFixedSize(260, 190)  # Fixed size to ensure visibility
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))  # Fixed typo: "Jarivs" -> "Jarvis"
        if movie.isValid():
            max_gif_size_W = 270
            max_gif_size_H = 200
            movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
            self.gif_label.setAlignment(Qt.AlignCenter)
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            self.gif_label.setText("GIF not found")
            self.gif_label.setStyleSheet("color: white; border: 1px solid red;")
        
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; border: none;")
        self.label.setAlignment(Qt.AlignCenter)
        
        right_section.addWidget(self.label)
        right_section.addWidget(self.gif_label)
        bottom_layout.addLayout(right_section)
        
        layout.addLayout(bottom_layout)
        
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        # One-time previous chat history load flag
        self._history_loaded = False
        # Ensure temp files exist to avoid first-run errors
        try:
            os.makedirs(TempDirPath, exist_ok=True)
            resp_path = TempDirectoryPath('Responses.data')
            if not os.path.exists(resp_path):
                with open(resp_path, 'w', encoding='utf-8') as f:
                    f.write("")
            status_path = TempDirectoryPath('Status.data')
            if not os.path.exists(status_path):
                with open(status_path, 'w', encoding='utf-8') as f:
                    f.write("")
        except Exception:
            pass

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
                QScrollBar:vertical{
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
                }          

                QScrollBar::handle:vertical{
                background: white;
                min-height: 20px;
                }

                QScrollBar::add-line:vertical{
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px
                } 
                
                QScrollBar::sub-line:vertical{
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
                }

                QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
                border: none;
                color: none;
                }
                
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{
                background: none;
                }
        """)

    def loadMessages(self):

        global old_chat_message

        # Lazy-load previous history once when the chat screen starts up
        if not self._history_loaded:
            self._history_loaded = True
            try:
                data_dir = os.path.join(current_dir, 'Data')
                chatlog_path = os.path.join(data_dir, 'ChatLog.json')
                if os.path.exists(chatlog_path):
                    import json
                    with open(chatlog_path, 'r', encoding='utf-8') as jf:
                        logs = json.load(jf)
                        # Render previous messages
                        for item in logs:
                            role = str(item.get('role', '')).lower().strip()
                            content = str(item.get('content', '')).strip()
                            if not content:
                                continue
                            # Color per role (user: cyan, assistant: white)
                            if role == 'user':
                                self.addMessage(message=f"You: {content}", color='Cyan')
                            elif role == 'assistant':
                                self.addMessage(message=f"{Assistantname or 'Assistant'}: {AnswerModifier(content)}", color='White')
                            else:
                                self.addMessage(message=content, color='White')
                        # Set old_chat_message to the last line in Responses to avoid immediate duplicate append
                        try:
                            with open(TempDirectoryPath('Responses.data'), 'r', encoding='utf-8') as rf:
                                old_chat_message = rf.read()
                        except Exception:
                            pass
            except Exception:
                pass

        with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
            messages = file.read()

            if None==messages:
                pass

            elif len(messages)<=1:
                pass
            
            elif str(old_chat_message)==str(messages):
                pass

            else:
                self.addMessage(message=messages, color='White')
                old_chat_message = messages

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):

        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
            MicButtonInitialed()

        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):

        def __init__(self, parent=None):
            super().__init__(parent)
            desktop = QApplication.desktop()
            screen_width = desktop.screenGeometry().width()
            screen_height = desktop.screenGeometry().height()
            content_layout = QVBoxLayout()
            content_layout.setContentsMargins(0, 0, 0, 0)
            gif_label = QLabel()
            movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
            gif_label.setMovie(movie)
            max_gif_size_W = 870
            max_gif_size_H = 670
            movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
            gif_label.setAlignment(Qt.AlignCenter)
            movie.start()
            gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # Mic button (left of center)
            self.icon_label = QLabel()
            mic_pix = QPixmap(GraphicsDirectoryPath('Mic_on.png')).scaled(60, 60)
            self.icon_label.setPixmap(mic_pix)
            self.icon_label.setFixedSize(90, 90)
            self.icon_label.setAlignment(Qt.AlignCenter)
            self.toggled = True
            self.toggle_icon()
            self.icon_label.mousePressEvent = self.toggle_icon
            # Web button (right of mic), opens pop menu
            self.web_button = QPushButton()
            self.web_button.setIcon(QIcon(ResourcePath('web.png')))
            self.web_button.setIconSize(QSize(60, 60))
            self.web_button.setFixedSize(90, 90)
            self.web_button.setFlat(True)
            self.web_button.setStyleSheet("border: none;")
            self.web_button.clicked.connect(self.openWebLinksPopover)
            self.label = QLabel("")
            self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
            content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
            content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
            # Centered row with Mic and Web buttons, slight spacing, still centered
            btn_row = QHBoxLayout()
            btn_row.addStretch(1)
            btn_row.addWidget(self.icon_label, alignment=Qt.AlignRight)
            btn_row.addSpacing(20)
            btn_row.addWidget(self.web_button, alignment=Qt.AlignLeft)
            btn_row.addStretch(1)
            content_layout.addLayout(btn_row)
            content_layout.setContentsMargins(0, 0, 0, 150)
            self.setLayout(content_layout)
            self.setFixedHeight(screen_height)
            self.setFixedWidth(screen_width)
            self.setStyleSheet("background-color: black;")
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.SpeechRecogText)
            self.timer.start(5)

        def openWebLinksPopover(self):
            dlg = WebLinksManagerDialog(self)
            dlg.setAttribute(Qt.WA_DeleteOnClose, True)
            dlg.exec_()

        def SpeechRecogText(self):
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)

        def load_icon(self, path, width=60, height=60):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)

        def toggle_icon(self, event=None):

            if self.toggled:
                self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
                MicButtonInitialed()

            else:
                self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
                MicButtonClosed()

            self.toggled = not self.toggled

class MessageScreen(QWidget):

        def __init__(self, parent=None):
            super().__init__(parent)
            desktop = QApplication.desktop()
            screen_width = desktop.screenGeometry().width()
            screen_height = desktop.screenGeometry().height()
            layout = QVBoxLayout()
            label = QLabel("")
            layout.addWidget(label)
            chat_section = ChatSection()
            layout.addWidget(chat_section)
            self.setLayout(layout)
            self.setStyleSheet('background-color: black;')
            self.setFixedHeight(screen_height)
            self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):

        def __init__(self, parent, stacked_widget):
            super().__init__(parent)
            self.initUI()
            self.current_screen = None
            self.stacked_widget = stacked_widget

        def initUI(self):
            self.setFixedHeight(50)
            layout = QHBoxLayout(self)
            layout.setAlignment(Qt.AlignRight)
            home_button = QPushButton()
            home_icon = QIcon(GraphicsDirectoryPath('Home.png'))
            home_button.setIcon(home_icon)
            home_button.setText( "Home")
            home_button.setStyleSheet("height: 40px;line-height: 40px; background-color: white; color: black;")
            message_button = QPushButton()
            message_icon = QIcon(GraphicsDirectoryPath('Chats.png'))
            message_button.setIcon(message_icon)
            message_button.setText(" Chat")
            message_button.setStyleSheet("height: 40px; line-height: 40px; background-color: white; color: black;")
            minimize_button = QPushButton()
            minimize_icon = QIcon(GraphicsDirectoryPath('Minimize2.png'))
            minimize_button.setIcon(minimize_icon)
            minimize_button.setText(" Minimize")
            minimize_button.setStyleSheet("background-color: white;")
            minimize_button.clicked.connect(self.minimizeWindow)
            self.maximize_button = QPushButton()
            self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
            self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
            self.maximize_button.setIcon(self.maximize_icon)
            self.maximize_button.setFlat(True)
            self.maximize_button.setStyleSheet("background-color: white;")
            self.maximize_button.clicked.connect(self.maximizeWindow)
            close_button = QPushButton()
            close_icon = QIcon(GraphicsDirectoryPath('Close.png'))
            close_button.setIcon(close_icon)
            close_button.setStyleSheet("background-color: white;")
            close_button.clicked.connect(self.closeWindow)
            line_frame = QFrame()
            line_frame.setFixedHeight(1)
            line_frame.setFrameShape(QFrame.HLine)
            line_frame.setFrameShadow(QFrame.Sunken)
            line_frame.setStyleSheet("border-color: black;")
            title_label = QLabel(f" {str(Assistantname).capitalize()} AI")
            title_label.setStyleSheet("background-color: white; color: black; font-size: 18px;")
            home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
            message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
            layout.addWidget(title_label)
            layout.addStretch(1)
            layout.addWidget(home_button)
            layout.addWidget(message_button)
            layout.addStretch(1)
            layout.addWidget(minimize_button)
            layout.addWidget(self.maximize_button)
            layout.addWidget(close_button)
            layout.addWidget(line_frame)
            self.draggable = True
            self.offset = None

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.fillRect(self.rect(), Qt.white)
            super().paintEvent(event)

        def minimizeWindow(self):
            self.parent().showMinimized()

        def maximizeWindow(self):
            if self.parent().isMaximized():
                self.parent().showNormal()
                self.maximize_button.setIcon(self.maximize_icon)
            else:
                self.parent().showMaximized()
                self.maximize_button.setIcon(self.restore_icon)

        def closeWindow(self):
            self.parent().close()

        def mousePressEvent(self, event):
            if self.draggable:
                self.offset = event.pos()

        def mouseMoveEvent(self, event):
            if self.draggable and self.offset:
                new_pos = event.globalPos() - self.offset
                self.parent().move(new_pos)

        def showMessageScreen(self):
            if self.current_screen is not None:
                self.current_screen.hide()

            message_screen = MessageScreen(self)
            layout = self.parent().layout()
            if layout is not None:
                layout.addWidget(message_screen)
            self.current_screen = message_screen

        def showInitialScreen(self):
            if self.current_screen is not None:
                self.current_screen.hide()

            initial_screen = InitialScreen(self)
            layout = self.parent().layout()
            if layout is not None:
                layout.addWidget(initial_screen)
            self.current_screen = initial_screen

class MainWindow(QMainWindow):

        def __init__(self):
            super().__init__()
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.initUI()

        def initUI(self):
            desktop = QApplication.desktop()
            screen_width = desktop.screenGeometry().width()
            screen_height = desktop.screenGeometry().height()
            stacked_widget = QStackedWidget(self)
            initial_screen = InitialScreen()
            message_screen = MessageScreen()
            stacked_widget.addWidget(initial_screen)
            stacked_widget.addWidget(message_screen)
            self.setGeometry(0, 0, screen_width, screen_height)
            self.setStyleSheet("background-color: black;")
            top_bar = CustomTopBar(self, stacked_widget)
            self.setMenuWidget(top_bar)
            self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# ------------- Pop Menus: Web Links Manager, Add Link, Confirm Delete -------------
class TitleBar(QWidget):
    def __init__(self, parent_dialog: QDialog, title: str):
        super().__init__(parent_dialog)
        self.parent_dialog = parent_dialog
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)
        ttl = QLabel(title)
        ttl.setStyleSheet("color: white; font-size: 16px;")
        lay.addWidget(ttl)
        lay.addStretch(1)
        btn_min = QPushButton()
        btn_min.setIcon(QIcon(ResourcePath('—Pngtree—minus vector icon_4015246.png')))
        btn_min.setIconSize(QSize(16, 16))
        btn_min.setFixedSize(28, 22)
        # Make minimize button background white for visibility
        btn_min.setStyleSheet("background: white; border: none;")
        btn_min.clicked.connect(self.minimize)
        btn_close = QPushButton()
        btn_close.setIcon(QIcon(ResourcePath('Close.png')))
        btn_close.setIconSize(QSize(16, 16))
        btn_close.setFixedSize(28, 22)
        btn_close.setStyleSheet("background: transparent; border: none;")
        btn_close.clicked.connect(self.close)
        lay.addWidget(btn_min)
        lay.addWidget(btn_close)
        self.setStyleSheet("background-color: black;")

    def minimize(self):
        self.parent_dialog.showMinimized()

    def close(self):
        self.parent_dialog.close()

class WebLinksManagerDialog(QDialog):

    def _hline(self):
        l = QFrame()
        l.setFrameShape(QFrame.HLine)
        l.setFixedHeight(1)
        l.setStyleSheet("background: white;")
        return l

    def _vline(self):
        l = QFrame()
        l.setFrameShape(QFrame.VLine)
        l.setFixedWidth(1)
        l.setStyleSheet("background: white;")
        return l

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        self.resize(780, 520)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        # Title bar
        root.addWidget(TitleBar(self, "Web Links"))
        # Header controls
        header = QHBoxLayout()
        add_btn = QPushButton("Add link")
        add_btn.setStyleSheet("background: #FFD700; color: black; padding: 6px 12px; font-weight: bold;")
        add_btn.clicked.connect(self.openAdd)
        header.addWidget(add_btn)
        header.addStretch(1)
        root.addLayout(header)
        # Column headers (no boxes, just separators like a table)
        header_row = QHBoxLayout()
        header_row.setContentsMargins(10, 6, 10, 6)
        name_hdr = QLabel("Web name")
        url_hdr  = QLabel("URL link")
        name_hdr.setStyleSheet("color: #FF69B4; font-size: 20px;")
        url_hdr.setStyleSheet("color: #32CD32; font-size: 20px;")
        header_row.addWidget(name_hdr, 3)
        header_row.addWidget(self._vline())
        header_row.addWidget(url_hdr, 6)
        header_row.addWidget(self._vline())
        header_row.addWidget(QLabel(""), 1)
        header_row.addWidget(self._vline())
        header_row.addWidget(self._vline())
        header_container = QVBoxLayout()
        header_container.setContentsMargins(0,0,0,0)
        top_widget = QWidget()
        top_widget.setLayout(header_row)
        header_container.addWidget(self._hline())
        header_container.addWidget(top_widget)
        header_container.addWidget(self._hline())
        hc = QWidget()
        hc.setLayout(header_container)
        root.addWidget(hc)
        # Scroll area list
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.scroll.setWidget(self.list_container)
        root.addWidget(self.scroll)
        # Ensure JSON seeded from Automation if empty
        SeedLinksFromAutomationIfEmpty()
        self.reload()

    def reload(self):
        # Clear existing rows
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        links = LoadWebLinks()
        if not links:
            # Try again after seeding
            if SeedLinksFromAutomationIfEmpty():
                links = LoadWebLinks()
            if not links:
                empty = QLabel("No links yet")
                empty.setStyleSheet("color: white;")
                self.list_layout.addWidget(empty)
                return
        for it in links:
            # Row content
            row = QHBoxLayout()
            row.setContentsMargins(10, 6, 10, 6)
            name = str(it.get('name', '')).strip()
            url = str(it.get('url', '')).strip()
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("color: #FF69B4; font-size: 18px;")
            url_lbl = QLabel(url)
            url_lbl.setStyleSheet("color: #32CD32; font-size: 18px;")
            del_btn = QPushButton()
            del_btn.setIcon(QIcon(ResourcePath('delete.png')))
            del_btn.setIconSize(QSize(28, 28))
            del_btn.setFixedSize(36, 32)
            del_btn.setStyleSheet("border: none; background: transparent;")
            del_btn.clicked.connect(lambda _, u=url: self.confirmDelete(u))

            row.addWidget(name_lbl, 3)
            row.addWidget(self._vline())
            row.addWidget(url_lbl, 6)
            row.addWidget(self._vline())
            row.addWidget(del_btn, 1)
            row.addWidget(self._vline())
            row.addWidget(self._vline())

            rc = QVBoxLayout()
            rc.setContentsMargins(0,0,0,0)
            rw = QWidget()
            rw.setLayout(row)
            rc.addWidget(rw)
            rc.addWidget(self._hline())
            rcontainer = QWidget()
            rcontainer.setLayout(rc)
            self.list_layout.addWidget(rcontainer)
        self.list_layout.addStretch(1)

    def openAdd(self):
        dlg = AddLinkDialog(self)
        dlg.setAttribute(Qt.WA_DeleteOnClose, True)
        if dlg.exec_() == QDialog.Accepted:
            self.reload()

    def confirmDelete(self, url: str):
        dlg = ConfirmDeleteDialog(url, self)
        dlg.setAttribute(Qt.WA_DeleteOnClose, True)
        if dlg.exec_() == QDialog.Accepted:
            self.reload()

class AddLinkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        self.resize(520, 260)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(TitleBar(self, "Add link"))
        body = QVBoxLayout()
        body.setContentsMargins(18, 12, 18, 12)
        name_lbl = QLabel("Enter web name")
        name_lbl.setStyleSheet("color: black;")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter web name")
        self.name_edit.setStyleSheet("color: black; border: 1px solid black; padding: 6px; background: white;")
        url_lbl = QLabel("Enter URL")
        url_lbl.setStyleSheet("color: black;")
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Enter URL")
        self.url_edit.setStyleSheet("color: black; border: 1px solid black; padding: 6px; background: white;")
        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet("color: #ff8080;")
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("background: #FF4D4D; color: white; padding: 6px 14px; font-weight: bold;")
        save_btn.clicked.connect(self.onSave)
        btn_row.addWidget(save_btn)
        body.addWidget(name_lbl)
        body.addWidget(self.name_edit)
        body.addSpacing(6)
        body.addWidget(url_lbl)
        body.addWidget(self.url_edit)
        body.addSpacing(8)
        body.addWidget(self.err_lbl)
        body.addLayout(btn_row)
        root.addLayout(body)

    def onSave(self):
        name = (self.name_edit.text() or '').strip()
        url = (self.url_edit.text() or '').strip()
        if not name or not url:
            self.err_lbl.setText("Please enter name and URL")
            return
        if not (url.startswith('http://') or url.startswith('https://')):
            self.err_lbl.setText("URL must start with http:// or https://")
            return
        items = LoadWebLinks()
        # unique name
        for it in items:
            if str(it.get('name', '')).strip().lower() == name.lower():
                self.err_lbl.setText("Name already exists")
                return
        items.append({'name': name, 'url': url})
        if SaveWebLinks(items):
            self.accept()
        else:
            self.err_lbl.setText("Failed to save. Try again")

class ConfirmDeleteDialog(QDialog):
    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        self.resize(520, 220)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(TitleBar(self, "Warning"))
        body = QVBoxLayout()
        body.setContentsMargins(18, 12, 18, 12)
        msg = QLabel("Are you sure you want to delete this URL?")
        msg.setStyleSheet("color: black; font-size: 14px;")
        url_lbl = QLabel(url)
        url_lbl.setStyleSheet("color: #32CD32; font-size: 13px;")  # green
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("background: #FF4D4D; color: white; padding: 6px 14px; font-weight: bold;")
        del_btn.clicked.connect(self.onDelete)
        btn_row.addWidget(del_btn)
        body.addWidget(msg)
        body.addSpacing(6)
        body.addWidget(url_lbl)
        body.addSpacing(12)
        body.addLayout(btn_row)
        root.addLayout(body)

    def onDelete(self):
        items = LoadWebLinks()
        new_items = [it for it in items if str(it.get('url', '')).strip() != self.url]
        if SaveWebLinks(new_items):
            self.accept()
        else:
            # leave dialog open; optional error label could be added
            pass