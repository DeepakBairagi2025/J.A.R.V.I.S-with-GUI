import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep
import logging

# Function to open and displav imaqes based on a given prompt
def open_images(prompt):
    folder_path = DATA_DIR # Folder where the images are stored
    prompt = prompt.replace(" ", "_") # Replace spaces in prompt with underscores

    # Generate the filenames for the images
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1) # Pause for 1 second before showing the next image

        except IOError:
            print(f"Unable to open {image_path}" ) 

# API detailes for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
# Resolve project root .env no matter where this script is run from
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ENV_PATH = os.path.join(BASE_DIR, '.env')
headers = {"Authorization": f"Bearer {get_key(ENV_PATH, 'HuggingFaceAPIKey')}"}
TRIGGER_FILE = os.path.join(BASE_DIR, r"Frontend", r"Files", r"ImageGeneration.data")
DATA_DIR = os.path.join(BASE_DIR, r"Data")
os.makedirs(DATA_DIR, exist_ok=True)

# Ensure trigger file exists and is initialized so script can start before user writes to it
try:
    if not os.path.exists(TRIGGER_FILE) or os.path.getsize(TRIGGER_FILE) == 0:
        with open(TRIGGER_FILE, "w") as _f:
            _f.write("False, False")
except Exception as _e:
    logging.warning(f"Could not initialize trigger file: {_e}")

# Async function to send a query to the Hugging Face API
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    if getattr(response, 'status_code', 200) != 200:
        try:
            preview = response.text[:400]
        except Exception:
            preview = str(response)
        print(f"HF API error: {response.status_code} | {preview}")
    return response.content

# Async Function to generate images based on the given prompt
async def generate_images(prompt: str):
    tasks = []

    # Create 4 images generation tasks
    for _ in range(4):
        payload = { 
            "inputs": f"{prompt}, quality=4K, sharpness-maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)

    # Save the generated images to file
    for i, image_bytes in enumerate(image_bytes_list):
        with open(os.path.join(DATA_DIR, f"{prompt.replace(' ','_')}{i+1}.jpg"), "wb") as f:
            f.write(image_bytes)

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt)) # Run the async image generation
    open_images(prompt) # Open the generated images

# Main loop to monitor for image generation requests
while True:

    try:
        # Read the status indicates an image generation requeset
        with open(TRIGGER_FILE, "r") as f:
            Data: str = f.read()
        
        Prompt, Status = [s.strip() for s in Data.split(",", 1)]

        # If the status indicates an image generation requests
        if Status == "True":
            print("Generating Images ...")
            ImageStatus = GenerateImages(prompt=Prompt)

            # Reset the status in the file after generating images
            with open(TRIGGER_FILE, "w") as f:
                f.write("False, False")
                break # Exit the loop after processing the request

        else:
            sleep(1) # Wait for 1 second before checking again

    except Exception as e:
        logging.error(f"Loop error: {e}")