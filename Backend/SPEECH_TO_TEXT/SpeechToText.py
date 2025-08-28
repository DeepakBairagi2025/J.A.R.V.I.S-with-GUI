from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
from pathlib import Path

# Load environment variables from the .env file.
# Resolve project root (two levels up from this file)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
env_vars = dotenv_values(str(PROJECT_ROOT / ".env"))

# Get the input language setting from the environment variables.
InputLanguage = env_vars.get("InputLanguage")

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code with the input language from the environment variables.
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the modified HTML code to a file at project Data directory.
data_dir = PROJECT_ROOT / "Data"
data_dir.mkdir(parents=True, exist_ok=True)
voice_file = data_dir / "Voice.html"
with open(voice_file, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Set current_dir to project root to keep original path formatting below.
current_dir = str(PROJECT_ROOT)
# Generate the file path for the HTML file.
Link = f"{current_dir}/Data/Voice.html"

# Set Chrome options for the webDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
# Reduce Chrome noise and disable push/notifications to avoid GCM-related errors
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-background-networking")
chrome_options.add_argument("--disable-features=Translate,PrivacySandboxAdsAPIs,InterestFeedContent,MediaRouter,OptimizationHints")
chrome_options.add_argument("--log-level=3")  # Errors only
chrome_options.add_argument("--disable-logging")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files.
TempDirPath = rf"{current_dir}/Frontend/Files"
os.makedirs(TempDirPath, exist_ok=True)

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]

    #Check if the query is a question and add a question mark if necessary
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question
        if query_words[-1][-1] not in ['.', '?', '!']:
            new_query = new_query + "."
        else:
            # If it already ends with punctuation, keep it as-is (don't duplicate)
            if query_words[-1][-1] != '.':
                new_query = new_query[:-1] + "."
            # else leave as is
    
    return new_query.capitalize()

# Function to translate text into english usig the mtranslate library.
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Function to perform speech recognition using the webDriver
def SpeechRecognition():
    # Open the HTML file in the browser.
    driver.get("file:///" + Link)
    # Start speech recognition by clicking the start button.
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            # Get the recognized text from the HTML output element.
            Text = driver.find_element(by=By.ID, value="output").text
            if Text:
                # Stop recognition by clicking the stop button.
                driver.find_element(by=By.ID, value="end").click()

                # If the input language is English, return the modified query.
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    # If the input language is not English, translate the text and return it.
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
                
        except Exception as e:
            pass

# Main execution block.
if __name__ == "__main__":
    while True:
        # Continously perform speech recognition and print the recognized text.
        Text = SpeechRecognition()
        print(Text)


""" from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
# Get the input language setting from the environment variables.
InputLanguage = env_vars.get("InputLanguage")

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code with the input language from the environment variables.
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the modified HTML code to a file.
with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)

# Get the current working directory.
current_dir = os.getcwd()
# Generate the file path for the HTML file.
Link = f"{current_dir}/Data/Voice.html"

# Set Chrome options for the webDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files.
TempDirPath = rf"{current_dir}/Frontend/Files"

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]

    #Check if the query is a question and add a question mark if necessary
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question
        if query_words[-1][-1] not in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

# Function to translate text into english usig the mtranslate library.
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Function to perform speech recognition using the webDriver
def SpeechRecognition():
    # Open the HTML file in the browser.
    driver.get("file:///" + Link)
    # Start speech recognition by clicking the start button.
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            # Get the recognized text from the HTML output element.
            Text = driver.find_element(by=By.ID, value="output").text
            if Text:
                # Stop recognition by clicking the stop button.
                driver.find_element(by=By.ID, value="end").click()

                # If the input language is English, return the modified query.
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    # If the input language is not English, translate the text and return it.
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
                
        except Exception as e:
            pass

# Main execution block.
if __name__ == "__main__":
    while True:
        # Continously perform speech recognition and print the recognized text.
        Text = SpeechRecognition()
        print(Text)
            pass

# Main execution block.
if __name__ == "__main__":
    while True:
        # Continously perform speech recognition and print the recognized text.
        Text = SpeechRecognition()
        print(Text) """