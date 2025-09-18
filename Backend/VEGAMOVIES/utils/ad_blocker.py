"""
Ad Blocker - Advanced ad blocking and popup prevention for Vegamovies
Implements multiple strategies to prevent and handle advertisements
"""

import time
from typing import List, Dict, Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AdBlocker:
    """Advanced ad blocking system for Vegamovies automation"""
    
    def __init__(self):
        # Known ad domains and patterns
        self.ad_domains = {
            'popads.net', 'popcash.net', 'propellerads.com', 'revcontent.com',
            'mgid.com', 'outbrain.com', 'taboola.com', 'adsystem.com',
            'doubleclick.net', 'googlesyndication.com', 'amazon-adsystem.com',
            'facebook.com/tr', 'googletagmanager.com', 'google-analytics.com'
        }
        
        # Ad element selectors to hide/remove
        self.ad_selectors = [
            '[id*="ad"]', '[class*="ad"]', '[id*="banner"]', '[class*="banner"]',
            '[id*="popup"]', '[class*="popup"]', '[id*="overlay"]', '[class*="overlay"]',
            'iframe[src*="ads"]', 'iframe[src*="doubleclick"]', 'iframe[src*="googlesyndication"]',
            '.advertisement', '.sponsored', '.promo', '.promotion'
        ]
        
        # Popup trigger elements to avoid
        self.popup_triggers = [
            'a[target="_blank"]', 'a[onclick*="window.open"]', 
            'a[onclick*="popup"]', 'button[onclick*="window.open"]'
        ]
        
        # CSS to inject for ad blocking
        self.blocking_css = """
            /* Hide common ad containers */
            [id*="ad"], [class*="ad"], [id*="banner"], [class*="banner"],
            [id*="popup"], [class*="popup"], [id*="overlay"], [class*="overlay"],
            .advertisement, .sponsored, .promo, .promotion {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                height: 0 !important;
                width: 0 !important;
            }
            
            /* Hide iframe ads */
            iframe[src*="ads"], iframe[src*="doubleclick"], 
            iframe[src*="googlesyndication"], iframe[src*="amazon-adsystem"] {
                display: none !important;
            }
            
            /* Prevent popup overlays */
            .popup-overlay, .modal-overlay, .ad-overlay {
                display: none !important;
            }
        """
    
    def inject_css_blocker(self, driver):
        """Inject CSS to block ads"""
        try:
            script = f"""
                var style = document.createElement('style');
                style.type = 'text/css';
                style.innerHTML = `{self.blocking_css}`;
                document.head.appendChild(style);
            """
            driver.execute_script(script)
            print("[AdBlocker] CSS ad blocker injected")
        except Exception as e:
            print(f"[AdBlocker] Failed to inject CSS blocker: {e}")
    
    def block_requests(self, driver):
        """Block ad requests using Chrome DevTools Protocol"""
        try:
            # Enable network domain
            driver.execute_cdp_cmd('Network.enable', {})
            
            # Set up request interception
            driver.execute_cdp_cmd('Network.setRequestInterception', {
                'patterns': [
                    {'urlPattern': '*ads*', 'interceptionStage': 'HeadersReceived'},
                    {'urlPattern': '*doubleclick*', 'interceptionStage': 'HeadersReceived'},
                    {'urlPattern': '*googlesyndication*', 'interceptionStage': 'HeadersReceived'},
                    {'urlPattern': '*amazon-adsystem*', 'interceptionStage': 'HeadersReceived'}
                ]
            })
            
            print("[AdBlocker] Request blocking enabled")
        except Exception as e:
            print(f"[AdBlocker] Failed to enable request blocking: {e}")
    
    def remove_ad_elements(self, driver):
        """Remove ad elements from the page"""
        removed_count = 0
        
        try:
            for selector in self.ad_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        driver.execute_script("arguments[0].remove();", element)
                        removed_count += 1
                except Exception:
                    continue
            
            if removed_count > 0:
                print(f"[AdBlocker] Removed {removed_count} ad elements")
                
        except Exception as e:
            print(f"[AdBlocker] Error removing ad elements: {e}")
        
        return removed_count
    
    def disable_popup_triggers(self, driver):
        """Disable elements that trigger popups"""
        disabled_count = 0
        
        try:
            for selector in self.popup_triggers:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # Remove onclick handlers
                        driver.execute_script("arguments[0].onclick = null;", element)
                        # Remove target="_blank"
                        driver.execute_script("arguments[0].removeAttribute('target');", element)
                        disabled_count += 1
                except Exception:
                    continue
            
            if disabled_count > 0:
                print(f"[AdBlocker] Disabled {disabled_count} popup triggers")
                
        except Exception as e:
            print(f"[AdBlocker] Error disabling popup triggers: {e}")
        
        return disabled_count
    
    def block_page_ads(self, driver):
        """Comprehensive ad blocking for current page"""
        try:
            print("[AdBlocker] Starting comprehensive ad blocking")
            
            # Inject CSS blocker
            self.inject_css_blocker(driver)
            
            # Remove ad elements
            self.remove_ad_elements(driver)
            
            # Disable popup triggers
            self.disable_popup_triggers(driver)
            
            # Block future requests
            self.block_requests(driver)
            
            print("[AdBlocker] Ad blocking completed")
            
        except Exception as e:
            print(f"[AdBlocker] Error in comprehensive ad blocking: {e}")
    
    def is_ad_url(self, url: str) -> bool:
        """Check if URL is likely an ad"""
        if not url:
            return False
            
        url_lower = url.lower()
        
        # Check against known ad domains
        for domain in self.ad_domains:
            if domain in url_lower:
                return True
        
        # Check for ad-related keywords
        ad_keywords = ['ads', 'advertisement', 'popup', 'banner', 'promo', 'sponsored']
        for keyword in ad_keywords:
            if keyword in url_lower:
                return True
        
        return False
    
    def monitor_and_block(self, driver, duration: int = 30):
        """Monitor page for new ads and block them"""
        start_time = time.time()
        
        print(f"[AdBlocker] Starting ad monitoring for {duration} seconds")
        
        while time.time() - start_time < duration:
            try:
                # Check for new ad elements every 3 seconds
                time.sleep(3)
                
                removed = self.remove_ad_elements(driver)
                if removed > 0:
                    print(f"[AdBlocker] Removed {removed} new ad elements")
                
            except Exception as e:
                print(f"[AdBlocker] Error during monitoring: {e}")
                break
        
        print("[AdBlocker] Ad monitoring completed")
    
    def create_ad_blocking_profile(self) -> Dict:
        """Create Chrome profile settings for ad blocking"""
        prefs = {
            # Block popups
            "profile.default_content_setting_values.popups": 2,
            
            # Block notifications
            "profile.default_content_setting_values.notifications": 2,
            
            # Block location sharing
            "profile.default_content_setting_values.geolocation": 2,
            
            # Block media stream
            "profile.default_content_setting_values.media_stream": 2,
            
            # Disable images (optional, for faster loading)
            # "profile.managed_default_content_settings.images": 2,
            
            # Disable JavaScript (not recommended for modern sites)
            # "profile.managed_default_content_settings.javascript": 2
        }
        
        return prefs
