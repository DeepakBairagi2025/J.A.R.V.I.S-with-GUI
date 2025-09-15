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
import json
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

    # Merge with user-defined links from Data/WebLinks.json (non-breaking)
    try:
        data_dir = PROJECT_ROOT / "Data"
        data_dir.mkdir(parents=True, exist_ok=True)
        wl_path = data_dir / "WebLinks.json"
        user_links = []
        if wl_path.exists():
            try:
                with open(wl_path, 'r', encoding='utf-8') as f:
                    user_links = json.load(f) or []
                    if not isinstance(user_links, list):
                        user_links = []
            except Exception:
                user_links = []
        # If file missing or empty, seed from defaults (use simple names only)
        if not user_links:
            seed = []
            seen = set()
            for k, u in website_keywords.items():
                # avoid duplicating dot-variants and duplicates
                if '.' in k:
                    continue
                if k in seen:
                    continue
                seen.add(k)
                seed.append({'name': k, 'url': u})
            try:
                with open(wl_path, 'w', encoding='utf-8') as f:
                    json.dump(seed, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            user_links = seed
        # Merge user-defined names, overriding defaults if same key
        for item in user_links:
            try:
                name = str(item.get('name', '')).strip().lower()
                url  = str(item.get('url', '')).strip()
                if name and (url.startswith('http://') or url.startswith('https://')):
                    website_keywords[name] = url
            except Exception:
                continue
    except Exception:
        pass
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
            # If screen monitor is running, prefer clicking an on-screen title match (e.g., YouTube video)
            mon_try = get_screen_monitor()
            query = command.removeprefix("open ").strip()
            if mon_try and mon_try.running and query:
                # Build prioritized short variants to avoid matching huge OCR lines
                stop = {"the","a","an","to","and","or","of","on","for","with","your","my","in","at","by"}
                q_trim = query.rstrip(" .!?\t\n")
                q_clean = re.sub(r"[^a-z0-9 ]+", " ", q_trim.lower()).strip()
                tokens = [t for t in q_clean.split() if t and t not in stop]
                variants = []
                for n in (6,5,4,3):
                    if tokens:
                        v = " ".join(tokens[:n])
                        if v and v not in variants:
                            variants.append(v)
                # Also try original trim and clean at the end
                for v in (q_trim, q_clean):
                    if v and v not in variants:
                        variants.append(v)
                box = None
                used = ""
                # Get screen size for location heuristics
                try:
                    sw, sh = pyautogui.size()
                except Exception:
                    sw, sh = (1920, 1080)
                for v in variants:
                    candidate = mon_try.find_text(v)
                    if not candidate:
                        continue
                    cx, cy = candidate.get('x'), candidate.get('y')
                    # Heuristics: avoid top nav (y<120), avoid extreme edges (x<100 or x>sw-120)
                    if cy is not None and cx is not None and cy >= 120 and 100 <= cx <= max(100, sw-120):
                        box = candidate
                        used = v
                        break
                if box:
                    try:
                        print(f"[Automation][Open] Clicking on-screen match for '{used}' (from '{query}') at ({box['x']},{box['y']})")
                    except Exception:
                        pass
                    mon_try.click_at(box['x'], box['y'])
                    handled = True
                    continue
            # Otherwise, fallback to original OpenApp behavior
            if "open it" in norm or norm == "open file":
                handled = True
                continue
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
            handled = True
            continue

        # Screen monitor toggles
        if "screen monitor on" in norm:
            start_screen_monitor()
            await asyncio.to_thread(TextToSpeech, "Screen monitor activated")
            handled = True
            continue

        if (
            "screen monitor off" in norm or
            "screen monitor of" in norm or
            "screen monitor testing off" in norm or
            "screen monitor testing of" in norm or
            "exit screen monitor" in norm
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

        if "screen monitor debug on" in norm or "screen monitor testing on" in norm:
            mon = get_screen_monitor()
            if mon:
                mon.set_debug(True)
                await asyncio.to_thread(TextToSpeech, "Screen monitor testing enabled" if "testing on" in norm else "Screen monitor debug enabled")
            else:
                await asyncio.to_thread(TextToSpeech, "Screen monitor is not running")
            handled = True
            continue

        if (
            "screen monitor debug off" in norm or
            "screen monitor testing off" in norm or
            "screen monitor debug of" in norm or
            "screen monitor testing of" in norm
        ):
            mon = get_screen_monitor()
            if mon:
                mon.set_debug(False)
                await asyncio.to_thread(TextToSpeech, "Screen monitor testing disabled" if "testing off" in norm else "Screen monitor debug disabled")
            else:
                await asyncio.to_thread(TextToSpeech, "Screen monitor is not running")
            handled = True
            continue

        # On-screen actions (monitor must be running)
        monitor = get_screen_monitor()
        if monitor and monitor.running:

            def _find_title_box(raw_title: str):
                t = (raw_title or "").strip()
                t_trim = t.rstrip(" .!?\t\n")
                t_clean = re.sub(r"[^a-z0-9 ]+", " ", t_trim.lower()).strip()
                stop = {"the","a","an","to","and","or","of","on","for","with","your","my","in","at","by"}
                tokens = [tok for tok in (t_clean.split() if t_clean else []) if tok and tok not in stop]
                variants: list[str] = []
                # Prefer short, distinctive heads first
                for n in (6,5,4,3):
                    if tokens:
                        v = " ".join(tokens[:n])
                        if v and v not in variants:
                            variants.append(v)
                # Then try original raw/trim/clean
                for v in (t, t_trim, t_clean):
                    if v and v not in variants:
                        variants.append(v)
                box = None
                # Get screen size for location heuristics
                try:
                    sw, sh = pyautogui.size()
                except Exception:
                    sw, sh = (1920, 1080)
                for v in variants:
                    candidate = monitor.find_text(v)
                    if not candidate:
                        continue
                    cx, cy = candidate.get('x'), candidate.get('y')
                    # Heuristics: ignore header/top chrome area and extreme edges
                    if cy is not None and cx is not None and cy >= 120 and 100 <= cx <= max(100, sw-120):
                        box = candidate
                        break
                return box

            # Focus/Pointer handler to visually verify OCR match
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
                    await asyncio.to_thread(TextToSpeech, "Please say the title to focus")
                    handled = True
                    continue
                await asyncio.to_thread(TextToSpeech, f"Focusing on: {title}")
                box = _find_title_box(title)
                if not box:
                    await asyncio.to_thread(TextToSpeech, "Cannot locate that title to focus")
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

            # Quick navigation: Home (left sidebar)
            if ("click on home" in norm or "click home" in norm or "click on homes" in norm or "click homes" in norm):
                try:
                    print("[Automation][Nav] Click Home matched")
                except Exception:
                    pass
                candidates = ["Home", "home", "HOME"]
                best = None
                for txt in candidates:
                    itm = monitor.find_text(txt)
                    if itm:
                        if (best is None) or (itm['x'] < best['x']):
                            best = itm
                if best:
                    try:
                        sw, _ = pyautogui.size()
                    except Exception:
                        sw = 1920
                    if best['x'] < int(0.4 * sw):
                        monitor.click_at(best['x'], best['y'])
                        await asyncio.to_thread(TextToSpeech, "Home")
                    else:
                        await asyncio.to_thread(TextToSpeech, "Home not found")
                else:
                    await asyncio.to_thread(TextToSpeech, "Home not found")
                handled = True
                continue

            # Quick navigation: History (left sidebar)
            if ("click on history" in norm or "click history" in norm or "click on histry" in norm or "click histry" in norm):
                try:
                    print("[Automation][Nav] Click History matched")
                except Exception:
                    pass
                candidates = ["History", "history", "Histry", "histry"]
                best = None
                for txt in candidates:
                    itm = monitor.find_text(txt)
                    if itm:
                        if (best is None) or (itm['x'] < best['x']):
                            best = itm
                if best:
                    try:
                        sw, _ = pyautogui.size()
                    except Exception:
                        sw = 1920
                    if best['x'] < int(0.4 * sw):
                        monitor.click_at(best['x'], best['y'])
                        await asyncio.to_thread(TextToSpeech, "History opened")
                    else:
                        await asyncio.to_thread(TextToSpeech, "History not found")
                else:
                    await asyncio.to_thread(TextToSpeech, "History not found")
                handled = True
                continue

            # Quick navigation: Watch later (left sidebar)
            if ("click on watch later" in norm or "click watch later" in norm or "click on watchlater" in norm or "click watchlater" in norm):
                try:
                    print("[Automation][Nav] Click Watch later matched")
                except Exception:
                    pass
                candidates = ["Watch later", "Watch Later", "watch later", "watchlater", "WATCH LATER"]
                best = None
                for txt in candidates:
                    itm = monitor.find_text(txt)
                    if itm:
                        if (best is None) or (itm['x'] < best['x']):
                            best = itm
                if best:
                    try:
                        sw, _ = pyautogui.size()
                    except Exception:
                        sw = 1920
                    if best['x'] < int(0.4 * sw):
                        monitor.click_at(best['x'], best['y'])
                        await asyncio.to_thread(TextToSpeech, "Opening Watch later")
                    else:
                        await asyncio.to_thread(TextToSpeech, "Watch later not found")
                else:
                    await asyncio.to_thread(TextToSpeech, "Watch later not found")
                handled = True
                continue

            # add to watch later <title> (open video -> Save -> Watch later)
            if norm.startswith("add to watch later "):
                try:
                    print("[Automation][WatchLater] Handler matched")
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

                try:
                    w, h = pyautogui.size()
                    pyautogui.click(w//2, h//2)
                    await asyncio.sleep(0.15)
                except Exception:
                    pass
                monitor.click_at(box['x'], box['y'])
                await asyncio.sleep(1.8)

                save_btn = None
                for _ in range(12):
                    save_btn = (
                        monitor.find_text("Save") or
                        monitor.find_text("save") or
                        monitor.find_text("SAVE")
                    )
                    if save_btn:
                        break
                    await asyncio.sleep(0.5)

                if not save_btn:
                    share = monitor.find_text("Share") or monitor.find_text("share")
                    if share:
                        for dx in [200, 240, 280, 320]:
                            for dy in [0, -15, 15]:
                                tx, ty = share['x'] + dx, share['y'] + dy
                                try:
                                    pyautogui.moveTo(tx, ty)
                                    monitor.click_at(tx, ty)
                                except Exception:
                                    continue
                                await asyncio.sleep(0.7)
                                save_btn = monitor.find_text("Save") or monitor.find_text("save")
                                if save_btn:
                                    break
                            if save_btn:
                                break
                    if not save_btn:
                        download = monitor.find_text("Download") or monitor.find_text("download")
                        if download:
                            for dx in [140, 180, 220, 260]:
                                for dy in [0, -15, 15]:
                                    tx, ty = download['x'] + dx, download['y'] + dy
                                    try:
                                        pyautogui.moveTo(tx, ty)
                                        monitor.click_at(tx, ty)
                                    except Exception:
                                        continue
                                    await asyncio.sleep(0.7)
                                    save_btn = monitor.find_text("Save") or monitor.find_text("save")
                                    if save_btn:
                                        break
                                if save_btn:
                                    break

                if save_btn:
                    try:
                        pyautogui.moveTo(save_btn['x'], save_btn['y'])
                        monitor.click_at(save_btn['x'], save_btn['y'])
                    except Exception:
                        pass
                    await asyncio.sleep(0.7)
                    wl = None
                    for _ in range(14):
                        wl = (
                            monitor.find_text("Watch later") or
                            monitor.find_text("watch later") or
                            monitor.find_text("WATCH LATER")
                        )
                        if wl:
                            break
                        await asyncio.sleep(0.35)
                    if wl:
                        pyautogui.moveTo(wl['x'], wl['y'])
                        monitor.click_at(wl['x'], wl['y'])
                        await asyncio.sleep(0.3)
                        await asyncio.to_thread(TextToSpeech, "Added to Watch later")
                    else:
                        await asyncio.to_thread(TextToSpeech, "Watch later option not found")
                else:
                    await asyncio.to_thread(TextToSpeech, "Save button not visible yet")

                try:
                    keyboard.press_and_release('escape')
                    await asyncio.sleep(0.2)
                except Exception:
                    pass
                try:
                    keyboard.press_and_release('alt+left')
                except Exception:
                    pass
                await asyncio.sleep(0.8)
                handled = True
                continue

        if not handled:
            mon_state = get_screen_monitor()
            if mon_state and mon_state.running:
                await asyncio.to_thread(TextToSpeech, "Screen-monitor: command not recognized")
            else:
                await asyncio.to_thread(TextToSpeech, "Command not recognized")
            continue

        # Bottom routing
        if command.startswith("general "):
            pass
        if command.startswith("realtime "):
            pass
        if command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        if command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYouTube, command.removeprefix("play ")))
        if command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))
        if command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))
        if command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))
        if command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))
        else:
            print(f"No Function Found. For {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result
async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands): # Translate and execute commands.
        pass

    return True

if __name__ == "__main__":
    asyncio.run(Automation(["open Instagram", "open Facebook"]))