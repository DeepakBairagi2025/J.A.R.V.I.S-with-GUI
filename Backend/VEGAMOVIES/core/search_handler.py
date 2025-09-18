"""
Search Handler - Robust search functionality with retry mechanisms
Handles search operations with ad-popup interference protection
"""

import time
from typing import Optional, List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

class SearchHandler:
    """Handles search operations with intelligent retry and ad protection"""
    
    def __init__(self, driver, tab_manager, ad_blocker):
        self.driver = driver
        self.tab_manager = tab_manager
        self.ad_blocker = ad_blocker
        self.search_selectors = [
            "input[type='search']",
            "input[placeholder*='search']", 
            "input[placeholder*='Search']",
            ".search-input",
            "#search",
            ".search-field",
            "input[name='s']"
        ]
        self.search_button_selectors = [
            "button[type='submit']",
            ".search-button",
            ".search-btn", 
            "input[type='submit']",
            ".fa-search",
            ".search-icon"
        ]
    
    def find_search_input(self) -> Optional[object]:
        """Find the search input field using multiple selectors"""
        wait = WebDriverWait(self.driver, 10)
        
        for selector in self.search_selectors:
            try:
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"[SearchHandler] Found search input: {selector}")
                return element
            except TimeoutException:
                continue
        
        print("[SearchHandler] No search input found")
        return None
    
    def find_search_button(self) -> Optional[object]:
        """Find the search button using multiple selectors"""
        wait = WebDriverWait(self.driver, 5)
        
        for selector in self.search_button_selectors:
            try:
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"[SearchHandler] Found search button: {selector}")
                return element
            except TimeoutException:
                continue
        
        print("[SearchHandler] No search button found")
        return None
    
    def perform_search(self, query: str, max_retries: int = 3) -> bool:
        """Perform search with retry mechanism and ad handling"""
        
        for attempt in range(max_retries):
            try:
                print(f"[SearchHandler] Search attempt {attempt + 1}/{max_retries} for: {query}")
                
                # Set main window reference
                self.tab_manager.set_main_window()
                
                # Find search input
                search_input = self.find_search_input()
                if not search_input:
                    print("[SearchHandler] Search input not found")
                    continue
                
                # Clear and enter search query
                search_input.clear()
                search_input.send_keys(query)
                time.sleep(1)
                
                # Try to find and click search button
                search_button = self.find_search_button()
                if search_button:
                    # Use safe click with popup handling
                    success = self.tab_manager.safe_click_with_popup_handling(search_button)
                    if not success:
                        print("[SearchHandler] Search button click failed")
                        continue
                else:
                    # Fallback: press Enter
                    search_input.send_keys(Keys.RETURN)
                
                # Wait for potential popups and handle them
                time.sleep(3)
                self.tab_manager.close_ad_popups()
                
                # Verify we're still on vegamovies and search was performed
                if self.verify_search_results(query):
                    print(f"[SearchHandler] Search successful for: {query}")
                    return True
                else:
                    print(f"[SearchHandler] Search verification failed for: {query}")
                    
            except ElementClickInterceptedException:
                print("[SearchHandler] Click intercepted, likely by ad popup")
                self.tab_manager.close_ad_popups()
                time.sleep(2)
                continue
                
            except Exception as e:
                print(f"[SearchHandler] Search attempt {attempt + 1} failed: {e}")
                self.tab_manager.close_ad_popups()
                time.sleep(2)
                continue
        
        print(f"[SearchHandler] All search attempts failed for: {query}")
        return False
    
    def verify_search_results(self, query: str) -> bool:
        """Verify that search results are displayed"""
        try:
            # Wait for page to load
            time.sleep(3)
            
            # Check if we're still on vegamovies
            current_url = self.driver.current_url.lower()
            if "vegamovies" not in current_url:
                print(f"[SearchHandler] Not on vegamovies page: {current_url}")
                return False
            
            # Look for search results indicators
            result_indicators = [
                ".search-results",
                ".movie-item",
                ".post-item", 
                ".content-item",
                "article",
                ".entry"
            ]
            
            wait = WebDriverWait(self.driver, 10)
            
            for selector in result_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"[SearchHandler] Found {len(elements)} search results")
                        return True
                except Exception:
                    continue
            
            # Check if URL contains search parameters
            if any(param in current_url for param in ['search', 's=', 'query']):
                print("[SearchHandler] Search URL detected")
                return True
            
            print("[SearchHandler] No search results found")
            return False
            
        except Exception as e:
            print(f"[SearchHandler] Error verifying search results: {e}")
            return False
    
    def perform_search_with_overlay_bypass(self, query: str, max_retries: int = 3) -> bool:
        """Enhanced search with overlay bypass techniques"""
        
        for attempt in range(max_retries):
            try:
                print(f"[SearchHandler] Enhanced search attempt {attempt + 1}/{max_retries} for: {query}")
                
                # Set main window reference
                self.tab_manager.set_main_window()
                
                # Remove overlays first
                self._remove_search_overlays()
                
                # Find search input
                search_input = self.find_search_input()
                if not search_input:
                    print("[SearchHandler] Search input not found")
                    continue
                
                # Clear and enter search query
                search_input.clear()
                search_input.send_keys(query)
                time.sleep(1)
                
                # Try multiple search strategies
                success = (
                    self._try_enter_key_search(search_input) or
                    self._try_javascript_click_search() or
                    self._try_coordinate_click_search() or
                    self._try_form_submit_search()
                )
                
                if success:
                    # Wait for potential popups and handle them
                    time.sleep(3)
                    self.tab_manager.close_ad_popups()
                    
                    # Verify search was performed
                    if self.verify_search_results(query):
                        print(f"[SearchHandler] Enhanced search successful for: {query}")
                        return True
                
            except Exception as e:
                print(f"[SearchHandler] Enhanced search attempt {attempt + 1} failed: {e}")
                self.tab_manager.close_ad_popups()
                time.sleep(2)
                continue
        
        print(f"[SearchHandler] All enhanced search attempts failed for: {query}")
        return False
    
    def _remove_search_overlays(self):
        """Remove overlay elements that block search interactions"""
        try:
            # JavaScript to remove high z-index overlays
            overlay_removal_script = """
                // Remove high z-index overlays
                var overlays = document.querySelectorAll('div[style*="z-index"]');
                overlays.forEach(function(overlay) {
                    var zIndex = window.getComputedStyle(overlay).zIndex;
                    if (zIndex && parseInt(zIndex) > 1000) {
                        overlay.style.display = 'none';
                        overlay.remove();
                    }
                });
                
                // Remove common ad overlay classes
                var adOverlays = document.querySelectorAll('.overlay, .popup-overlay, .ad-overlay, [id*="overlay"], [class*="overlay"]');
                adOverlays.forEach(function(el) { 
                    el.style.display = 'none'; 
                    el.remove(); 
                });
                
                // Remove elements with pointer-events: auto that might be blocking
                var blockingElements = document.querySelectorAll('div[style*="pointer-events: auto"]');
                blockingElements.forEach(function(el) {
                    if (el.style.position === 'absolute' || el.style.position === 'fixed') {
                        el.style.display = 'none';
                        el.remove();
                    }
                });
            """
            
            self.driver.execute_script(overlay_removal_script)
            print("[SearchHandler] Removed search overlays")
            time.sleep(1)
            
        except Exception as e:
            print(f"[SearchHandler] Error removing overlays: {e}")
    
    def _try_enter_key_search(self, search_input) -> bool:
        """Try search using Enter key"""
        try:
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)
            print("[SearchHandler] Tried Enter key search")
            return True
        except Exception as e:
            print(f"[SearchHandler] Enter key search failed: {e}")
            return False
    
    def _try_javascript_click_search(self) -> bool:
        """Try search using JavaScript click"""
        try:
            # Find search button and click via JavaScript
            js_click_script = """
                var searchBtn = document.querySelector('input[type="submit"].search-submit') || 
                               document.querySelector('.search-button') ||
                               document.querySelector('button[type="submit"]');
                if (searchBtn) {
                    searchBtn.click();
                    return true;
                }
                return false;
            """
            
            result = self.driver.execute_script(js_click_script)
            if result:
                print("[SearchHandler] JavaScript click search successful")
                time.sleep(2)
                return True
            else:
                print("[SearchHandler] JavaScript click search failed - button not found")
                return False
                
        except Exception as e:
            print(f"[SearchHandler] JavaScript click search failed: {e}")
            return False
    
    def _try_coordinate_click_search(self) -> bool:
        """Try search using ActionChains coordinate click"""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            search_button = self.find_search_button()
            if search_button:
                # Get button location and size
                location = search_button.location
                size = search_button.size
                
                # Calculate center coordinates
                center_x = location['x'] + size['width'] // 2
                center_y = location['y'] + size['height'] // 2
                
                # Use ActionChains to click at coordinates
                actions = ActionChains(self.driver)
                actions.move_by_offset(center_x, center_y).click().perform()
                
                print(f"[SearchHandler] Coordinate click at ({center_x}, {center_y})")
                time.sleep(2)
                return True
            
            return False
            
        except Exception as e:
            print(f"[SearchHandler] Coordinate click search failed: {e}")
            return False
    
    def _try_form_submit_search(self) -> bool:
        """Try search by submitting the form directly"""
        try:
            # Find and submit the search form
            form_submit_script = """
                var searchForm = document.querySelector('form[role="search"]') ||
                                document.querySelector('.search-form') ||
                                document.querySelector('form:has(input[type="search"])');
                if (searchForm) {
                    searchForm.submit();
                    return true;
                }
                return false;
            """
            
            result = self.driver.execute_script(form_submit_script)
            if result:
                print("[SearchHandler] Form submit search successful")
                time.sleep(2)
                return True
            else:
                print("[SearchHandler] Form submit search failed - form not found")
                return False
                
        except Exception as e:
            print(f"[SearchHandler] Form submit search failed: {e}")
            return False
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions if available"""
        suggestions = []
        
        try:
            search_input = self.find_search_input()
            if not search_input:
                return suggestions
            
            # Type partial query
            search_input.clear()
            search_input.send_keys(partial_query)
            time.sleep(2)
            
            # Look for suggestion dropdown
            suggestion_selectors = [
                ".search-suggestions li",
                ".autocomplete-suggestion",
                ".suggestion-item",
                ".search-dropdown li"
            ]
            
            for selector in suggestion_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements[:5]:  # Limit to 5 suggestions
                        text = element.text.strip()
                        if text and text not in suggestions:
                            suggestions.append(text)
                    
                    if suggestions:
                        break
                        
                except Exception:
                    continue
            
            print(f"[SearchHandler] Found {len(suggestions)} suggestions")
            
        except Exception as e:
            print(f"[SearchHandler] Error getting suggestions: {e}")
        
        return suggestions
