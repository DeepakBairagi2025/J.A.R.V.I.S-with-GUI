"""
Vegamovies Popup GUI - Display movie gallery with auto-slideshow
Shows movie posters and details with 7-second intervals
"""

import sys
import time
import threading
from pathlib import Path
from typing import List, Dict, Any
import requests
from io import BytesIO

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    print("PyQt5 not found, trying PyQt6...")
    try:
        from PyQt6.QtWidgets import *
        from PyQt6.QtCore import *
        from PyQt6.QtGui import *
    except ImportError:
        print("Neither PyQt5 nor PyQt6 found. Please install one of them.")
        sys.exit(1)

# Get project root for resource paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]

class MovieCard(QWidget):
    """Individual movie card widget"""
    
    def __init__(self, movie_data: Dict[str, Any]):
        super().__init__()
        self.movie_data = movie_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the movie card UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Movie poster
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(300, 450)
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.poster_label.setStyleSheet("""
            QLabel {
                border: 2px solid #FF69B4;
                border-radius: 10px;
                background-color: #1a1a1a;
                color: white;
            }
        """)
        
        # Load poster image
        self.load_poster_image()
        
        # Movie details container
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(8)
        
        # Title
        title = self.movie_data.get('title', 'Unknown Title')
        # Clean title (remove "Download" prefix and file info)
        clean_title = title.replace('Download ', '').split(' (')[0].split(' WEB-DL')[0].split(' 480p')[0]
        
        title_label = QLabel(clean_title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            QLabel {
                color: #FF69B4;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        
        # Year
        year = self.movie_data.get('year', 'Unknown Year')
        if not year or year == 'Unknown Year':
            # Try to extract year from title
            import re
            year_match = re.search(r'\((\d{4})\)', title)
            if year_match:
                year = year_match.group(1)
            else:
                year = '2025'  # Default to current year
        
        year_label = QLabel(f"Year: {year}")
        year_label.setStyleSheet("color: #32CD32; font-size: 14px;")
        
        # Genre
        genre = self.movie_data.get('genre', 'Action/Drama')
        if not genre:
            genre = 'Action/Drama'  # Default genre
        
        genre_label = QLabel(f"Genre: {genre}")
        genre_label.setStyleSheet("color: #87CEEB; font-size: 14px;")
        
        # Quality
        quality = self.movie_data.get('quality', '')
        if not quality:
            # Extract quality from title
            if '1080p' in title:
                quality = '1080p HD'
            elif '720p' in title:
                quality = '720p HD'
            elif '480p' in title:
                quality = '480p'
            else:
                quality = 'HD'
        
        quality_label = QLabel(f"Quality: {quality}")
        quality_label.setStyleSheet("color: #FFD700; font-size: 14px;")
        
        # Source info
        source_info = "Vegamovies.menu"
        source_label = QLabel(f"Source: {source_info}")
        source_label.setStyleSheet("color: #FFA500; font-size: 12px;")
        
        # Add all details to layout
        details_layout.addWidget(title_label)
        details_layout.addWidget(year_label)
        details_layout.addWidget(genre_label)
        details_layout.addWidget(quality_label)
        details_layout.addWidget(source_label)
        details_layout.addStretch()
        
        # Add poster and details to main layout
        layout.addWidget(self.poster_label)
        layout.addWidget(details_widget)
        
        self.setLayout(layout)
    
    def load_poster_image(self):
        """Load poster image from URL"""
        try:
            image_url = self.movie_data.get('image_url', '')
            print(f"[MovieCard] Loading image from: {image_url}")
            
            if image_url and image_url.startswith('http'):
                # Download image with headers to avoid blocking
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                print(f"[MovieCard] Downloading image...")
                response = requests.get(image_url, timeout=15, headers=headers, stream=True)
                
                if response.status_code == 200:
                    print(f"[MovieCard] Image downloaded successfully, size: {len(response.content)} bytes")
                    
                    # Load image from bytes
                    pixmap = QPixmap()
                    success = pixmap.loadFromData(response.content)
                    
                    if success and not pixmap.isNull():
                        print(f"[MovieCard] Image loaded successfully: {pixmap.width()}x{pixmap.height()}")
                        
                        # Scale image to fit label
                        scaled_pixmap = pixmap.scaled(
                            280, 420, 
                            Qt.AspectRatioMode.KeepAspectRatio, 
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.poster_label.setPixmap(scaled_pixmap)
                        print(f"[MovieCard] Image displayed successfully")
                        return
                    else:
                        print(f"[MovieCard] Failed to load image data into QPixmap")
                else:
                    print(f"[MovieCard] Failed to download image: HTTP {response.status_code}")
            else:
                print(f"[MovieCard] Invalid or missing image URL")
            
            # Fallback: show placeholder
            self.show_placeholder_image()
            
        except Exception as e:
            print(f"[MovieCard] Error loading image: {e}")
            import traceback
            traceback.print_exc()
            self.show_placeholder_image()
    
    def show_placeholder_image(self):
        """Show placeholder when image can't be loaded"""
        # Create a simple placeholder
        pixmap = QPixmap(280, 420)
        pixmap.fill(QColor(40, 40, 40))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 105, 180))  # Pink color
        painter.setFont(QFont("Arial", 16))
        
        # Draw movie icon
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🎬\nMOVIE\nPOSTER")
        painter.end()
        
        self.poster_label.setPixmap(pixmap)

class VegamoviesPopup(QDialog):
    """Main popup window for Vegamovies movie gallery"""
    
    def __init__(self, movies: List[Dict[str, Any]], title: str = "Vegamovies Movies"):
        super().__init__()
        self.movies = movies
        self.current_index = 0
        self.slideshow_timer = None
        self.slideshow_active = True
        self.popup_title = title
        
        # Add auto-close timer (30 seconds)
        self.auto_close_timer = QTimer()
        self.auto_close_timer.timeout.connect(self.close)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.start(30000)  # 30 seconds
        
        self.setup_ui()
        self.start_slideshow()
    
    def setup_ui(self):
        """Setup the popup UI"""
        self.setWindowTitle(self.popup_title)
        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                border: 2px solid #FF69B4;
                border-radius: 10px;
            }
        """)
        
        # Center the window
        self.center_window()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title bar
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)
        
        # Movie display area
        self.movie_container = QWidget()
        self.movie_layout = QHBoxLayout(self.movie_container)
        self.movie_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create movie cards
        self.movie_cards = []
        for movie in self.movies:
            card = MovieCard(movie)
            self.movie_cards.append(card)
            card.hide()  # Hide all cards initially
        
        # Show first card
        if self.movie_cards:
            self.movie_layout.addWidget(self.movie_cards[0])
            self.movie_cards[0].show()
        
        main_layout.addWidget(self.movie_container)
        
        # Control bar
        control_bar = self.create_control_bar()
        main_layout.addWidget(control_bar)
        
        self.setLayout(main_layout)
    
    def create_title_bar(self):
        """Create title bar with movie counter"""
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        # Title
        title_label = QLabel(self.popup_title)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        # Counter
        self.counter_label = QLabel(f"1 / {len(self.movies)}")
        self.counter_label.setStyleSheet("""
            QLabel {
                color: #FF69B4;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.counter_label)
        title_layout.addWidget(close_btn)
        
        return title_widget
    
    def create_control_bar(self):
        """Create control bar with navigation and slideshow controls"""
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(10, 5, 10, 5)
        
        # Previous button
        prev_btn = QPushButton("◀ Previous")
        prev_btn.setStyleSheet(self.get_button_style())
        prev_btn.clicked.connect(self.previous_movie)
        
        # Play/Pause button
        self.play_pause_btn = QPushButton("⏸ Pause")
        self.play_pause_btn.setStyleSheet(self.get_button_style())
        self.play_pause_btn.clicked.connect(self.toggle_slideshow)
        
        # Next button
        next_btn = QPushButton("Next ▶")
        next_btn.setStyleSheet(self.get_button_style())
        next_btn.clicked.connect(self.next_movie)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 70)  # 7 seconds * 10 (100ms intervals)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #FF69B4;
                border-radius: 5px;
                background-color: #1a1a1a;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #FF69B4;
                border-radius: 4px;
            }
        """)
        
        control_layout.addWidget(prev_btn)
        control_layout.addWidget(self.play_pause_btn)
        control_layout.addWidget(next_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.progress_bar)
        
        return control_widget
    
    def get_button_style(self):
        """Get consistent button styling"""
        return """
            QPushButton {
                background-color: #FF69B4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
            QPushButton:pressed {
                background-color: #C71585;
            }
        """
    
    def center_window(self):
        """Center the window on screen"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def start_slideshow(self):
        """Start the automatic slideshow"""
        if not self.slideshow_active or not self.movies:
            return
        
        self.slideshow_timer = QTimer()
        self.slideshow_timer.timeout.connect(self.next_movie)
        self.slideshow_timer.start(7000)  # 7 seconds
        
        # Progress timer for visual feedback
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(100)  # Update every 100ms
        self.progress_value = 0
    
    def stop_slideshow(self):
        """Stop the automatic slideshow"""
        if self.slideshow_timer:
            self.slideshow_timer.stop()
        if hasattr(self, 'progress_timer'):
            self.progress_timer.stop()
    
    def toggle_slideshow(self):
        """Toggle slideshow on/off"""
        self.slideshow_active = not self.slideshow_active
        
        if self.slideshow_active:
            self.play_pause_btn.setText("⏸ Pause")
            self.start_slideshow()
        else:
            self.play_pause_btn.setText("▶ Play")
            self.stop_slideshow()
    
    def update_progress(self):
        """Update progress bar"""
        if self.slideshow_active:
            self.progress_value += 1
            if self.progress_value > 70:
                self.progress_value = 0
            self.progress_bar.setValue(self.progress_value)
    
    def show_movie(self, index: int):
        """Show movie at given index"""
        if not self.movie_cards or index < 0 or index >= len(self.movie_cards):
            return
        
        # Hide current card
        for card in self.movie_cards:
            card.hide()
            if card.parent():
                self.movie_layout.removeWidget(card)
        
        # Show new card
        self.movie_layout.addWidget(self.movie_cards[index])
        self.movie_cards[index].show()
        
        # Update counter
        self.counter_label.setText(f"{index + 1} / {len(self.movies)}")
        
        # Reset progress
        self.progress_value = 0
        self.progress_bar.setValue(0)
    
    def next_movie(self):
        """Show next movie"""
        if not self.movies:
            return
        
        self.current_index = (self.current_index + 1) % len(self.movies)
        self.show_movie(self.current_index)
    
    def previous_movie(self):
        """Show previous movie"""
        if not self.movies:
            return
        
        self.current_index = (self.current_index - 1) % len(self.movies)
        self.show_movie(self.current_index)
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.stop_slideshow()
        event.accept()

def show_vegamovies_popup(movies: List[Dict[str, Any]], title: str = "Vegamovies Movies"):
    """Show Vegamovies popup with movie gallery"""
    try:
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            app.setQuitOnLastWindowClosed(False)
        
        # Create and show popup
        popup = VegamoviesPopup(movies, title)
        popup.show()
        popup.raise_()
        popup.activateWindow()
        
        # Process events to ensure popup is visible
        app.processEvents()
        
        # Run the popup event loop
        result = popup.exec()
        
        return True
        
    except Exception as e:
        print(f"[VegamoviesPopup] Error showing popup: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test function
if __name__ == "__main__":
    # Sample movie data for testing
    sample_movies = [
        {
            'title': 'Avengers: Endgame (2019)',
            'year': '2019',
            'genre': 'Action/Adventure',
            'quality': '1080p HD',
            'image_url': 'https://example.com/poster1.jpg'
        },
        {
            'title': 'Spider-Man: No Way Home (2021)',
            'year': '2021', 
            'genre': 'Action/Adventure',
            'quality': '1080p HD',
            'image_url': 'https://example.com/poster2.jpg'
        }
    ]
    
    app = QApplication(sys.argv)
    show_vegamovies_popup(sample_movies, "Test Movies")
    sys.exit(app.exec())
