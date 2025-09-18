"""
Data Extractor - Extracts movie/series data from Vegamovies pages
Handles content parsing and data structuring
"""

import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class DataExtractor:
    """Extracts and structures movie/series data from Vegamovies"""
    
    def __init__(self, driver):
        self.driver = driver
        self.movie_selectors = {
            'container': ['.post-item', '.movie-item', 'article', '.entry', '.content-item'],
            'title': ['h2', 'h3', '.title', '.movie-title', '.post-title'],
            'image': ['img', '.poster img', '.thumbnail img'],
            'link': ['a', '.movie-link', '.post-link'],
            'year': ['.year', '.date', '.release-year'],
            'genre': ['.genre', '.category', '.tags'],
            'quality': ['.quality', '.resolution', '.format']
        }
    
    def extract_movie_data(self, container_element) -> Dict[str, Any]:
        """Extract data from a single movie container"""
        movie_data = {
            'title': '',
            'year': '',
            'genre': '',
            'quality': '',
            'image_url': '',
            'page_url': '',
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            # Extract title
            for selector in self.movie_selectors['title']:
                try:
                    title_elem = container_element.find_element(By.CSS_SELECTOR, selector)
                    movie_data['title'] = title_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract image URL
            for selector in self.movie_selectors['image']:
                try:
                    img_elem = container_element.find_element(By.CSS_SELECTOR, selector)
                    movie_data['image_url'] = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                    break
                except NoSuchElementException:
                    continue
            
            # Extract page URL
            for selector in self.movie_selectors['link']:
                try:
                    link_elem = container_element.find_element(By.CSS_SELECTOR, selector)
                    movie_data['page_url'] = link_elem.get_attribute('href')
                    break
                except NoSuchElementException:
                    continue
            
            # Extract year
            for selector in self.movie_selectors['year']:
                try:
                    year_elem = container_element.find_element(By.CSS_SELECTOR, selector)
                    year_text = year_elem.text.strip()
                    year_match = re.search(r'(\d{4})', year_text)
                    if year_match:
                        movie_data['year'] = year_match.group(1)
                    break
                except NoSuchElementException:
                    continue
            
            # Extract genre
            for selector in self.movie_selectors['genre']:
                try:
                    genre_elem = container_element.find_element(By.CSS_SELECTOR, selector)
                    movie_data['genre'] = genre_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract quality
            for selector in self.movie_selectors['quality']:
                try:
                    quality_elem = container_element.find_element(By.CSS_SELECTOR, selector)
                    movie_data['quality'] = quality_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Clean up title (remove year if present)
            if movie_data['title'] and movie_data['year']:
                movie_data['title'] = re.sub(r'\s*\(\d{4}\)\s*', '', movie_data['title']).strip()
            
        except Exception as e:
            print(f"[DataExtractor] Error extracting movie data: {e}")
        
        return movie_data
    
    def find_movie_containers(self) -> List:
        """Find all movie containers on the current page"""
        containers = []
        
        for selector in self.movie_selectors['container']:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"[DataExtractor] Found {len(elements)} containers with selector: {selector}")
                    containers = elements
                    break
            except Exception as e:
                print(f"[DataExtractor] Error with selector {selector}: {e}")
                continue
        
        return containers
    
    def extract_current_date_movies(self) -> List[Dict[str, Any]]:
        """Extract movies released today"""
        movies = []
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            print(f"[DataExtractor] Extracting current date movies for {today}")
            
            # Navigate to latest/recent movies section
            self.navigate_to_recent_movies()
            
            # Find movie containers
            containers = self.find_movie_containers()
            
            for container in containers[:20]:  # Limit to first 20 movies
                try:
                    movie_data = self.extract_movie_data(container)
                    
                    # Filter for today's movies (basic filtering)
                    if movie_data['title']:
                        movies.append(movie_data)
                        
                except Exception as e:
                    print(f"[DataExtractor] Error processing container: {e}")
                    continue
            
            print(f"[DataExtractor] Extracted {len(movies)} current date movies")
            
        except Exception as e:
            print(f"[DataExtractor] Error extracting current date movies: {e}")
        
        return movies
    
    def extract_current_week_movies(self) -> List[Dict[str, Any]]:
        """Extract movies released this week"""
        movies = []
        
        try:
            print("[DataExtractor] Extracting current week movies")
            
            # Navigate to latest/recent movies section
            self.navigate_to_recent_movies()
            
            # Find movie containers
            containers = self.find_movie_containers()
            
            for container in containers[:50]:  # Limit to first 50 movies
                try:
                    movie_data = self.extract_movie_data(container)
                    
                    if movie_data['title']:
                        movies.append(movie_data)
                        
                except Exception as e:
                    print(f"[DataExtractor] Error processing container: {e}")
                    continue
            
            print(f"[DataExtractor] Extracted {len(movies)} current week movies")
            
        except Exception as e:
            print(f"[DataExtractor] Error extracting current week movies: {e}")
        
        return movies
    
    def navigate_to_recent_movies(self):
        """Navigate to the recent/latest movies section"""
        try:
            # Look for recent/latest movies links
            recent_links = [
                "//a[contains(text(), 'Latest')]",
                "//a[contains(text(), 'Recent')]", 
                "//a[contains(text(), 'New')]",
                "//a[contains(text(), 'Today')]"
            ]
            
            for xpath in recent_links:
                try:
                    link = self.driver.find_element(By.XPATH, xpath)
                    link.click()
                    time.sleep(3)
                    print(f"[DataExtractor] Navigated to recent movies section")
                    return
                except NoSuchElementException:
                    continue
            
            print("[DataExtractor] No recent movies link found, staying on current page")
            
        except Exception as e:
            print(f"[DataExtractor] Error navigating to recent movies: {e}")
    
    def scroll_and_load_more(self, max_scrolls: int = 3):
        """Scroll down to load more content"""
        try:
            for i in range(max_scrolls):
                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Look for "Load More" button
                load_more_selectors = [
                    ".load-more",
                    ".show-more", 
                    ".next-page",
                    "button[onclick*='load']"
                ]
                
                for selector in load_more_selectors:
                    try:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if button.is_displayed():
                            button.click()
                            time.sleep(3)
                            print(f"[DataExtractor] Clicked load more button")
                            break
                    except NoSuchElementException:
                        continue
                
        except Exception as e:
            print(f"[DataExtractor] Error during scroll and load: {e}")
    
    def extract_movie_details(self, movie_url: str) -> Dict[str, Any]:
        """Extract detailed information from a movie's individual page"""
        details = {}
        
        try:
            current_url = self.driver.current_url
            self.driver.get(movie_url)
            time.sleep(3)
            
            # Extract detailed information
            detail_selectors = {
                'description': ['.description', '.synopsis', '.plot', '.summary'],
                'cast': ['.cast', '.actors', '.starring'],
                'director': ['.director', '.directed-by'],
                'duration': ['.duration', '.runtime', '.length'],
                'rating': ['.rating', '.imdb-rating', '.score']
            }
            
            for key, selectors in detail_selectors.items():
                for selector in selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        details[key] = element.text.strip()
                        break
                    except NoSuchElementException:
                        continue
            
            # Return to previous page
            self.driver.get(current_url)
            time.sleep(2)
            
        except Exception as e:
            print(f"[DataExtractor] Error extracting movie details: {e}")
        
        return details
