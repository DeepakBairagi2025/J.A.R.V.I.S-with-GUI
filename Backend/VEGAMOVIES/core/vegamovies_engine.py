"""
Vegamovies Engine - Main orchestrator for Vegamovies automation
Handles search, content extraction, and GUI integration
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..utils.ad_blocker import AdBlocker
from ..utils.cache_manager import CacheManager
from .tab_manager import TabManager
from .search_handler import SearchHandler
from .data_extractor import DataExtractor

# Get project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]

class VegamoviesEngine:
    """Main engine for Vegamovies automation with ad-blocking and intelligent navigation"""
    
    def __init__(self):
        self.base_url = "https://vegamovies.menu"
        self.driver = None
        self.tab_manager = None
        self.search_handler = None
        self.data_extractor = None
        self.ad_blocker = AdBlocker()
        self.cache_manager = CacheManager()
        self.is_initialized = False
        
    def initialize(self):
        """Initialize the browser and components"""
        if self.is_initialized:
            return True
            
        try:
            # Setup Chrome options for stealth mode
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Initialize components
            self.tab_manager = TabManager(self.driver)
            self.search_handler = SearchHandler(self.driver, self.tab_manager, self.ad_blocker)
            self.data_extractor = DataExtractor(self.driver)
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"[VegamoviesEngine] Initialization failed: {e}")
            return False
    
    def navigate_to_vegamovies(self):
        """Navigate to Vegamovies homepage with ad protection"""
        if not self.initialize():
            return False
            
        try:
            print(f"[VegamoviesEngine] Navigating to {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for page load and handle initial ads
            time.sleep(3)
            self.tab_manager.close_ad_popups()
            
            # Verify we're on the right page
            if "vegamovies" in self.driver.current_url.lower():
                print("[VegamoviesEngine] Successfully loaded Vegamovies")
                return True
            else:
                print(f"[VegamoviesEngine] Unexpected URL: {self.driver.current_url}")
                return False
                
        except Exception as e:
            print(f"[VegamoviesEngine] Navigation failed: {e}")
            return False
    
    def search_movie(self, title: str) -> bool:
        """Search for a movie/series with ad-popup handling"""
        if not self.navigate_to_vegamovies():
            return False
            
        try:
            print(f"[VegamoviesEngine] Searching for: {title}")
            # Use enhanced search with overlay bypass
            return self.search_handler.perform_search_with_overlay_bypass(title)
            
        except Exception as e:
            print(f"[VegamoviesEngine] Search failed: {e}")
            return False
    
    def get_current_date_movies(self) -> List[Dict[str, Any]]:
        """Get movies released today"""
        cache_key = f"current_date_movies_{time.strftime('%Y-%m-%d')}"
        
        # Check cache first
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            print("[VegamoviesEngine] Using cached current date movies")
            return cached_data
            
        if not self.navigate_to_vegamovies():
            return []
            
        try:
            print("[VegamoviesEngine] Extracting current date movies")
            movies = self.data_extractor.extract_current_date_movies()
            
            # Cache the results for 6 hours
            self.cache_manager.set(cache_key, movies, ttl=21600)
            return movies
            
        except Exception as e:
            print(f"[VegamoviesEngine] Current date movies extraction failed: {e}")
            return []
    
    def get_current_week_movies(self) -> List[Dict[str, Any]]:
        """Get movies released this week"""
        cache_key = f"current_week_movies_{time.strftime('%Y-W%U')}"
        
        # Check cache first
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            print("[VegamoviesEngine] Using cached current week movies")
            return cached_data
            
        if not self.navigate_to_vegamovies():
            return []
            
        try:
            print("[VegamoviesEngine] Extracting current week movies")
            movies = self.data_extractor.extract_current_week_movies()
            
            # Cache the results for 12 hours
            self.cache_manager.set(cache_key, movies, ttl=43200)
            return movies
            
        except Exception as e:
            print(f"[VegamoviesEngine] Current week movies extraction failed: {e}")
            return []
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            self.is_initialized = False
            print("[VegamoviesEngine] Cleanup completed")
        except Exception as e:
            print(f"[VegamoviesEngine] Cleanup error: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

# Global instance for easy access
vegamovies_engine = VegamoviesEngine()
