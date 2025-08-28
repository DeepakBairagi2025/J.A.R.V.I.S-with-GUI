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
    }
    for kw, url in website_keywords.items():
        if kw in app_key:
            webopen(url)
            return True
    
    try:
        appopen(app, match_closest=True, output=True, throw_error=True) # Attempt to open the application.
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

    if "chrome" in app:
        pass # Skip if the app is Chrome
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True) # Attempt to close the app.
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

        if command.startswith("open "): # Handle "open" commands.

            if "open it" in command: # Ignore "open it" command
                pass
            
            if "open file" == command: # Ignore "open file" commands.
                pass

            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

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