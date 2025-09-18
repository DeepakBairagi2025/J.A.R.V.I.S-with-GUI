"""
Current Date Movies Scraper - Extracts movies released today from Vegamovies
Specialized scraper for today's movie releases with intelligent date parsing
"""

import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .date_parser import DateParser
from ...core.data_extractor import DataExtractor

class CurrentDateMovies:
    """Scraper for movies released on current date"""
    
    def __init__(self, driver, tab_manager, ad_blocker):
        self.driver = driver
        self.tab_manager = tab_manager
        self.ad_blocker = ad_blocker
        self.data_extractor = DataExtractor(driver)
        self.date_parser = DateParser()
        self.today = datetime.now().strftime('%Y-%m-%d')
        
        # Selectors for date-specific content
        self.date_selectors = [
            '.release-date', '.date', '.published', '.post-date',
            '.movie-date', '.upload-date', '.added-date'
        ]
        
        # Keywords that indicate recent releases
        self.recent_keywords = [
            'today', 'new', 'latest', 'fresh', 'just added',
            'recently added', 'new release', 'today\'s'
        ]
    
    def extract_current_date_movies(self) -> List[Dict[str, Any]]:
        """Extract movies released today"""
        movies = []
        
        try:
            print(f"[CurrentDateMovies] Starting extraction for {self.today}")
            
            # Apply ad blocking
            self.ad_blocker.block_page_ads(self.driver)
            
            # Navigate to latest movies section
            self._navigate_to_latest_section()
            
            # Extract movies from multiple sources
            movies.extend(self._extract_from_homepage())
            movies.extend(self._extract_from_latest_page())
            movies.extend(self._extract_from_new_releases())
            
            # Filter and deduplicate
            movies = self._filter_current_date_movies(movies)
            movies = self._deduplicate_movies(movies)
            
            print(f"[CurrentDateMovies] Extracted {len(movies)} current date movies")
            
        except Exception as e:
            print(f"[CurrentDateMovies] Error extracting current date movies: {e}")
        
        return movies
    
    def _navigate_to_latest_section(self):
        """Navigate to the latest movies section"""
        try:
            # Look for latest/new movies navigation
            nav_selectors = [
                "//a[contains(text(), 'Latest')]",
                "//a[contains(text(), 'New')]",
                "//a[contains(text(), 'Recent')]",
                "//a[contains(text(), 'Today')]",
                ".menu-item a[href*='latest']",
                ".menu-item a[href*='new']"
            ]
            
            for selector in nav_selectors:
                try:
                    if selector.startswith('//'):
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Use safe click to handle popups
                    self.tab_manager.safe_click_with_popup_handling(element)
                    time.sleep(3)
                    print(f"[CurrentDateMovies] Navigated to latest section")
                    return
                    
                except NoSuchElementException:
                    continue
            
            print("[CurrentDateMovies] No latest section found, staying on current page")
            
        except Exception as e:
            print(f"[CurrentDateMovies] Error navigating to latest section: {e}")
    
    def _extract_from_homepage(self) -> List[Dict[str, Any]]:
        """Extract current date movies from homepage"""
        movies = []
        
        try:
            # Look for featured/latest sections on homepage
            featured_sections = [
                '.featured-movies', '.latest-movies', '.new-releases',
                '.today-movies', '.recent-movies', '.homepage-movies'
            ]
            
            for section_selector in featured_sections:
                try:
                    section = self.driver.find_element(By.CSS_SELECTOR, section_selector)
                    section_movies = self._extract_movies_from_section(section)
                    movies.extend(section_movies)
                    print(f"[CurrentDateMovies] Found {len(section_movies)} movies in {section_selector}")
                except NoSuchElementException:
                    continue
            
        except Exception as e:
            print(f"[CurrentDateMovies] Error extracting from homepage: {e}")
        
        return movies
    
    def _extract_from_latest_page(self) -> List[Dict[str, Any]]:
        """Extract movies from dedicated latest movies page"""
        movies = []
        
        try:
            # Get all movie containers
            containers = self.data_extractor.find_movie_containers()
            
            for container in containers[:30]:  # Limit to first 30
                try:
                    movie_data = self.data_extractor.extract_movie_data(container)
                    
                    # Add date information
                    date_info = self._extract_date_from_container(container)
                    if date_info:
                        movie_data['release_date'] = date_info
                    
                    if movie_data['title']:
                        movies.append(movie_data)
                        
                except Exception as e:
                    print(f"[CurrentDateMovies] Error processing container: {e}")
                    continue
            
        except Exception as e:
            print(f"[CurrentDateMovies] Error extracting from latest page: {e}")
        
        return movies
    
    def _extract_from_new_releases(self) -> List[Dict[str, Any]]:
        """Extract from new releases section"""
        movies = []
        
        try:
            # Look for "New Releases" or similar sections
            new_release_urls = [
                '/category/new-releases/',
                '/new-movies/',
                '/latest-movies/',
                '/today-movies/'
            ]
            
            current_url = self.driver.current_url
            
            for url_path in new_release_urls:
                try:
                    full_url = self.driver.current_url.split('/')[0:3]
                    full_url = '/'.join(full_url) + url_path
                    
                    self.driver.get(full_url)
                    time.sleep(3)
                    
                    # Handle any popups
                    self.tab_manager.close_ad_popups()
                    
                    # Extract movies from this page
                    containers = self.data_extractor.find_movie_containers()
                    
                    for container in containers[:20]:  # Limit to first 20
                        try:
                            movie_data = self.data_extractor.extract_movie_data(container)
                            if movie_data['title']:
                                movies.append(movie_data)
                        except Exception:
                            continue
                    
                    print(f"[CurrentDateMovies] Found {len(movies)} movies from {url_path}")
                    break  # Stop after first successful extraction
                    
                except Exception as e:
                    print(f"[CurrentDateMovies] Error with URL {url_path}: {e}")
                    continue
            
            # Return to original page
            self.driver.get(current_url)
            time.sleep(2)
            
        except Exception as e:
            print(f"[CurrentDateMovies] Error extracting from new releases: {e}")
        
        return movies
    
    def _extract_movies_from_section(self, section_element) -> List[Dict[str, Any]]:
        """Extract movies from a specific section element"""
        movies = []
        
        try:
            # Find movie containers within the section
            movie_containers = section_element.find_elements(
                By.CSS_SELECTOR, 
                '.movie-item, .post-item, article, .content-item'
            )
            
            for container in movie_containers:
                try:
                    movie_data = self.data_extractor.extract_movie_data(container)
                    
                    # Add section context
                    movie_data['source_section'] = section_element.get_attribute('class') or 'unknown'
                    
                    if movie_data['title']:
                        movies.append(movie_data)
                        
                except Exception as e:
                    print(f"[CurrentDateMovies] Error processing section container: {e}")
                    continue
            
        except Exception as e:
            print(f"[CurrentDateMovies] Error extracting from section: {e}")
        
        return movies
    
    def _extract_date_from_container(self, container) -> Optional[str]:
        """Extract date information from movie container"""
        try:
            for selector in self.date_selectors:
                try:
                    date_element = container.find_element(By.CSS_SELECTOR, selector)
                    date_text = date_element.text.strip()
                    
                    # Parse the date
                    parsed_date = self.date_parser.parse_date(date_text)
                    if parsed_date:
                        return parsed_date
                        
                except NoSuchElementException:
                    continue
            
            return None
            
        except Exception as e:
            print(f"[CurrentDateMovies] Error extracting date: {e}")
            return None
    
    def _filter_current_date_movies(self, movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter movies to only include those from current date"""
        filtered_movies = []
        
        try:
            for movie in movies:
                # Check if movie has today's date
                release_date = movie.get('release_date', '')
                
                if release_date == self.today:
                    filtered_movies.append(movie)
                    continue
                
                # Check for recent keywords in title or other fields
                title = movie.get('title', '').lower()
                if any(keyword in title for keyword in self.recent_keywords):
                    movie['is_recent'] = True
                    filtered_movies.append(movie)
                    continue
                
                # If no specific date, include if it seems recent
                if not release_date and self._seems_recent(movie):
                    movie['assumed_recent'] = True
                    filtered_movies.append(movie)
            
            print(f"[CurrentDateMovies] Filtered to {len(filtered_movies)} current date movies")
            
        except Exception as e:
            print(f"[CurrentDateMovies] Error filtering movies: {e}")
        
        return filtered_movies
    
    def _seems_recent(self, movie: Dict[str, Any]) -> bool:
        """Heuristic to determine if movie seems recently added"""
        try:
            # Check source section
            source_section = movie.get('source_section', '').lower()
            if any(keyword in source_section for keyword in ['latest', 'new', 'recent', 'today']):
                return True
            
            # Check if it's from a recent movies page
            if 'latest' in movie.get('page_url', '').lower():
                return True
            
            # Check quality indicators (new releases often have good quality)
            quality = movie.get('quality', '').lower()
            if any(q in quality for q in ['1080p', '4k', 'hdrip', 'webrip']):
                return True
            
            return False
            
        except Exception:
            return False
    
    def _deduplicate_movies(self, movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate movies based on title similarity"""
        unique_movies = []
        seen_titles = set()
        
        try:
            for movie in movies:
                title = movie.get('title', '').lower().strip()
                
                # Clean title for comparison
                clean_title = re.sub(r'[^\w\s]', '', title)
                clean_title = re.sub(r'\s+', ' ', clean_title)
                
                if clean_title and clean_title not in seen_titles:
                    seen_titles.add(clean_title)
                    unique_movies.append(movie)
            
            print(f"[CurrentDateMovies] Deduplicated to {len(unique_movies)} unique movies")
            
        except Exception as e:
            print(f"[CurrentDateMovies] Error deduplicating movies: {e}")
        
        return unique_movies
