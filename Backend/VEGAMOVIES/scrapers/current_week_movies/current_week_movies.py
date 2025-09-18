"""
Current Week Movies Scraper - Extracts movies released this week from Vegamovies
Specialized scraper for weekly movie releases with week range analysis
"""

import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .week_analyzer import WeekAnalyzer
from ...core.data_extractor import DataExtractor

class CurrentWeekMovies:
    """Scraper for movies released in current week"""
    
    def __init__(self, driver, tab_manager, ad_blocker):
        self.driver = driver
        self.tab_manager = tab_manager
        self.ad_blocker = ad_blocker
        self.data_extractor = DataExtractor(driver)
        self.week_analyzer = WeekAnalyzer()
        
        # Current week date range
        self.week_start, self.week_end = self.week_analyzer.get_current_week_range()
        
        # Selectors for weekly content
        self.weekly_selectors = [
            '.weekly-movies', '.this-week', '.week-releases',
            '.recent-week', '.latest-week'
        ]
    
    def extract_current_week_movies(self) -> List[Dict[str, Any]]:
        """Extract movies released this week"""
        movies = []
        
        try:
            print(f"[CurrentWeekMovies] Extracting for week {self.week_start} to {self.week_end}")
            
            # Apply ad blocking
            self.ad_blocker.block_page_ads(self.driver)
            
            # Extract from multiple sources
            movies.extend(self._extract_from_weekly_sections())
            movies.extend(self._extract_from_recent_pages())
            movies.extend(self._extract_from_category_pages())
            
            # Filter for current week and deduplicate
            movies = self._filter_current_week_movies(movies)
            movies = self._deduplicate_movies(movies)
            
            # Add week metadata
            for movie in movies:
                movie['week_start'] = self.week_start
                movie['week_end'] = self.week_end
                movie['extraction_type'] = 'current_week'
            
            print(f"[CurrentWeekMovies] Extracted {len(movies)} current week movies")
            
        except Exception as e:
            print(f"[CurrentWeekMovies] Error extracting current week movies: {e}")
        
        return movies
    
    def _extract_from_weekly_sections(self) -> List[Dict[str, Any]]:
        """Extract from dedicated weekly sections"""
        movies = []
        
        try:
            for selector in self.weekly_selectors:
                try:
                    section = self.driver.find_element(By.CSS_SELECTOR, selector)
                    section_movies = self._extract_movies_from_section(section)
                    movies.extend(section_movies)
                    print(f"[CurrentWeekMovies] Found {len(section_movies)} movies in {selector}")
                except NoSuchElementException:
                    continue
            
        except Exception as e:
            print(f"[CurrentWeekMovies] Error extracting from weekly sections: {e}")
        
        return movies
    
    def _extract_from_recent_pages(self) -> List[Dict[str, Any]]:
        """Extract from recent/latest movies pages"""
        movies = []
        
        try:
            # Navigate through recent pages
            recent_urls = [
                '/latest-movies/',
                '/recent-movies/', 
                '/new-releases/',
                '/category/latest/'
            ]
            
            current_url = self.driver.current_url
            base_url = '/'.join(current_url.split('/')[:3])
            
            for url_path in recent_urls:
                try:
                    full_url = base_url + url_path
                    self.driver.get(full_url)
                    time.sleep(3)
                    
                    # Handle popups
                    self.tab_manager.close_ad_popups()
                    
                    # Extract movies
                    containers = self.data_extractor.find_movie_containers()
                    
                    for container in containers[:40]:  # More movies for weekly
                        try:
                            movie_data = self.data_extractor.extract_movie_data(container)
                            
                            # Add date information
                            date_info = self._extract_date_from_container(container)
                            if date_info:
                                movie_data['release_date'] = date_info
                            
                            if movie_data['title']:
                                movie_data['source_page'] = url_path
                                movies.append(movie_data)
                                
                        except Exception:
                            continue
                    
                    print(f"[CurrentWeekMovies] Extracted {len(movies)} movies from {url_path}")
                    
                    # Don't overload - break after first successful extraction
                    if movies:
                        break
                        
                except Exception as e:
                    print(f"[CurrentWeekMovies] Error with {url_path}: {e}")
                    continue
            
            # Return to original page
            self.driver.get(current_url)
            time.sleep(2)
            
        except Exception as e:
            print(f"[CurrentWeekMovies] Error extracting from recent pages: {e}")
        
        return movies
    
    def _extract_from_category_pages(self) -> List[Dict[str, Any]]:
        """Extract from category pages that might have weekly content"""
        movies = []
        
        try:
            # Look for category navigation
            category_links = [
                "//a[contains(text(), 'Movies')]",
                "//a[contains(text(), 'Latest')]",
                "//a[contains(text(), 'Hollywood')]",
                "//a[contains(text(), 'Bollywood')]"
            ]
            
            for xpath in category_links:
                try:
                    link = self.driver.find_element(By.XPATH, xpath)
                    
                    # Use safe click
                    self.tab_manager.safe_click_with_popup_handling(link)
                    time.sleep(3)
                    
                    # Extract movies from category page
                    containers = self.data_extractor.find_movie_containers()
                    
                    for container in containers[:30]:
                        try:
                            movie_data = self.data_extractor.extract_movie_data(container)
                            
                            if movie_data['title']:
                                movie_data['source_category'] = xpath
                                movies.append(movie_data)
                                
                        except Exception:
                            continue
                    
                    print(f"[CurrentWeekMovies] Found {len(movies)} movies from category")
                    break  # Stop after first successful category
                    
                except NoSuchElementException:
                    continue
            
        except Exception as e:
            print(f"[CurrentWeekMovies] Error extracting from categories: {e}")
        
        return movies
    
    def _extract_movies_from_section(self, section_element) -> List[Dict[str, Any]]:
        """Extract movies from a specific section element"""
        movies = []
        
        try:
            # Find movie containers within section
            containers = section_element.find_elements(
                By.CSS_SELECTOR,
                '.movie-item, .post-item, article, .content-item, .film-item'
            )
            
            for container in containers:
                try:
                    movie_data = self.data_extractor.extract_movie_data(container)
                    
                    # Add section context
                    movie_data['source_section'] = section_element.get_attribute('class') or 'weekly'
                    
                    # Extract date from container
                    date_info = self._extract_date_from_container(container)
                    if date_info:
                        movie_data['release_date'] = date_info
                    
                    if movie_data['title']:
                        movies.append(movie_data)
                        
                except Exception:
                    continue
            
        except Exception as e:
            print(f"[CurrentWeekMovies] Error extracting from section: {e}")
        
        return movies
    
    def _extract_date_from_container(self, container) -> Optional[str]:
        """Extract date information from movie container"""
        try:
            date_selectors = [
                '.release-date', '.date', '.published', '.post-date',
                '.movie-date', '.upload-date', '.added-date', '.time'
            ]
            
            for selector in date_selectors:
                try:
                    date_element = container.find_element(By.CSS_SELECTOR, selector)
                    date_text = date_element.text.strip()
                    
                    # Use week analyzer to parse date
                    parsed_date = self.week_analyzer.parse_date(date_text)
                    if parsed_date:
                        return parsed_date
                        
                except NoSuchElementException:
                    continue
            
            return None
            
        except Exception as e:
            print(f"[CurrentWeekMovies] Error extracting date: {e}")
            return None
    
    def _filter_current_week_movies(self, movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter movies to only include those from current week"""
        filtered_movies = []
        
        try:
            for movie in movies:
                # Check if movie has date within current week
                release_date = movie.get('release_date', '')
                
                if release_date and self.week_analyzer.is_in_current_week(release_date):
                    movie['week_verified'] = True
                    filtered_movies.append(movie)
                    continue
                
                # Check for weekly keywords
                if self._has_weekly_indicators(movie):
                    movie['week_assumed'] = True
                    filtered_movies.append(movie)
                    continue
                
                # If from recent source and no conflicting date, include
                if self._seems_weekly_relevant(movie):
                    movie['week_inferred'] = True
                    filtered_movies.append(movie)
            
            print(f"[CurrentWeekMovies] Filtered to {len(filtered_movies)} current week movies")
            
        except Exception as e:
            print(f"[CurrentWeekMovies] Error filtering movies: {e}")
        
        return filtered_movies
    
    def _has_weekly_indicators(self, movie: Dict[str, Any]) -> bool:
        """Check if movie has indicators of being from current week"""
        try:
            # Check title for weekly keywords
            title = movie.get('title', '').lower()
            weekly_keywords = ['this week', 'weekly', 'new this week', 'week release']
            
            if any(keyword in title for keyword in weekly_keywords):
                return True
            
            # Check source section
            source_section = movie.get('source_section', '').lower()
            if any(keyword in source_section for keyword in ['week', 'recent', 'latest']):
                return True
            
            # Check source page
            source_page = movie.get('source_page', '').lower()
            if 'recent' in source_page or 'latest' in source_page:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _seems_weekly_relevant(self, movie: Dict[str, Any]) -> bool:
        """Heuristic to determine if movie is relevant for current week"""
        try:
            # If from a recent/latest source without old date, likely relevant
            source_indicators = [
                movie.get('source_page', '').lower(),
                movie.get('source_section', '').lower(),
                movie.get('source_category', '').lower()
            ]
            
            recent_indicators = ['recent', 'latest', 'new', 'today']
            has_recent_source = any(
                any(indicator in source for indicator in recent_indicators)
                for source in source_indicators if source
            )
            
            if has_recent_source:
                # Check if there's an old date that would exclude it
                release_date = movie.get('release_date', '')
                if release_date:
                    return self.week_analyzer.is_recent_enough(release_date, days=14)
                else:
                    return True  # No date but from recent source
            
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
                clean_title = re.sub(r'\b(movie|film|hd|1080p|720p|webrip|hdrip)\b', '', clean_title)
                clean_title = clean_title.strip()
                
                if clean_title and clean_title not in seen_titles:
                    seen_titles.add(clean_title)
                    unique_movies.append(movie)
            
            print(f"[CurrentWeekMovies] Deduplicated to {len(unique_movies)} unique movies")
            
        except Exception as e:
            print(f"[CurrentWeekMovies] Error deduplicating movies: {e}")
        
        return unique_movies
    
    def get_week_summary(self, movies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for the week's movies"""
        try:
            summary = {
                'total_movies': len(movies),
                'week_start': self.week_start,
                'week_end': self.week_end,
                'verified_dates': len([m for m in movies if m.get('week_verified')]),
                'assumed_weekly': len([m for m in movies if m.get('week_assumed')]),
                'inferred_weekly': len([m for m in movies if m.get('week_inferred')]),
                'genres': {},
                'qualities': {},
                'sources': {}
            }
            
            # Analyze genres, qualities, sources
            for movie in movies:
                genre = movie.get('genre', 'Unknown')
                if genre:
                    summary['genres'][genre] = summary['genres'].get(genre, 0) + 1
                
                quality = movie.get('quality', 'Unknown')
                if quality:
                    summary['qualities'][quality] = summary['qualities'].get(quality, 0) + 1
                
                source = movie.get('source_page', movie.get('source_section', 'Unknown'))
                if source:
                    summary['sources'][source] = summary['sources'].get(source, 0) + 1
            
            return summary
            
        except Exception as e:
            print(f"[CurrentWeekMovies] Error generating summary: {e}")
            return {}
