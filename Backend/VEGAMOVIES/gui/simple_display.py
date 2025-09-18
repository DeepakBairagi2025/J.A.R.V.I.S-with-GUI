"""
Simple movie display without GUI dependencies
Shows movie information in a clean, visual format with auto-slideshow
"""

import time
import os
import sys
from typing import List, Dict, Any
import threading
import requests
from pathlib import Path

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_movie_card(movie: Dict[str, Any], index: int, total: int):
    """Display a single movie card in console"""
    clear_screen()
    
    # Header
    print("🎬" * 20)
    print(f"   VEGAMOVIES MOVIE GALLERY   ({index + 1}/{total})")
    print("🎬" * 20)
    print()
    
    # Movie details
    title = movie.get('title', 'Unknown Title')
    # Clean title (remove "Download" prefix and file info)
    clean_title = title.replace('Download ', '').split(' (')[0].split(' WEB-DL')[0].split(' 480p')[0]
    
    # Extract year from title if not available
    year = movie.get('year', '')
    if not year:
        import re
        year_match = re.search(r'\((\d{4})\)', title)
        year = year_match.group(1) if year_match else '2025'
    
    # Extract quality from title
    quality = movie.get('quality', '')
    if not quality:
        if '1080p' in title:
            quality = '1080p HD'
        elif '720p' in title:
            quality = '720p HD'
        elif '480p' in title:
            quality = '480p'
        else:
            quality = 'HD'
    
    genre = movie.get('genre', 'Action/Drama')
    if not genre:
        genre = 'Action/Drama'
    
    image_url = movie.get('image_url', '')
    
    # Display movie poster as ASCII art (simple representation)
    print("┌" + "─" * 50 + "┐")
    print("│" + " " * 20 + "🎬 POSTER" + " " * 19 + "│")
    print("│" + " " * 50 + "│")
    print("│" + f"  {clean_title[:44]:^44}  " + "│")
    print("│" + " " * 50 + "│")
    print("│" + f"  Year: {year}" + " " * (44 - len(f"Year: {year}")) + "│")
    print("│" + f"  Genre: {genre[:38]}" + " " * (44 - len(f"Genre: {genre[:38]}")) + "│")
    print("│" + f"  Quality: {quality}" + " " * (44 - len(f"Quality: {quality}")) + "│")
    print("│" + " " * 50 + "│")
    if image_url:
        print("│" + f"  Image: Available" + " " * 32 + "│")
    else:
        print("│" + f"  Image: Not Available" + " " * 28 + "│")
    print("│" + " " * 50 + "│")
    print("└" + "─" * 50 + "┘")
    print()
    
    # Progress bar for slideshow
    print("📊 Slideshow Progress:")
    print("▶ Auto-advancing in 7 seconds...")
    print("⏸ Press Ctrl+C to stop slideshow")
    print()
    
    # Source info
    print(f"🌐 Source: Vegamovies.menu")
    print(f"🔗 Image URL: {image_url[:60]}..." if len(image_url) > 60 else f"🔗 Image URL: {image_url}")

def show_progress_bar(duration: int = 7):
    """Show a progress bar for the given duration"""
    print("\n" + "─" * 50)
    for i in range(duration):
        progress = "█" * (i + 1) + "░" * (duration - i - 1)
        print(f"\r⏱️  [{progress}] {i + 1}/{duration}s", end="", flush=True)
        time.sleep(1)
    print("\n" + "─" * 50)

def show_movie_slideshow(movies: List[Dict[str, Any]], title: str = "Vegamovies Movies"):
    """Show movie slideshow in console"""
    if not movies:
        print("❌ No movies to display")
        return
    
    print(f"\n🎬 Starting {title} slideshow...")
    print(f"📊 Total movies: {len(movies)}")
    print("⏸ Press Ctrl+C anytime to stop\n")
    
    try:
        for i, movie in enumerate(movies):
            display_movie_card(movie, i, len(movies))
            
            # Show progress bar for 7 seconds
            try:
                show_progress_bar(7)
            except KeyboardInterrupt:
                print(f"\n\n⏹️ Slideshow stopped by user")
                break
        
        # Show completion message
        clear_screen()
        print("🎬" * 20)
        print("   SLIDESHOW COMPLETED!")
        print("🎬" * 20)
        print(f"\n✅ Displayed {len(movies)} movies")
        print("🎯 All movies from Vegamovies.menu")
        print("\nPress Enter to continue...")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️ Slideshow interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during slideshow: {e}")

def show_vegamovies_display(movies: List[Dict[str, Any]], title: str = "Vegamovies Movies"):
    """Main function to show Vegamovies movie display"""
    try:
        print(f"\n🎬 {title}")
        print("=" * 60)
        
        if not movies:
            print("❌ No movies available to display")
            return False
        
        # Ask user for display preference
        print(f"📊 Found {len(movies)} movies")
        print("\nDisplay Options:")
        print("1. 🎬 Auto Slideshow (7s per movie)")
        print("2. 📝 Quick Text List")
        print("3. ⏭️  Skip Display")
        
        try:
            choice = input("\nEnter choice (1-3, default=1): ").strip()
            if not choice:
                choice = "1"
        except:
            choice = "1"
        
        if choice == "1":
            show_movie_slideshow(movies, title)
        elif choice == "2":
            show_quick_text_list(movies)
        else:
            print("⏭️ Display skipped")
        
        return True
        
    except Exception as e:
        print(f"❌ Error showing movie display: {e}")
        return False

def show_quick_text_list(movies: List[Dict[str, Any]]):
    """Show quick text list of movies"""
    print("\n📝 Quick Movie List:")
    print("=" * 60)
    
    for i, movie in enumerate(movies[:10]):  # Show first 10
        title = movie.get('title', 'Unknown Title')
        clean_title = title.replace('Download ', '').split(' (')[0].split(' WEB-DL')[0].split(' 480p')[0]
        
        year = movie.get('year', '')
        if not year:
            import re
            year_match = re.search(r'\((\d{4})\)', title)
            year = year_match.group(1) if year_match else '2025'
        
        print(f"🎬 {i+1:2d}. {clean_title[:50]} ({year})")
    
    if len(movies) > 10:
        print(f"\n... and {len(movies) - 10} more movies")
    
    print(f"\n✅ Total: {len(movies)} movies from Vegamovies.menu")

# Test function
if __name__ == "__main__":
    # Sample movie data for testing
    sample_movies = [
        {
            'title': 'Download Avengers: Endgame (2019) 1080p',
            'year': '2019',
            'genre': 'Action/Adventure',
            'quality': '1080p HD',
            'image_url': 'https://example.com/poster1.jpg'
        },
        {
            'title': 'Download Spider-Man: No Way Home (2021) 720p',
            'year': '2021', 
            'genre': 'Action/Adventure',
            'quality': '720p HD',
            'image_url': 'https://example.com/poster2.jpg'
        }
    ]
    
    show_vegamovies_display(sample_movies, "Test Movies")
