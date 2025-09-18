"""
Date Parser - Intelligent date parsing for Vegamovies content
Handles various date formats and relative date expressions
"""

import re
from datetime import datetime, timedelta
from typing import Optional, List

class DateParser:
    """Parses various date formats found on Vegamovies"""
    
    def __init__(self):
        self.today = datetime.now()
        
        # Common date patterns
        self.date_patterns = [
            # Standard formats
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', '%m-%d-%Y'),
            
            # Month name formats
            (r'(\w+)\s+(\d{1,2}),\s+(\d{4})', '%B %d, %Y'),
            (r'(\d{1,2})\s+(\w+)\s+(\d{4})', '%d %B %Y'),
            (r'(\w+)\s+(\d{4})', '%B %Y'),
            
            # Abbreviated formats
            (r'(\w{3})\s+(\d{1,2}),\s+(\d{4})', '%b %d, %Y'),
            (r'(\d{1,2})\s+(\w{3})\s+(\d{4})', '%d %b %Y'),
        ]
        
        # Relative date keywords
        self.relative_dates = {
            'today': 0,
            'yesterday': -1,
            'tomorrow': 1,
            'just now': 0,
            'few minutes ago': 0,
            'hour ago': 0,
            'hours ago': 0,
            'day ago': -1,
            'days ago': -1,
            'week ago': -7,
            'weeks ago': -7,
            'month ago': -30,
            'months ago': -30
        }
        
        # Month name mappings
        self.month_names = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
    
    def parse_date(self, date_text: str) -> Optional[str]:
        """Parse date text and return standardized date string (YYYY-MM-DD)"""
        if not date_text:
            return None
        
        date_text = date_text.lower().strip()
        
        try:
            # Try relative dates first
            parsed_date = self._parse_relative_date(date_text)
            if parsed_date:
                return parsed_date
            
            # Try standard date patterns
            parsed_date = self._parse_standard_date(date_text)
            if parsed_date:
                return parsed_date
            
            # Try extracting numbers for relative dates
            parsed_date = self._parse_numeric_relative(date_text)
            if parsed_date:
                return parsed_date
            
            return None
            
        except Exception as e:
            print(f"[DateParser] Error parsing date '{date_text}': {e}")
            return None
    
    def _parse_relative_date(self, date_text: str) -> Optional[str]:
        """Parse relative date expressions"""
        try:
            for keyword, days_offset in self.relative_dates.items():
                if keyword in date_text:
                    target_date = self.today + timedelta(days=days_offset)
                    return target_date.strftime('%Y-%m-%d')
            
            return None
            
        except Exception as e:
            print(f"[DateParser] Error parsing relative date: {e}")
            return None
    
    def _parse_standard_date(self, date_text: str) -> Optional[str]:
        """Parse standard date formats"""
        try:
            for pattern, format_str in self.date_patterns:
                match = re.search(pattern, date_text)
                if match:
                    try:
                        # Handle different group arrangements
                        groups = match.groups()
                        
                        if '%Y-%m-%d' in format_str:
                            year, month, day = groups
                            parsed_date = datetime(int(year), int(month), int(day))
                        elif '%m/%d/%Y' in format_str or '%m-%d-%Y' in format_str:
                            month, day, year = groups
                            parsed_date = datetime(int(year), int(month), int(day))
                        elif '%B %d, %Y' in format_str or '%b %d, %Y' in format_str:
                            month_name, day, year = groups
                            month_num = self._get_month_number(month_name)
                            if month_num:
                                parsed_date = datetime(int(year), month_num, int(day))
                            else:
                                continue
                        elif '%d %B %Y' in format_str or '%d %b %Y' in format_str:
                            day, month_name, year = groups
                            month_num = self._get_month_number(month_name)
                            if month_num:
                                parsed_date = datetime(int(year), month_num, int(day))
                            else:
                                continue
                        elif '%B %Y' in format_str:
                            month_name, year = groups
                            month_num = self._get_month_number(month_name)
                            if month_num:
                                parsed_date = datetime(int(year), month_num, 1)
                            else:
                                continue
                        else:
                            continue
                        
                        return parsed_date.strftime('%Y-%m-%d')
                        
                    except (ValueError, TypeError):
                        continue
            
            return None
            
        except Exception as e:
            print(f"[DateParser] Error parsing standard date: {e}")
            return None
    
    def _parse_numeric_relative(self, date_text: str) -> Optional[str]:
        """Parse numeric relative dates like '2 days ago', '1 week ago'"""
        try:
            # Pattern for "X time_unit ago"
            pattern = r'(\d+)\s+(minute|hour|day|week|month)s?\s+ago'
            match = re.search(pattern, date_text)
            
            if match:
                number = int(match.group(1))
                unit = match.group(2)
                
                if unit == 'minute':
                    target_date = self.today
                elif unit == 'hour':
                    target_date = self.today
                elif unit == 'day':
                    target_date = self.today - timedelta(days=number)
                elif unit == 'week':
                    target_date = self.today - timedelta(weeks=number)
                elif unit == 'month':
                    target_date = self.today - timedelta(days=number * 30)
                else:
                    return None
                
                return target_date.strftime('%Y-%m-%d')
            
            return None
            
        except Exception as e:
            print(f"[DateParser] Error parsing numeric relative date: {e}")
            return None
    
    def _get_month_number(self, month_name: str) -> Optional[int]:
        """Convert month name to number"""
        try:
            month_name = month_name.lower().strip()
            return self.month_names.get(month_name)
        except Exception:
            return None
    
    def is_today(self, date_text: str) -> bool:
        """Check if date text represents today"""
        parsed_date = self.parse_date(date_text)
        if parsed_date:
            today_str = self.today.strftime('%Y-%m-%d')
            return parsed_date == today_str
        return False
    
    def is_recent(self, date_text: str, days_threshold: int = 7) -> bool:
        """Check if date is within recent threshold"""
        parsed_date = self.parse_date(date_text)
        if parsed_date:
            try:
                date_obj = datetime.strptime(parsed_date, '%Y-%m-%d')
                days_diff = (self.today - date_obj).days
                return 0 <= days_diff <= days_threshold
            except ValueError:
                return False
        return False
    
    def get_date_variants(self, date_str: str) -> List[str]:
        """Get different format variants of a date"""
        variants = []
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Add different format variants
            variants.extend([
                date_obj.strftime('%Y-%m-%d'),
                date_obj.strftime('%m/%d/%Y'),
                date_obj.strftime('%d/%m/%Y'),
                date_obj.strftime('%B %d, %Y'),
                date_obj.strftime('%b %d, %Y'),
                date_obj.strftime('%d %B %Y'),
                date_obj.strftime('%d %b %Y'),
            ])
            
            # Add relative variants if it's recent
            days_diff = (self.today - date_obj).days
            if days_diff == 0:
                variants.extend(['today', 'just now'])
            elif days_diff == 1:
                variants.extend(['yesterday', '1 day ago'])
            elif days_diff < 7:
                variants.append(f'{days_diff} days ago')
            
        except ValueError:
            pass
        
        return list(set(variants))  # Remove duplicates
