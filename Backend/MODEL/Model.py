from http.client import responses

import cohere # Import the Cohere library for AI services.
from pyexpat.errors import messages
from rich import print # Import the Rich library to enhance terminal outputs.
from dotenv import dotenv_values # Import dotenv to load environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve API key.
CohereAPIKey = env_vars.get("CohereAPIKey")

# Create a Cohere client using the provided API key.
co = cohere.Client(api_key=CohereAPIKey)

# Define a list of recognized function keywords for task categorization.
# Include canonical automation commands so they pass the initial filter.
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search ", "reminder", "automation",
    # Automation canonical intents
    "add to watch later ",
    "copy link for ",
    "copy link ",
    # Cursor/focus pointer intents
    "focus on ",
    "focus title ",
    "cursor title ",
    "cursor ",
    "pointer title ",
    "point to ",
    "show pointer ",
]

# Initialize an empty list to store user messages.
messages = []

# Define the preamble that guides the AI model on how to categorize queries.
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
-> Respond with 'automation (command)' for any command that interacts with a user interface on the screen, such as 'add to watch later', 'copy link', 'focus on', 'click button', etc. For example: 'automation add to watch later my favorite video', 'automation copy link for the current video', 'automation focus on the search bar'.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# Define a chat history with predefined user-chatbot interactions for context.
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome and firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance."},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."},
    {"role": "User", "message": "add to watch later the new spiderman trailer"},
    {"role": "Chatbot", "message": "automation add to watch later the new spiderman trailer"},
    {"role": "User", "message": "focus on the search bar"},
    {"role": "Chatbot", "message": "automation focus on the search bar"},
    {"role": "User", "message": "copy the link for this video"},
    {"role": "Chatbot", "message": "automation copy link for this video"},
]

# Define the main function for decision making on queries.
def FirstLayerDMM(prompt: str = "test"):
    # Add the user's query to the messages list.
    messages.append({"role": "user", "content": f"{prompt}"})

    # Create a streaming chat session with the Cohere model.
    stream = co.chat_stream(
        model='command-r-plus', # Specify the Cohere model to use.
        message=prompt, # Pass the user's query.
        temperature=0.7, # Set the creativity level
        chat_history=ChatHistory, # Provide the predefined chat history for context.
        prompt_truncation='OFF', # Ensure the prompt is no truncated.
        connectors=[], # No additional connectors are used.
        preamble=preamble # Pass the detailed instruction preamble.
    )

    # Initialize an empty string to store the generate response.
    response = ""

    # Iterate over events in the stream and capture text generation events.
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text # Append generated text to the response.

    # Remove newline characters and split responses into individual tasks.
    response = response.replace("\n", "")
    response = response.split(",")

    # Strip leading and trailing whitespaces from each task.
    response = [i.strip() for i in response]

    # Strong intent override based on the raw prompt to avoid misclassification
    low_prompt = (prompt or "").lower().strip()
    def tail_after(prefix: str) -> str:
        return prompt[len(prefix):].strip()
    if low_prompt.startswith("focus on "):
        response = [f"focus on {tail_after('focus on ')}"]
    elif low_prompt.startswith("focus title "):
        response = [f"focus title {tail_after('focus title ')}"]
    elif low_prompt.startswith("cursor title "):
        response = [f"cursor title {tail_after('cursor title ')}"]
    elif low_prompt.startswith("cursor "):
        response = [f"cursor {tail_after('cursor ')}"]
    elif low_prompt.startswith("point to "):
        response = [f"point to {tail_after('point to ')}"]
    elif low_prompt.startswith("show pointer "):
        response = [f"show pointer {tail_after('show pointer ')}"]
    elif low_prompt.startswith("add to watch later "):
        response = [f"add to watch later {tail_after('add to watch later ')}"]
    elif low_prompt.startswith("copy link for "):
        response = [f"copy link for {tail_after('copy link for ')}"]
    elif low_prompt.startswith("copy link "):
        response = [f"copy link for {tail_after('copy link ')}"]
    elif low_prompt.startswith("open "):
        response = [f"open {tail_after('open ')}"]

    # Initialize an empty list to filter valid tasks.
    temp = []

    # Filter the tasks based on recognized function keywords.
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task) # Add valid tasks to the filtered list.

    # Update the responsed with the filtered list of tasks.
    response = temp

    # Lightweight normalization: strip misclassification prefixes for key automation commands
    canonical_starts = (
        "add to watch later ",
        "copy link for ",
        "copy link ",
        "focus on ",
        "focus title ",
        "cursor title ",
        "cursor ",
        "pointer title ",
        "point to ",
        "show pointer ",
        "open ",
        "automation ",
    )
    def strip_prefix(task: str) -> str:
        low = task.lower()
        prefixes = (
            "general ",
            "youtube search ",
            "google search ",
            "realtime ",
            "content ",
        )
        for p in prefixes:
            if low.startswith(p):
                tail = task[len(p):].strip()
                low_tail = tail.lower()
                # If tail already begins with a canonical command, keep it
                if low_tail.startswith(canonical_starts):
                    return tail
                # If tail begins with 'automation ', keep it to allow downstream handling
                if low_tail.startswith("automation "):
                    return tail
        return task

    response = [strip_prefix(t) for t in response]
    try:
        print(f"[DMM] Final tasks: {response}")
    except Exception:
        pass

    # De-duplicate conflicting commands: prefer high-level actions over 'open' for the same title
    try:
        action_titles = []
        for t in response:
            lowt = t.lower()
            if lowt.startswith("add to watch later "):
                action_titles.append(t[len("add to watch later "):].strip().lower())
            elif lowt.startswith("copy link for "):
                action_titles.append(t[len("copy link for "):].strip().lower())

        def same_title(a: str, b: str) -> bool:
            # Simple containment match both ways to be forgiving
            a, b = a.lower().strip(), b.lower().strip()
            return (a in b) or (b in a)

        filtered = []
        for t in response:
            lowt = t.lower()
            if lowt.startswith("open "):
                tail = t[len("open "):].strip().lower()
                if any(same_title(tail, at) for at in action_titles):
                    # Skip opening when a higher-level action on the same title is present
                    continue
            filtered.append(t)
        response = filtered
    except Exception:
        # In case of any unexpected parsing issue, keep the original response
        pass

    # If '(query)' is in the response, recursively call the function for further clarification.
    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse # Return the clarified response.
    else:
        return response # Return the filtered response.

# Entry point for the script.
if __name__ == "__main__":
    # Continously prompt the user for input and process it.
    while True:
        print(FirstLayerDMM(input(">>>"))) # Print the categorized response.