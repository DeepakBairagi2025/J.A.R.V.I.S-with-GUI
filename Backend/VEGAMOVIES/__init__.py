# Vegamovies Automation Module
# Main package for Vegamovies website automation and content extraction

__version__ = "1.0.0"
__author__ = "J.A.R.V.I.S System"

from .core.vegamovies_engine import VegamoviesEngine
from .scrapers.current_date_movies.current_date_movies import CurrentDateMovies
from .scrapers.current_week_movies.current_week_movies import CurrentWeekMovies

__all__ = [
    'VegamoviesEngine',
    'CurrentDateMovies', 
    'CurrentWeekMovies'
]
