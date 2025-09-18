"""
Vegamovies Test Script - Standalone testing for Vegamovies automation
Run this script to test all Vegamovies functionality before integration
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from Backend.VEGAMOVIES.core.vegamovies_engine import VegamoviesEngine

def test_basic_navigation():
    """Test basic navigation to Vegamovies"""
    print("\n" + "="*60)
    print("🌐 TESTING BASIC NAVIGATION")
    print("="*60)
    
    engine = VegamoviesEngine()
    
    try:
        success = engine.navigate_to_vegamovies()
        if success:
            print("✅ Successfully navigated to Vegamovies")
            print(f"📍 Current URL: {engine.driver.current_url}")
            time.sleep(3)  # Let user see the page
            return True
        else:
            print("❌ Failed to navigate to Vegamovies")
            return False
            
    except Exception as e:
        print(f"❌ Navigation test failed: {e}")
        return False
    finally:
        # Don't cleanup yet, keep browser open for next tests
        pass

def test_search_functionality(engine, search_term="Avengers"):
    """Test search functionality with ad handling"""
    print("\n" + "="*60)
    print(f"🔍 TESTING SEARCH: '{search_term}'")
    print("="*60)
    
    try:
        success = engine.search_movie(search_term)
        if success:
            print(f"✅ Successfully searched for '{search_term}'")
            print(f"📍 Current URL: {engine.driver.current_url}")
            time.sleep(5)  # Let user see search results
            return True
        else:
            print(f"❌ Search failed for '{search_term}'")
            return False
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def test_current_date_movies(engine):
    """Test current date movies extraction"""
    print("\n" + "="*60)
    print("📅 TESTING CURRENT DATE MOVIES")
    print("="*60)
    
    try:
        movies = engine.get_current_date_movies()
        
        if movies:
            print(f"✅ Found {len(movies)} current date movies")
            
            # Show GUI popup with movies
            try:
                from Backend.VEGAMOVIES.gui.vegamovies_popup import show_vegamovies_popup
                print("🎬 Opening movie gallery popup with images...")
                print("📝 Note: Popup will show actual movie posters and auto-slideshow")
                show_vegamovies_popup(movies, "Current Date Movies - Vegamovies")
                print("✅ Movie gallery closed")
            except Exception as gui_error:
                print(f"⚠️ GUI popup failed: {gui_error}")
                print("📝 Trying simple display fallback...")
                
                try:
                    from Backend.VEGAMOVIES.gui.simple_display import show_vegamovies_display
                    show_vegamovies_display(movies, "Current Date Movies - Vegamovies")
                except Exception as display_error:
                    print(f"⚠️ Simple display also failed: {display_error}")
                    print("📝 Falling back to basic text display...")
                    
                    # Fallback: Display first 3 movies in text
                    for i, movie in enumerate(movies[:3]):
                        print(f"\n🎬 Movie {i+1}:")
                        print(f"   Title: {movie.get('title', 'N/A')}")
                        print(f"   Year: {movie.get('year', 'N/A')}")
                        print(f"   Genre: {movie.get('genre', 'N/A')}")
                        print(f"   Quality: {movie.get('quality', 'N/A')}")
                        print(f"   Image: {movie.get('image_url', 'N/A')[:50]}...")
                    
                    if len(movies) > 3:
                        print(f"\n... and {len(movies) - 3} more movies")
            
            return True
        else:
            print("⚠️ No current date movies found")
            return False
            
    except Exception as e:
        print(f"❌ Current date movies test failed: {e}")
        return False

def test_current_week_movies(engine):
    """Test current week movies extraction"""
    print("\n" + "="*60)
    print("📆 TESTING CURRENT WEEK MOVIES")
    print("="*60)
    
    try:
        movies = engine.get_current_week_movies()
        
        if movies:
            print(f"✅ Found {len(movies)} current week movies")
            
            # Show GUI popup with movies
            try:
                from Backend.VEGAMOVIES.gui.vegamovies_popup import show_vegamovies_popup
                print("🎬 Opening movie gallery popup with images...")
                print("📝 Note: Popup will show actual movie posters and auto-slideshow")
                show_vegamovies_popup(movies, "Current Week Movies - Vegamovies")
                print("✅ Movie gallery closed")
            except Exception as gui_error:
                print(f"⚠️ GUI popup failed: {gui_error}")
                print("📝 Trying simple display fallback...")
                
                try:
                    from Backend.VEGAMOVIES.gui.simple_display import show_vegamovies_display
                    show_vegamovies_display(movies, "Current Week Movies - Vegamovies")
                except Exception as display_error:
                    print(f"⚠️ Simple display also failed: {display_error}")
                    print("📝 Falling back to basic text display...")
                    
                    # Fallback: Display first 3 movies in text
                    for i, movie in enumerate(movies[:3]):
                        print(f"\n🎬 Movie {i+1}:")
                        print(f"   Title: {movie.get('title', 'N/A')}")
                        print(f"   Year: {movie.get('year', 'N/A')}")
                        print(f"   Genre: {movie.get('genre', 'N/A')}")
                        print(f"   Quality: {movie.get('quality', 'N/A')}")
                        print(f"   Week Start: {movie.get('week_start', 'N/A')}")
                        print(f"   Week End: {movie.get('week_end', 'N/A')}")
                    
                    if len(movies) > 3:
                        print(f"\n... and {len(movies) - 3} more movies")
            
            return True
        else:
            print("⚠️ No current week movies found")
            return False
            
    except Exception as e:
        print(f"❌ Current week movies test failed: {e}")
        return False

def test_cache_functionality(engine):
    """Test caching system"""
    print("\n" + "="*60)
    print("💾 TESTING CACHE FUNCTIONALITY")
    print("="*60)
    
    try:
        # Test cache stats
        stats = engine.cache_manager.get_stats()
        print(f"📊 Cache Stats:")
        print(f"   Total entries: {stats.get('total_entries', 0)}")
        print(f"   Active entries: {stats.get('active_entries', 0)}")
        print(f"   Expired entries: {stats.get('expired_entries', 0)}")
        print(f"   Estimated size: {stats.get('estimated_size_bytes', 0)} bytes")
        
        # Test cache operations
        test_key = "test_cache_key"
        test_value = {"test": "data", "timestamp": time.time()}
        
        # Set cache
        engine.cache_manager.set(test_key, test_value, ttl=60)
        print(f"✅ Set cache entry: {test_key}")
        
        # Get cache
        retrieved = engine.cache_manager.get(test_key)
        if retrieved == test_value:
            print(f"✅ Retrieved cache entry successfully")
        else:
            print(f"❌ Cache retrieval failed")
        
        # Clean up test cache
        engine.cache_manager.delete(test_key)
        print(f"✅ Cleaned up test cache entry")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False

def run_interactive_test():
    """Run interactive test with user choices"""
    print("\n" + "🎬"*20)
    print("VEGAMOVIES AUTOMATION TEST SUITE")
    print("🎬"*20)
    
    engine = None
    
    try:
        # Test 1: Basic Navigation
        if not test_basic_navigation():
            print("\n❌ Basic navigation failed. Cannot continue.")
            return
        
        # Get engine instance for subsequent tests
        engine = VegamoviesEngine()
        if not engine.navigate_to_vegamovies():
            print("\n❌ Could not establish engine connection.")
            return
        
        # Interactive menu
        while True:
            print("\n" + "="*60)
            print("🎯 CHOOSE TEST TO RUN:")
            print("="*60)
            print("1. 🔍 Test Search Functionality")
            print("2. 📅 Test Current Date Movies")
            print("3. 📆 Test Current Week Movies") 
            print("4. 💾 Test Cache System")
            print("5. 🔄 Run All Tests")
            print("6. 🌐 Navigate to Vegamovies (refresh)")
            print("7. ❌ Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                search_term = input("Enter movie/series name to search (or press Enter for 'Avengers'): ").strip()
                if not search_term:
                    search_term = "Avengers"
                test_search_functionality(engine, search_term)
                
            elif choice == "2":
                test_current_date_movies(engine)
                
            elif choice == "3":
                test_current_week_movies(engine)
                
            elif choice == "4":
                test_cache_functionality(engine)
                
            elif choice == "5":
                print("\n🚀 RUNNING ALL TESTS...")
                test_search_functionality(engine, "Spider-Man")
                test_current_date_movies(engine)
                test_current_week_movies(engine)
                test_cache_functionality(engine)
                print("\n✅ ALL TESTS COMPLETED!")
                
            elif choice == "6":
                engine.navigate_to_vegamovies()
                
            elif choice == "7":
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-7.")
            
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
    
    finally:
        # Cleanup
        if engine:
            print("\n🧹 Cleaning up...")
            engine.cleanup()
        print("\n👋 Test suite finished!")

def run_quick_test():
    """Run a quick automated test"""
    print("\n🚀 RUNNING QUICK AUTOMATED TEST...")
    
    engine = VegamoviesEngine()
    results = {
        "navigation": False,
        "search": False,
        "current_date": False,
        "current_week": False,
        "cache": False
    }
    
    try:
        # Test navigation
        results["navigation"] = engine.navigate_to_vegamovies()
        
        if results["navigation"]:
            # Test search
            results["search"] = engine.search_movie("Batman")
            
            # Test current date movies
            movies = engine.get_current_date_movies()
            results["current_date"] = len(movies) > 0
            
            # Test current week movies
            movies = engine.get_current_week_movies()
            results["current_week"] = len(movies) > 0
            
            # Test cache
            results["cache"] = test_cache_functionality(engine)
        
        # Print results
        print("\n" + "="*60)
        print("📊 QUICK TEST RESULTS")
        print("="*60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        total_passed = sum(results.values())
        print(f"\nOverall: {total_passed}/5 tests passed")
        
        if total_passed == 5:
            print("🎉 ALL TESTS PASSED! Vegamovies automation is working perfectly!")
        elif total_passed >= 3:
            print("⚠️ Most tests passed. Some features may need adjustment.")
        else:
            print("❌ Multiple tests failed. Check your setup and dependencies.")
    
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
    
    finally:
        engine.cleanup()

if __name__ == "__main__":
    print("🎬 VEGAMOVIES AUTOMATION TESTER")
    print("Choose test mode:")
    print("1. Interactive Test (recommended)")
    print("2. Quick Automated Test")
    
    mode = input("Enter choice (1 or 2): ").strip()
    
    if mode == "2":
        run_quick_test()
    else:
        run_interactive_test()
