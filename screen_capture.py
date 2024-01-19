import subprocess
import base64
import os
import requests
import io
from dotenv import load_dotenv
from pynput import keyboard
import tempfile
import threading
import itertools
import time
from rich.console import Console
from rich.status import Status

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def take_screenshot():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        tmp_filename = tmp_file.name

    # Take a screenshot and save it to the temporary file
    try:
        subprocess.run(["screencapture", "-i", tmp_filename])
    except Exception as e:
        print(f"Error occurred: {e}")
        exit(1)

    # Read the screenshot from the temporary file into a BytesIO object
    try:
        with open(tmp_filename, 'rb') as f:
            img_byte_arr = io.BytesIO(f.read())
        
        # Check if the BytesIO object is not empty
        if img_byte_arr.getbuffer().nbytes > 0:
            print("Screenshot captured and stored in bytes stream.")
            return img_byte_arr
        else:
            print("No data captured in the screenshot.")

    finally:
        # Clean up the temporary file
        os.remove(tmp_filename)


def encode_image_stream(image_stream: io.BytesIO, image_format: str = "PNG"):
    """Encodes an image stream to base64 and determines the correct MIME type."""
    mime_type = f"image/{image_format.lower()}"
    encoded_string = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f"data:{mime_type};base64,{encoded_string}"

def create_payload(image, prompt: str, model="gpt-4-vision-preview", max_tokens=1000, detail="high"):
    """Creates the payload for the API request."""
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        },
    ]

    base64_image = encode_image_stream(image)
    messages[0]["content"].append({
        "type": "image_url",
        "image_url": {
            "url": base64_image,
            "detail": detail,
        }
    })

    return {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens
    }

def query_openai(payload, console):
    """Sends a request to the OpenAI API and prints the response."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    with console.status("[bold green]Making API request...", spinner="dots"):
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return response.json()

class ShortcutListener:
    def __init__(self, hotkey, console):
        self.hotkey = hotkey
        self.current_keys = set()
        self.console = console

        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_activate(self):
        print("Keyboard shortcut activated!")
        image_stream = take_screenshot()
        payload = create_payload(image_stream, prompt="Solve the question in this image and output the answer with a short explanation.")
        
        

        response = query_openai(payload, self.console)

        self.console.print("[bold magenta]Response:[/bold magenta]")
        self.console.print(response["choices"][0]["message"]["content"])
        self.console.print("[bold magenta]Done![/bold magenta] Press ctrl+alt+s to make another request.")
        #print(image_stream)

    def for_canonical(self, f):
        return lambda k: f(l.canonical(k))

    def on_press(self, key):
        if key in self.hotkey:
            self.current_keys.add(key)
            if all(k in self.current_keys for k in self.hotkey):
                self.on_activate()

    def on_release(self, key):
        try:
            self.current_keys.remove(key)
        except KeyError:
            pass

if __name__ == "__main__":
    console = Console()
    console.print("[bold magenta]Hello! Press ctrl+alt+s to start...[/bold magenta]")
    hotkey = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('s')}
    sl = ShortcutListener(hotkey)

    #print(response["choices"][0]["message"]["content"])
