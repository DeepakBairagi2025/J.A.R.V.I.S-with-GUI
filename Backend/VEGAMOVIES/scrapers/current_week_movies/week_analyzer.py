"""
Week Analyzer - Analyzes and manages week-based date ranges for Vegamovies
Handles current week calculations and date range operations
"""

import re
from datetime import datetime, timedelta
from typing import Tuple, Optional, List

class WeekAnalyzer:
    """Analyzes dates and week ranges for current week movie extraction"""
    
    def __init__(self):
        self.today = datetime.now()
        
        # Week starts on Monday (0=Monday, 6=Sunday)
        self.week_start_day = 0
        
        # Date parsing patterns (reuse from DateParser)
        self.date_patterns = [
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', '%m-%d-%Y'),
            (r'(\w+)\s+(\d{1,2}),\s+(\d{4})', '%B %d, %Y'),
            (r'(\d{1,2})\s+(\w+)\s+(\d{4})', '%d %B %Y'),
        ]
        
        # Relative date keywords for week analysis
        self.week_keywords = {
            'this week': 0,
            'current week': 0,
            'week': 0,
            'last week': -1,
            'previous week': -1,
            'next week': 1,
            'coming week': 1
        }
        
        # Month name mappings
        self.month_names = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2,
            'march': 3, 'mar': 3, 'april': 4, 'apr': 4,
            'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
            'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10, 'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
    
    def get_current_week_range(self) -> Tuple[str, str]:
        """Get current week's start and end dates (Monday to Sunday)"""
        try:
            # Find Monday of current week
            days_since_monday = self.today.weekday()
            week_start = self.today - timedelta(days=days_since_monday)
            
            # Find Sunday of current week
            week_end = week_start + timedelta(days=6)
            
            return (
                week_start.strftime('%Y-%m-%d'),
                week_end.strftime('%Y-%m-%d')
            )
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error getting current week range: {e}")
            # Fallback to today
            today_str = self.today.strftime('%Y-%m-%d')
            return (today_str, today_str)
    
    def get_week_range(self, date_str: str) -> Tuple[str, str]:
        """Get week range for a specific date"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Find Monday of that week
            days_since_monday = date_obj.weekday()
            week_start = date_obj - timedelta(days=days_since_monday)
            
            # Find Sunday of that week
            week_end = week_start + timedelta(days=6)
            
            return (
                week_start.strftime('%Y-%m-%d'),
                week_end.strftime('%Y-%m-%d')
            )
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error getting week range for {date_str}: {e}")
            return (date_str, date_str)
    
    def is_in_current_week(self, date_str: str) -> bool:
        """Check if date falls within current week"""
        try:
            week_start, week_end = self.get_current_week_range()
            
            # Convert to datetime objects for comparison
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            start_obj = datetime.strptime(week_start, '%Y-%m-%d')
            end_obj = datetime.strptime(week_end, '%Y-%m-%d')
            
            return start_obj <= date_obj <= end_obj
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error checking if {date_str} is in current week: {e}")
            return False
    
    def is_recent_enough(self, date_str: str, days: int = 14) -> bool:
        """Check if date is recent enough (within specified days)"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            days_diff = (self.today - date_obj).days
            return 0 <= days_diff <= days
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error checking if {date_str} is recent: {e}")
            return False
    
    def parse_date(self, date_text: str) -> Optional[str]:
        """Parse date text and return standardized date string"""
        if not date_text:
            return None
        
        date_text = date_text.lower().strip()
        
        try:
            # Try week-relative dates first
            parsed_date = self._parse_week_relative(date_text)
            if parsed_date:
                return parsed_date
            
            # Try standard date patterns
            parsed_date = self._parse_standard_date(date_text)
            if parsed_date:
                return parsed_date
            
            # Try relative expressions
            parsed_date = self._parse_relative_expressions(date_text)
            if parsed_date:
                return parsed_date
            
            return None
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error parsing date '{date_text}': {e}")
            return None
    
    def _parse_week_relative(self, date_text: str) -> Optional[str]:
        """Parse week-relative expressions"""
        try:
            for keyword, week_offset in self.week_keywords.items():
                if keyword in date_text:
                    # Calculate target week
                    target_date = self.today + timedelta(weeks=week_offset)
                    return target_date.strftime('%Y-%m-%d')
            
            return None
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error parsing week relative: {e}")
            return None
    
    def _parse_standard_date(self, date_text: str) -> Optional[str]:
        """Parse standard date formats"""
        try:
            for pattern, format_str in self.date_patterns:
                match = re.search(pattern, date_text)
                if match:
                    try:
                        groups = match.groups()
                        
                        if '%Y-%m-%d' in format_str:
                            year, month, day = groups
                            parsed_date = datetime(int(year), int(month), int(day))
                        elif '%m/%d/%Y' in format_str or '%m-%d-%Y' in format_str:
                            month, day, year = groups
                            parsed_date = datetime(int(year), int(month), int(day))
                        elif '%B %d, %Y' in format_str:
                            month_name, day, year = groups
                            month_num = self._get_month_number(month_name)
                            if month_num:
                                parsed_date = datetime(int(year), month_num, int(day))
                            else:
                                continue
                        elif '%d %B %Y' in format_str:
                            day, month_name, year = groups
                            month_num = self._get_month_number(month_name)
                            if month_num:
                                parsed_date = datetime(int(year), month_num, int(day))
                            else:
                                continue
                        else:
                            continue
                        
                        return parsed_date.strftime('%Y-%m-%d')
                        
                    except (ValueError, TypeError):
                        continue
            
            return None
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error parsing standard date: {e}")
            return None
    
    def _parse_relative_expressions(self, date_text: str) -> Optional[str]:
        """Parse relative date expressions"""
        try:
            # Today/yesterday/tomorrow
            if 'today' in date_text or 'just now' in date_text:
                return self.today.strftime('%Y-%m-%d')
            elif 'yesterday' in date_text:
                return (self.today - timedelta(days=1)).strftime('%Y-%m-%d')
            elif 'tomorrow' in date_text:
                return (self.today + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # X days ago
            days_ago_pattern = r'(\d+)\s+days?\s+ago'
            match = re.search(days_ago_pattern, date_text)
            if match:
                days = int(match.group(1))
                target_date = self.today - timedelta(days=days)
                return target_date.strftime('%Y-%m-%d')
            
            # X weeks ago
            weeks_ago_pattern = r'(\d+)\s+weeks?\s+ago'
            match = re.search(weeks_ago_pattern, date_text)
            if match:
                weeks = int(match.group(1))
                target_date = self.today - timedelta(weeks=weeks)
                return target_date.strftime('%Y-%m-%d')
            
            return None
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error parsing relative expressions: {e}")
            return None
    
    def _get_month_number(self, month_name: str) -> Optional[int]:
        """Convert month name to number"""
        try:
            month_name = month_name.lower().strip()
            return self.month_names.get(month_name)
        except Exception:
            return None
    
    def get_week_days(self, week_start_str: str) -> List[str]:
        """Get all days in a week given the start date"""
        try:
            start_date = datetime.strptime(week_start_str, '%Y-%m-%d')
            week_days = []
            
            for i in range(7):
                day = start_date + timedelta(days=i)
                week_days.append(day.strftime('%Y-%m-%d'))
            
            return week_days
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error getting week days: {e}")
            return []
    
    def get_week_number(self, date_str: str) -> Optional[int]:
        """Get ISO week number for a date"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.isocalendar()[1]
        except Exception as e:
            print(f"[WeekAnalyzer] Error getting week number: {e}")
            return None
    
    def is_same_week(self, date1_str: str, date2_str: str) -> bool:
        """Check if two dates are in the same week"""
        try:
            week1_start, week1_end = self.get_week_range(date1_str)
            week2_start, week2_end = self.get_week_range(date2_str)
            
            return week1_start == week2_start and week1_end == week2_end
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error comparing weeks: {e}")
            return False
    
    def get_previous_week_range(self) -> Tuple[str, str]:
        """Get previous week's date range"""
        try:
            current_start, _ = self.get_current_week_range()
            current_start_obj = datetime.strptime(current_start, '%Y-%m-%d')
            
            prev_week_start = current_start_obj - timedelta(days=7)
            prev_week_end = prev_week_start + timedelta(days=6)
            
            return (
                prev_week_start.strftime('%Y-%m-%d'),
                prev_week_end.strftime('%Y-%m-%d')
            )
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error getting previous week range: {e}")
            today_str = self.today.strftime('%Y-%m-%d')
            return (today_str, today_str)
    
    def get_next_week_range(self) -> Tuple[str, str]:
        """Get next week's date range"""
        try:
            current_start, _ = self.get_current_week_range()
            current_start_obj = datetime.strptime(current_start, '%Y-%m-%d')
            
            next_week_start = current_start_obj + timedelta(days=7)
            next_week_end = next_week_start + timedelta(days=6)
            
            return (
                next_week_start.strftime('%Y-%m-%d'),
                next_week_end.strftime('%Y-%m-%d')
            )
            
        except Exception as e:
            print(f"[WeekAnalyzer] Error getting next week range: {e}")
            today_str = self.today.strftime('%Y-%m-%d')
            return (today_str, today_str)
