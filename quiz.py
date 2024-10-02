import os
import time
import base64
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from notif import notify

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')

if not API_KEY:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")

TEXT_PROMPT = "Please give the correct answer to the question. You should just provide the answer. No justification required. This is important."


class Watcher:
    DIRECTORY_TO_WATCH = "/Users/hamza/Desktop/screenshots"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def try_open_file(file_path, attempts=5, delay=1):
        """Attempt to open a file multiple times with a delay."""
        for attempt in range(attempts):
            try:
                with open(file_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
            except FileNotFoundError:
                print(f"Attempt {attempt + 1}: File not found, retrying...")
                time.sleep(delay)
        print("Failed to open file after multiple attempts.")
        return None

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == "created":
            # Check if the new file is a picture.
            # get file name and extension
            # file_name, file_extension = os.path.splitext(event.src_path)
            # print(file_name, file_extension)
            if event.src_path.lower().endswith(
                (".png", ".jpg", ".jpeg", ".gif", ".bmp")
            ):
                # notify("New Picture", f"{event.src_path} has been added.")
                print(f"{event.src_path} has been added.")
                file_path = event.src_path
                # print(file_path)
                split_path = file_path.split("/")
                # print(split_path[-1])
                if split_path[-1].startswith("."):
                    split_path[-1] = split_path[-1][1:]
                    # print(split_path[-1])
                    file_path = "/".join(split_path)
                else:
                    return
                # print(file_path)
                # Encode the picture in base64
                # with open(file_path, "rb") as image_file:
                #     base64_image = base64.b64encode(image_file.read()).decode("utf-8")

                base64_image = Handler.try_open_file(file_path)
                if not base64_image:
                    return

                # Prepare the payload for the OpenAI API
                # data = {
                #     "prompt": {
                #         "image": base64_image,
                #         "text": "Answer the question shown in this picture.",
                #     },
                #     "temperature": 0.5,
                #     "max_tokens": 100,
                #     "model": "gpt-4",
                # }
                headers = {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                }
                # Send the request to OpenAI API
                payload = {
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": TEXT_PROMPT,
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    "max_tokens": 300,
                }

                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                # print(response.json())
                notify(
                    "Message",
                    response.json()["choices"][0]["message"]["content"],
                )


if __name__ == "__main__":
    # ask user for course and other details
    course = input("Enter the course name: ")
    print(f"Course: {course}")
    # append course to the prompt
    TEXT_PROMPT += f" The course is {course}."
    # ask for additional prompts if needed
    additional_prompts = input(
        "Do you want to add additional prompts? If yes, enter them. If no, press enter: "
    )
    print(f"Additional Prompts: {additional_prompts}")
    # append additional prompts to the prompt
    TEXT_PROMPT += f" {additional_prompts}"
    w = Watcher()
    w.run()
