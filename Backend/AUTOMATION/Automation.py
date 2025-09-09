from urllib import response
from AppOpener import close, open as appopen # Import functions to open and close apps.
from webbrowser import open as webopen # Import web browser functionality.
from pywhatkit import search, playonyt # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values # Import dotenv_values to manage environment variables.
from bs4 import BeautifulSoup # Import BeautifulSoup for parsing HTML content.
from rich import print # Import rich print for enhanced console output.
from groq import Groq # Import Groq for AI chat functionality.
import webbrowser # Import webbrowser for opening URLs.
import subprocess # Import subprocess for interacting with the system.
import requests # Import requests for making HTTP requests.
import keyboard # Import keyboard for simulating keyboard events.
import asyncio # Import asyncio for asynchronous programming.
import os # Import os for operating system interactions.
from pathlib import Path # Import Path to resolve project root reliably.
import re # Import re for normalizing/cleaning commands
from Backend.TEXT_TO_SPEECH.TextToSpeech import TextToSpeech
from .utils import extract_title_from_command
import pyautogui  # For hover/mouse move without clicking

from .ScreenMonitor import (
    start_screen_monitor,
    stop_screen_monitor,
    get_screen_monitor
)


# Resolve project root (two levels up from this file) and load environment variables.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
env_vars = dotenv_values(str(PROJECT_ROOT / ".env"))
# Retrieve the Groq API key (prefer .env, fallback to OS env var)
GroqAPIKey = (env_vars.get("GroqAPIKey") or os.getenv("GroqAPIKey") or "").strip()
if not GroqAPIKey:
    raise RuntimeError("GroqAPIKey not found. Add it to your .env at project root or set the OS env var GroqAPIKey.")

# Define CSS classes for parsing specific elements in HTML content.
classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
           "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table",
           "dDoNo ikb4Bb gsrt", "sXLaOe",
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b",]

# Define a user-agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything I can assist you with.",
    "I'm at your service for any additional questions or support you many need-don't hesitate to ask.",
]

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot. Be tolerant if Username env var is missing.
user_name = env_vars.get("Username") or os.getenv("USERNAME") or os.getenv("UserName") or "User"
SystemChatBot = [{"role": "user", "content": f"Hello, I am {user_name}, You're a content writer. You have to write content like letter, codes, applications, essays, notes, songs, poem etc."}]

# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic) # Use pywhatkit's search function to perform a Google search.
    return True # Indicate success.

# Function to generate content using the API and save it to a file.
def Content(Topic):

    # Nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = "notepad.exe" # default text editor
        subprocess.Popen([default_text_editor, File]) # Open the file in Notepad.

    # Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"}) # Add user prompt to messages.

        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant", # Updated model (Mixtral deprecated)
                messages=SystemChatBot + messages, # Include system instructions and chat history.
                max_tokens=2048, # Limit the maximum tokens in the response.
                temperature=0.7, # Adjust response randomness.
                top_p=1, # Use nucleus sampling for response diversity.
                stream=True, # Enable streaming for real-time responses.
                stop=None # Allow the model to determine stopping conditions.
            )

            Answer = "" # Initialize an empty string for the response.

            # Process streamed response chunks.
            for chunk in completion:
                if chunk.choices[0].delta.content: # Check for content in the current chunk.
                    Answer += chunk.choices[0].delta.content # Append the content to the answer.

            Answer = Answer.replace("</s>", "") # Remove unwanted tokens from the response.
            messages.append({"role": "assistant", "content": Answer}) # Add the AI's response to messages.
            return Answer

        except Exception as e:
            print(f"[red]Groq API error:[/red] {e}")
            return "Sorry, I couldn't generate content at the moment."

    Topic: str = Topic.replace("Content ", "") # Remove "Content " From the topic.
    ContentByAI = ContentWriterAI(Topic) # Generate content using the AI.

    # Save the generated content to a text file under the project's Data directory.
    data_dir = PROJECT_ROOT / "Data"
    data_dir.mkdir(parents=True, exist_ok=True)
    out_path = data_dir / f"{Topic.lower().replace(' ','')}.text"
    with open(out_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(str(out_path)) # Open the file in Notepad.
    return True # Indicate success.

# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}" # Construct the YouTube search URL.
    webbrowser.open(Url4Search) # Open the search URL in the default web browser.
    return True # Indicate success.


# Function to play a video on YouTube.
def PlayYouTube(query):
    playonyt(query) # Use pywhatkit's playonyt function to play the video.
    return True # Indicate success.

# Function to open an application or a relevant webpage.
def OpenApp(app, sess=requests.session()):
    
    # Quick direct-URL handling for popular sites to avoid search result pages
    app_key = app.strip().lower()
    website_keywords = {
        "instagram": "https://www.instagram.com/",
        "instagram.com": "https://www.instagram.com/",
        "insta": "https://www.instagram.com/",
        "facebook": "https://www.facebook.com/",
        "facebook.com": "https://www.facebook.com/",
        "fb": "https://www.facebook.com/",
        "youtube": "https://www.youtube.com/",
        "youtube.com": "https://www.youtube.com/",
        "yt": "https://www.youtube.com/",
        "google": "https://www.google.com/",
        "google.com": "https://www.google.com/",
        "g": "https://www.google.com/",
        "gmail": "https://mail.google.com/",
        "gmail.com": "https://mail.google.com/",
        "mail": "https://mail.google.com/",
        "whatsapp": "https://web.whatsapp.com/",
        "whatsapp.com": "https://web.whatsapp.com/",
        "wh": "https://web.whatsapp.com/",
        "twitter": "https://twitter.com/",
        "twitter.com": "https://twitter.com/",
        "tw": "https://twitter.com/",
        "linkedin": "https://www.linkedin.com/",
        "linkedin.com": "https://www.linkedin.com/",
        "ln": "https://www.linkedin.com/",
        "telegram": "https://web.telegram.org/",
        "telegram.com": "https://web.telegram.org/",
        "tg": "https://web.telegram.org/",
        "snapchat": "https://www.snapchat.com/",
        "snapchat.com": "https://www.snapchat.com/",
        "snap": "https://www.snapchat.com/",
        "github": "https://github.com/",
        "github.com": "https://github.com/",
        "git": "https://github.com/",
        "cohere": "https://cohere.com/",
        "cohere.com": "https://cohere.com/",
        "co": "https://cohere.com/",
        "chatgpt": "https://chat.openai.com/",
        "chatgpt.com": "https://chat.openai.com/",
        "aisaver": "https://aisaver.com/",
        "aisaver.com": "https://aisaver.com/",
        "magichour": "https://magichour.com/",
        "magichour.com": "https://magichour.com/",
        'google': 'https://www.google.com',
        'youtube': 'https://www.youtube.com',
        'facebook': 'https://www.facebook.com',
        'twitter': 'https://www.twitter.com',
        'instagram': 'https://www.instagram.com',
        'linkedin': 'https://www.linkedin.com',
        'github': 'https://www.github.com',
        'stackoverflow': 'https://stackoverflow.com',
        'reddit': 'https://www.reddit.com',
        'wikipedia': 'https://www.wikipedia.org',
        'quora': 'https://www.quora.com',
        'amazon': 'https://www.amazon.com',
        'flipkart': 'https://www.flipkart.com',
        'snapdeal': 'https://www.snapdeal.com',
        'myntra': 'https://www.myntra.com',
        'udemy': 'https://www.udemy.com',
        'coursera': 'https://www.coursera.org',
        'edx': 'https://www.edx.org',
        'khanacademy': 'https://www.khanacademy.org',
        'medium': 'https://medium.com',
        'netflix': 'https://www.netflix.com',
        'hotstar': 'https://www.hotstar.com',
        'primevideo': 'https://www.primevideo.com',
        'zomato': 'https://www.zomato.com',
        'swiggy': 'https://www.swiggy.com',
        'canva': 'https://www.canva.com',
        'notion': 'https://www.notion.so',
        'gmail': 'https://mail.google.com',
        'yahoo': 'https://www.yahoo.com',
        'duckduckgo': 'https://www.duckduckgo.com',
        'bing': 'https://www.bing.com',
        'zoho': 'https://www.zoho.com',
        'pixabay': 'https://www.pixabay.com',
        'pexels': 'https://www.pexels.com',
        'unsplash': 'https://www.unsplash.com',
        'wordpress': 'https://www.wordpress.com',
        'blogger': 'https://www.blogger.com',
        'tumblr': 'https://www.tumblr.com',
        'trello': 'https://www.trello.com',
        'dropbox': 'https://www.dropbox.com',
        'drive': 'https://drive.google.com',
        'skype': 'https://www.skype.com',
        'zoom': 'https://zoom.us',
        'meet': 'https://meet.google.com',
        'figma': 'https://www.figma.com',
        'codepen': 'https://codepen.io',
        'replit': 'https://replit.com',
        'w3schools': 'https://www.w3schools.com',
        'geeksforgeeks': 'https://www.geeksforgeeks.org',
        'tutorialspoint': 'https://www.tutorialspoint.com',
        'udacity': 'https://www.udacity.com',
        'futurelearn': 'https://www.futurelearn.com',
        'javatpoint': 'https://www.javatpoint.com',
        'crunchyroll': 'https://www.crunchyroll.com',
        'openai': 'https://www.openai.com',
        'codeacademy': 'https://www.codecademy.com',
        'freecodecamp': 'https://www.freecodecamp.org',
        'codeforces': 'https://codeforces.com',
        'atcoder': 'https://atcoder.jp',
        'leetcode': 'https://leetcode.com',
        'hackerank': 'https://www.hackerrank.com',
        'hackernews': 'https://news.ycombinator.com',
        'producthunt': 'https://www.producthunt.com',
        'techcrunch': 'https://techcrunch.com',
        'thenextweb': 'https://thenextweb.com',
        'wired': 'https://www.wired.com',
        'cnn': 'https://www.cnn.com',
        'bbc': 'https://www.bbc.com',
        'ndtv': 'https://www.ndtv.com',
        'indiatimes': 'https://www.indiatimes.com',
        'moneycontrol': 'https://www.moneycontrol.com',
        'groww': 'https://www.groww.in',
        'zerodha': 'https://www.zerodha.com',
        'coinmarketcap': 'https://coinmarketcap.com',
        'tradingview': 'https://www.tradingview.com',
        'spotify': 'https://www.spotify.com',
        'soundcloud': 'https://soundcloud.com',
        'gaana': 'https://gaana.com',
        'wynk': 'https://wynk.in',
        'jiosaavn': 'https://www.jiosaavn.com',
        'telegram': 'https://web.telegram.org',
        'whatsapp': 'https://web.whatsapp.com',
        'discord': 'https://discord.com',
        'tiktok': 'https://www.tiktok.com',
        'snapchat': 'https://www.snapchat.com',
        'glassdoor': 'https://www.glassdoor.com',
        'naukri': 'https://www.naukri.com',
        'indeed': 'https://www.indeed.com',
        'monster': 'https://www.monster.com',
        'internshala': 'https://internshala.com',
        'timesjobs': 'https://www.timesjobs.com',
        'freelancer': 'https://www.freelancer.com',
        'fiverr': 'https://www.fiverr.com',
        'upwork': 'https://www.upwork.com',
        'behance': 'https://www.behance.net',
        'dribbble': 'https://dribbble.com',
        'envato': 'https://www.envato.com',
        'themeforest': 'https://themeforest.net',
        'githubpages': 'https://pages.github.com',
        'netlify': 'https://www.netlify.com',
        'vercel': 'https://vercel.com',
        'cloudflare': 'https://www.cloudflare.com',
        'aws': 'https://aws.amazon.com',
        'azure': 'https://azure.microsoft.com',
        'gcp': 'https://cloud.google.com',
    }
    for kw, url in website_keywords.items():
        if kw in app_key:
            webopen(url)
            return True
    
    try:
        appopen(app, match_closest=False, output=True, throw_error=True) # Attempt to open the application without nearest-match.
        return True # Indicate success.
    
    except:
        # Nested function to extract links from HTML content.
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser') # Parse the HTML content.
            # Primary selector (original): specific jsname anchors
            links = [link.get('href') for link in soup.find_all('a', {'jsname': 'UWckNb'}) if link.get('href')]
            if links:
                return links
            # Fallback selector: standard Google result anchors starting with /url?q=
            fallback_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/url?q=') and 'webcache' not in href and 'translate.google' not in href:
                    # Decode target URL from Google's redirect without adding new imports
                    try:
                        target = href.split('/url?q=', 1)[1].split('&', 1)[0]
                        target = requests.utils.unquote(target)
                        if target.startswith('http'):
                            fallback_links.append(target)
                    except Exception:
                        pass
            return fallback_links
        
        # Nested function to perform a Google search and retrieve HTML.
        def search_google(query):
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}" # Construct the Google search URL with URL-encoded spaces.
            headers = { "User-Agent" :useragent}
            response = sess.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results.")
                return None
            
        html = search_google(app) # Perform a Google search for the app.

        if html:
            found_links = extract_links(html)
            if found_links:
                webopen(found_links[0]) # Open the first found link in a web browser.
            else:
                # Fallback: open Google search results page directly
                webopen(f"https://www.google.com/search?q={app}")

        return True # Indicate success.
    
# Function to close an application.
def CloseApp(app):
    try:
        # Do not use nearest-match when closing, and allow Chrome to be closed as well.
        close(app, match_closest=False, output=True, throw_error=True) # Attempt to close the app.
        return True # Indicate success.
    except:
        return False # Indicate failure.

# Function to execute system-level commands.
def System(command):

    # Nested function to mute the system volume.
    def mute():
        keyboard.press_and_release("volume mute") # Simulate the mute key press.

    # Nested function to unmute the system volume.
    def unmute():
        keyboard.press_and_release("volume mute") # Simulate the unmute key press.

    # Nested function to increase the system volume
    def volume_up():
        keyboard.press_and_release("volume up") # Simulate the volume up key press.

    # Nested function to decrease the system volume
    def volume_down():
        keyboard.press_and_release("volume down") # Simulate the volume down key press.

    # Execute the appropriate command.
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):

    funcs = [] # List to store asynchronous tasks.
    
    for command in commands:
        handled = False
        # Normalize the command to be more tolerant: lowercase and strip punctuation
        if command.lower().startswith("automation "):
            command = command[len("automation "):].strip()

        norm = re.sub(r"[^a-z0-9 ]+", "", command.lower())
        try:
            print(f"[Automation] Received command: '{command}' | norm='{norm}'")
        except Exception:
            pass

        # (Removed early URL-opening navigation handler per user request)

        # Early handling for 'open ...' to avoid being swallowed by screen-monitor block
        if norm.startswith("open "):
            # Ignore ambiguous/unsupported phrases
            if "open it" in norm or norm == "open file":
                handled = True
                continue
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
            funcs.append(fun)
            handled = True
            continue

        # If user asks to click on Home/History/Watch later but monitor is OFF, inform and skip (no URL open)
        if ("click on home" in norm or "click home" in norm
            or "click on history" in norm or "click history" in norm or "click on histry" in norm or "click histry" in norm
            or "click on watch later" in norm or "click watch later" in norm or "click on watchlater" in norm or "click watchlater" in norm):
            mon_state = get_screen_monitor()
            if not (mon_state and mon_state.running):
                await asyncio.to_thread(TextToSpeech, "Screen monitor is not running")
                handled = True
                continue

                # SCREEN MONITOR MODE HANDLING
        if "screen monitor on" in norm:
            start_screen_monitor()
            await asyncio.to_thread(TextToSpeech, "Screen monitor activated")
            handled = True
            continue

        # Turn OFF handling: tolerate 'off'/'of' variants and always disable debug + stop monitor
        if (
            "screen monitor off" in norm
            or "screen monitor of" in norm
            or "screen monitor testing off" in norm
            or "screen monitor testing of" in norm
            or "exit screen monitor" in norm
        ):
            mon = get_screen_monitor()
            if mon:
                try:
                    mon.set_debug(False)
                except Exception:
                    pass
            stop_screen_monitor()
            await asyncio.to_thread(TextToSpeech, "Screen monitor testing disabled and deactivated")
            handled = True
            continue

        # Support both 'debug on' and 'testing on'
        if "screen monitor debug on" in norm or "screen monitor testing on" in norm:
            mon = get_screen_monitor()
            if mon:
                mon.set_debug(True)
                await asyncio.to_thread(TextToSpeech, "Screen monitor testing enabled" if "testing on" in norm else "Screen monitor debug enabled")
            else:
                await asyncio.to_thread(TextToSpeech, "Screen monitor is not running")
            handled = True
            continue

        # Support both 'debug off' and 'testing off' (also tolerate 'of')
        if (
            "screen monitor debug off" in norm
            or "screen monitor testing off" in norm
            or "screen monitor debug of" in norm
            or "screen monitor testing of" in norm
        ):
            mon = get_screen_monitor()
            if mon:
                mon.set_debug(False)
                await asyncio.to_thread(TextToSpeech, "Screen monitor testing disabled" if "testing off" in norm else "Screen monitor debug disabled")
            else:
                await asyncio.to_thread(TextToSpeech, "Screen monitor is not running")
            handled = True
            continue

        monitor = get_screen_monitor()
        if monitor and monitor.running:
            # Utility to sanitize and find a title robustly
            def _find_title_box(raw_title: str):
                t = (raw_title or "").strip()
                t_trim = t.rstrip(" .!?\t\n")
                t_clean = re.sub(r"[^a-z0-9 ]+", " ", t_trim.lower()).strip()
                box = monitor.find_text(t) or monitor.find_text(t_trim) or monitor.find_text(t_clean)
                if not box and t_clean:
                    parts = t_clean.split()
                    short = " ".join(parts[:6]) if parts else t_clean
                    if short:
                        box = monitor.find_text(short)
                return box

            # 0) Cursor/Focus command to verify OCR coordinates interactively (replaces 'hover')
            if (
                norm.startswith("cursor title ") or
                norm.startswith("cursor ") or
                norm.startswith("focus title ") or
                norm.startswith("focus on ") or
                norm.startswith("pointer title ") or
                norm.startswith("point to ") or
                norm.startswith("show pointer ")
            ):
                try:
                    print("[Automation][Focus] Handler matched")
                except Exception:
                    pass
                lower_cmd = command.lower()
                # Accepted keys (ordered, first match wins)
                keys = [
                    "cursor title ",
                    "cursor ",
                    "focus title ",
                    "focus on ",
                    "pointer title ",
                    "point to ",
                    "show pointer ",
                ]
                title = ""
                for key in keys:
                    if lower_cmd.startswith(key):
                        try:
                            start = len(key)
                            title = command[start:].strip()
                        except Exception:
                            title = ""
                        break
                if not title:
                    title = extract_title_from_command(command) or ""

                if not title:
                    await asyncio.to_thread(TextToSpeech, "Please say the video title to hover")
                    handled = True
                    continue

                # Announce what we're focusing so user knows handler triggered
                await asyncio.to_thread(TextToSpeech, f"Focusing on: {title}")
                try:
                    print(f"[Automation][Focus] Title raw='{title}'")
                except Exception:
                    pass

                box = _find_title_box(title)
                if not box:
                    await asyncio.to_thread(TextToSpeech, "Cannot locate that video title to hover")
                    try:
                        print("[Automation][Focus] No OCR box found for title")
                    except Exception:
                        pass
                    handled = True
                    continue
                try:
                    pyautogui.moveTo(box['x'], box['y'])
                except Exception:
                    pass
                await asyncio.sleep(0.15)
                await asyncio.to_thread(TextToSpeech, f"Hovering at {box['x']}, {box['y']}")
                handled = True
                continue

            # Quick navigation commands on YouTube-like UIs (handle before fallback)
            if ("click on home" in norm or "click home" in norm):
                try:
                    print("[Automation][Nav] Click Home matched")
                except Exception:
                    pass
                # Try common variants and pick the leftmost occurrence (sidebar)
                candidates = [
                    "Home", "home", "HOME"
                ]
                best = None
                for txt in candidates:
                    itm = monitor.find_text(txt)
                    if itm:
                        if (best is None) or (itm['x'] < best['x']):
                            best = itm
                if best:
                    w, _ = pyautogui.size()
                    if best['x'] < int(0.4 * w):
                        monitor.click_at(best['x'], best['y'])
                    else:
                        await asyncio.to_thread(TextToSpeech, "Home not found")
                        handled = True
                        continue
                    await asyncio.to_thread(TextToSpeech, "Home")
                else:
                    await asyncio.to_thread(TextToSpeech, "Home not found")
                handled = True
                continue

            if ("click on history" in norm or "click history" in norm
                or "click on histry" in norm or "click histry" in norm):
                try:
                    print("[Automation][Nav] Click History matched")
                except Exception:
                    pass
                candidates = [
                    "History", "history", "Histry", "histry"
                ]
                best = None
                for txt in candidates:
                    itm = monitor.find_text(txt)
                    if itm:
                        if (best is None) or (itm['x'] < best['x']):
                            best = itm
                if best:
                    w, _ = pyautogui.size()
                    if best['x'] < int(0.4 * w):
                        monitor.click_at(best['x'], best['y'])
                    else:
                        await asyncio.to_thread(TextToSpeech, "History not found")
                        handled = True
                        continue
                    await asyncio.to_thread(TextToSpeech, "History opened")
                else:
                    await asyncio.to_thread(TextToSpeech, "History not found")
                handled = True
                continue

            if ("click on watch later" in norm or "click watch later" in norm
                or "click on watchlater" in norm or "click watchlater" in norm):
                try:
                    print("[Automation][Nav] Click Watch later matched")
                except Exception:
                    pass
                candidates = [
                    "Watch later", "Watch Later", "watch later", "watchlater", "WATCH LATER"
                ]
                best = None
                for txt in candidates:
                    itm = monitor.find_text(txt)
                    if itm:
                        if (best is None) or (itm['x'] < best['x']):
                            best = itm
                if best:
                    w, _ = pyautogui.size()
                    if best['x'] < int(0.4 * w):
                        monitor.click_at(best['x'], best['y'])
                    else:
                        await asyncio.to_thread(TextToSpeech, "Watch later not found")
                        handled = True
                        continue
                    await asyncio.to_thread(TextToSpeech, "Opening Watch later")
                else:
                    await asyncio.to_thread(TextToSpeech, "Watch later not found")
                handled = True
                continue

            # High-level action: Add to Watch later by video title (place BEFORE fallback)
            if norm.startswith("add to watch later "):
                try:
                    print("[Automation][WatchLater] Handler matched (pre-fallback)")
                except Exception:
                    pass
                lower_cmd = command.lower()
                key = "add to watch later "
                try:
                    start = lower_cmd.index(key) + len(key)
                    title = command[start:].strip()
                except ValueError:
                    title = extract_title_from_command(command) or ""

                if not title:
                    await asyncio.to_thread(TextToSpeech, "Please say the video title to add to Watch later")
                    handled = True
                    continue

                await asyncio.to_thread(TextToSpeech, f"Add to Watch later: {title}")
                try:
                    print(f"[Automation][WatchLater] Searching for title='{title}'")
                except Exception:
                    pass
                box = _find_title_box(title)
                if not box:
                    await asyncio.to_thread(TextToSpeech, "Cannot locate that video title")
                    handled = True
                    continue

                # Ensure browser window focus before interacting near the tile
                try:
                    w, h = pyautogui.size()
                    pyautogui.click(w//2, h//2)
                    await asyncio.sleep(0.15)
                except Exception:
                    pass

                # Hover slightly above title to reveal overlay/menu icons
                try:
                    pyautogui.moveTo(box['x'], max(0, box['y'] - 60))
                except Exception:
                    pass
                await asyncio.sleep(0.35)

                # Try overlay watch-later icon near this tile
                try:
                    print("[Automation][WatchLater] Trying overlay icon near title")
                except Exception:
                    pass
                wl_icon = None
                try:
                    wl_icon = monitor.match_template_near("watch_later_icon.png", box['x'], box['y'], search_radius=500, threshold=0.75)
                except Exception:
                    wl_icon = None
                if wl_icon:
                    monitor.click_at(wl_icon['x'], wl_icon['y'])
                    await asyncio.to_thread(TextToSpeech, "Added to Watch later")
                    handled = True
                    continue

                # Relative three-dot menu path
                try:
                    print("[Automation][WatchLater] Trying relative 3-dot menu near title")
                except Exception:
                    pass
                rel_clicked = False
                for dx in (200, 240, 280):
                    for dy in (-20, -10, 0):
                        tx, ty = box['x'] + dx, box['y'] + dy
                        try:
                            pyautogui.moveTo(tx, ty)
                            monitor.click_at(tx, ty)
                        except Exception:
                            continue
                        await asyncio.sleep(0.25)
                        # If Watch later is directly in this menu
                        item = monitor.find_text("watch later")
                        if item:
                            w, _ = pyautogui.size()
                            if abs(item['y'] - box['y']) < 300 and (box['x'] - 50) < item['x'] < int(0.9 * w):
                                monitor.click_at(item['x'], item['y'])
                                await asyncio.to_thread(TextToSpeech, "Added to Watch later")
                                rel_clicked = True
                                break
                        # Otherwise look for Save then Watch later
                        save = monitor.find_text("save") or monitor.find_text("save to")
                        if save:
                            monitor.click_at(save['x'], save['y'])
                            await asyncio.sleep(0.3)
                            wl = monitor.find_text("watch later")
                            if wl and abs(wl['y'] - box['y']) < 300 and wl['x'] > box['x'] - 50:
                                monitor.click_at(wl['x'], wl['y'])
                                await asyncio.to_thread(TextToSpeech, "Added to Watch later")
                                rel_clicked = True
                                break
                    if rel_clicked:
                        break
                if rel_clicked:
                    handled = True
                    continue

                # Template 3-dot near the tile, or fallback to open video page
                try:
                    print("[Automation][WatchLater] Trying template 3-dot icon near title")
                except Exception:
                    pass
                icon = monitor.match_template_near("three_dot_icon.png", box['x'], box['y'], search_radius=500, threshold=0.75)
                if icon:
                    monitor.click_at(icon['x'], icon['y'])
                else:
                    await asyncio.to_thread(TextToSpeech, "Menu not found, opening video page to save")
                    monitor.click_at(box['x'], box['y'])
                    await asyncio.sleep(1.8)
                    try:
                        w, h = pyautogui.size()
                        pyautogui.click(w//2, h//2)
                        await asyncio.sleep(0.2)
                        keyboard.press_and_release('k')
                    except Exception:
                        pass
                    await asyncio.sleep(0.5)
                    try:
                        print("[Automation][WatchLater] Pressing 's' to open Save dialog")
                        keyboard.press_and_release('s')
                        await asyncio.sleep(0.8)
                    except Exception:
                        pass
                    # Already handled by keyboard flow above; keep this block as no-op
                    save_btn = (
                        monitor.find_text("save") or
                        monitor.find_text("save to") or
                        monitor.find_text("save to playlist")
                    )
                    if save_btn:
                        pyautogui.moveTo(save_btn['x'], save_btn['y'])
                        monitor.click_at(save_btn['x'], save_btn['y'])
                        await asyncio.sleep(0.3)
                        wl = (
                            monitor.find_text("watch later") or
                            monitor.find_text("watchlater")
                        )
                        if wl:
                            if abs(wl['y'] - box['y']) < 400:
                                pyautogui.moveTo(wl['x'], wl['y'])
                                monitor.click_at(wl['x'], wl['y'])
                            else:
                                await asyncio.to_thread(TextToSpeech, "Watch later option not found")
                            await asyncio.to_thread(TextToSpeech, "Added to Watch later")
                        else:
                            await asyncio.to_thread(TextToSpeech, "Watch later option not found")
                        try:
                            keyboard.press_and_release('alt+left')
                        except Exception:
                            pass
                        await asyncio.sleep(0.8)
                        handled = True
                        continue

        # If we reached here and nothing handled this command, announce fallback and stop processing
        if not handled:
            mon_state = get_screen_monitor()
            if mon_state and mon_state.running:
                await asyncio.to_thread(TextToSpeech, "Screen-monitor: command not recognized")
            else:
                await asyncio.to_thread(TextToSpeech, "Command not recognized")
            continue

            # High-level actions on a video by title
            # 1) Add to Watch later
            if norm.startswith("add to watch later "):
                try:
                    print("[Automation][WatchLater] Handler matched")
                except Exception:
                    pass
                # Extract the raw title from the original command to preserve casing/punctuation
                lower_cmd = command.lower()
                key = "add to watch later "
                try:
                    start = lower_cmd.index(key) + len(key)
                    title = command[start:].strip()
                except ValueError:
                    title = extract_title_from_command(command) or ""

                if not title:
                    await asyncio.to_thread(TextToSpeech, "Please say the video title to add to Watch later")
                    handled = True
                    continue

                # Announce intent with title so user knows it's processing
                await asyncio.to_thread(TextToSpeech, f"Add to Watch later: {title}")
                try:
                    print(f"[Automation][WatchLater] Searching for title='{title}'")
                except Exception:
                    pass
                box = _find_title_box(title)
                if not box:
                    await asyncio.to_thread(TextToSpeech, "Cannot locate that video title")
                    try:
                        print("[Automation][WatchLater] No OCR box found for title")
                    except Exception:
                        pass
                    handled = True
                    continue

                # Hover over near the title to reveal overlay/menu icons (aim slightly above title -> thumbnail area)
                try:
                    pyautogui.moveTo(box['x'], max(0, box['y'] - 60))
                except Exception:
                    pass
                await asyncio.sleep(0.35)

                # Attempt fastest path: click overlay watch-later icon directly near this tile
                wl_icon = None
                try:
                    print("[Automation][WatchLater] Trying overlay icon near title")
                    wl_icon = monitor.match_template_near("watch_later_icon.png", box['x'], box['y'], search_radius=500, threshold=0.75)
                except Exception:
                    wl_icon = None
                if wl_icon:
                    monitor.click_at(wl_icon['x'], wl_icon['y'])
                    await asyncio.to_thread(TextToSpeech, "Added to Watch later")
                    handled = True
                    continue

                # (Corrupted duplicate 'relative 3-dot menu' block removed here; see the correct block above.)

            if ("click on watch later" in norm or "click watch later" in norm
                or "click on watchlater" in norm or "click watchlater" in norm):
                item = monitor.find_text("Watch later")
                if item:
                    monitor.click_at(item['x'], item['y'])
                    await asyncio.to_thread(TextToSpeech, "Opening Watch later")
                else:
                    await asyncio.to_thread(TextToSpeech, "Watch later not found")
                continue
            if any(k in norm for k in ["play", "watch", "open"]) and extract_title_from_command(command):
                title = extract_title_from_command(command)
                box = monitor.find_text(title)
                if box:
                    monitor.click_at(box['x'], box['y'])
                    await asyncio.to_thread(TextToSpeech, f"Playing {box['text']}")
                else:
                    await asyncio.to_thread(TextToSpeech, "Could not find that title on screen")
                continue

            if "open menu for" in norm or "menu for" in norm:
                title = extract_title_from_command(command)
                box = monitor.find_text(title)
                if not box:
                    await asyncio.to_thread(TextToSpeech, "Cannot locate the video title")
                    continue
                icon = monitor.match_template("three_dot_icon.png")
                if icon:
                    monitor.click_at(icon['x'], icon['y'])
                    await asyncio.to_thread(TextToSpeech, "Menu opened")
                else:
                    await asyncio.to_thread(TextToSpeech, "Menu icon not found")
                continue

            if "copy link" in norm:
                item = monitor.find_text("copy link")
                if item:
                    monitor.click_at(item['x'], item['y'])
                    await asyncio.to_thread(TextToSpeech, "Link copied to clipboard")
                else:
                    await asyncio.to_thread(TextToSpeech, "Copy link option not found")
                continue

            if "paste link" in norm:
                monitor.paste()
                await asyncio.to_thread(TextToSpeech, "Pasted link")
                continue

            await asyncio.to_thread(TextToSpeech, "Screen-monitor: command not recognized")
            continue

        # 'open' handled earlier to avoid interference with screen-monitor block

        elif command.startswith("general "): # Placeholder for general commands.
            pass

        elif command.startswith("realtime "): # Placeholder for real-time commands.
            pass

        elif command.startswith("close "): # Handle "close" commands.
            fun = asyncio. to_thread(CloseApp, command.removeprefix("close ")) # Schedule app closing
            funcs.append(fun)

        elif command.startswith("play " ): # Handle "play" commands.
            fun = asyncio.to_thread(PlayYouTube, command. removeprefix("play ")) # Schedule youtube playback
            funcs.append(fun)

        elif command.startswith("content "): # Handle "content" commands.
            fun = asyncio.to_thread(Content, command.removeprefix( "content "))
            funcs.append(fun)

        elif command.startswith("google search "): # Handle google search commands.
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "): # Handle youtube search commands.
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "): # Handle system commands
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"No Function Found. For {command}") # Print an error for unrecognized commands.

    results = await asyncio.gather(*funcs) # Execute all tasks concurrently.

    for result in results: # Process the results
        if isinstance(result, str):
            yield result
        else:
            yield result

# Asynchronous function to automate execution
async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands): # Translate and execute commands.
        pass

    return True

if __name__ == "__main__":
    asyncio.run(Automation(["open Instagram", "open Facebook"]))