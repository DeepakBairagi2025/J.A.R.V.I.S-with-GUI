"""
Tab Manager - Handles ad popups and tab switching for Vegamovies
Intelligent tab management to maintain focus on main content
"""

import time
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException

class TabManager:
    """Manages browser tabs and handles ad popup interference"""
    
    def __init__(self, driver):
        self.driver = driver
        self.main_window_handle = None
        self.vegamovies_patterns = [
            "vegamovies",
            "vega movies",
            "vegamovies.menu",
            "vegamovies.com",
            "vegamovies.one",
            "vegamovies.info"
        ]
        self.ad_patterns = [
            "ads",
            "advertisement", 
            "popup",
            "promo",
            "offer",
            "casino",
            "betting",
            "download",
            "install"
        ]
    
    def set_main_window(self):
        """Set the current window as the main Vegamovies window"""
        try:
            self.main_window_handle = self.driver.current_window_handle
            print(f"[TabManager] Main window set: {self.main_window_handle}")
        except Exception as e:
            print(f"[TabManager] Failed to set main window: {e}")
    
    def get_all_windows(self) -> List[str]:
        """Get all open window handles"""
        try:
            return self.driver.window_handles
        except Exception as e:
            print(f"[TabManager] Failed to get windows: {e}")
            return []
    
    def is_ad_window(self, window_handle: str) -> bool:
        """Check if a window is likely an ad popup"""
        try:
            current_window = self.driver.current_window_handle
            self.driver.switch_to.window(window_handle)
            
            # Check URL for ad patterns
            url = self.driver.current_url.lower()
            title = self.driver.title.lower()
            
            # Switch back to original window
            self.driver.switch_to.window(current_window)
            
            # Check if URL or title contains ad patterns
            for pattern in self.ad_patterns:
                if pattern in url or pattern in title:
                    return True
            
            # Check if it's NOT a vegamovies window
            is_vegamovies = any(pattern in url for pattern in self.vegamovies_patterns)
            return not is_vegamovies
            
        except Exception as e:
            print(f"[TabManager] Error checking ad window: {e}")
            return False
    
    def close_ad_popups(self) -> int:
        """Close all detected ad popup windows"""
        closed_count = 0
        
        try:
            all_windows = self.get_all_windows()
            
            if len(all_windows) <= 1:
                return 0
            
            # Store current window
            current_window = self.driver.current_window_handle
            
            # Check each window
            for window_handle in all_windows:
                if window_handle == current_window:
                    continue
                    
                try:
                    if self.is_ad_window(window_handle):
                        print(f"[TabManager] Closing ad window: {window_handle}")
                        self.driver.switch_to.window(window_handle)
                        self.driver.close()
                        closed_count += 1
                        
                except NoSuchWindowException:
                    # Window already closed
                    continue
                except Exception as e:
                    print(f"[TabManager] Error closing window {window_handle}: {e}")
            
            # Return to main window
            try:
                self.driver.switch_to.window(current_window)
            except NoSuchWindowException:
                # Main window was closed, switch to any remaining vegamovies window
                self.find_and_switch_to_vegamovies()
            
            if closed_count > 0:
                print(f"[TabManager] Closed {closed_count} ad popup(s)")
                
        except Exception as e:
            print(f"[TabManager] Error in close_ad_popups: {e}")
        
        return closed_count
    
    def find_and_switch_to_vegamovies(self) -> bool:
        """Find and switch to the main Vegamovies window"""
        try:
            all_windows = self.get_all_windows()
            
            for window_handle in all_windows:
                try:
                    self.driver.switch_to.window(window_handle)
                    url = self.driver.current_url.lower()
                    
                    # Check if this is a vegamovies window
                    if any(pattern in url for pattern in self.vegamovies_patterns):
                        self.main_window_handle = window_handle
                        print(f"[TabManager] Switched to Vegamovies window: {window_handle}")
                        return True
                        
                except Exception as e:
                    print(f"[TabManager] Error checking window {window_handle}: {e}")
                    continue
            
            print("[TabManager] No Vegamovies window found")
            return False
            
        except Exception as e:
            print(f"[TabManager] Error finding Vegamovies window: {e}")
            return False
    
    def monitor_and_clean(self, duration: int = 10):
        """Monitor for new popups and clean them for specified duration"""
        start_time = time.time()
        
        print(f"[TabManager] Starting popup monitoring for {duration} seconds")
        
        while time.time() - start_time < duration:
            try:
                # Check for new popups every 2 seconds
                time.sleep(2)
                
                window_count = len(self.get_all_windows())
                if window_count > 1:
                    closed = self.close_ad_popups()
                    if closed > 0:
                        print(f"[TabManager] Cleaned {closed} popup(s) during monitoring")
                        
            except Exception as e:
                print(f"[TabManager] Error during monitoring: {e}")
                break
        
        print("[TabManager] Popup monitoring completed")
    
    def safe_click_with_popup_handling(self, element, wait_time: int = 5):
        """Click an element and handle any resulting popups"""
        try:
            # Record initial window count
            initial_windows = len(self.get_all_windows())
            
            # Click the element
            element.click()
            
            # Wait a moment for popups to appear
            time.sleep(2)
            
            # Check for new windows
            current_windows = len(self.get_all_windows())
            
            if current_windows > initial_windows:
                print(f"[TabManager] Detected {current_windows - initial_windows} new window(s) after click")
                self.close_ad_popups()
                
                # Ensure we're back on the main window
                self.find_and_switch_to_vegamovies()
            
            return True
            
        except Exception as e:
            print(f"[TabManager] Error in safe_click_with_popup_handling: {e}")
            return False
