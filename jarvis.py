import datetime
import webbrowser
import requests
import os
import subprocess

import pyttsx3
import speech_recognition as sr
from decouple import config


# ====== CONFIG / ENV ======
USER = config("USER", default="sir")
BOTNAME = config("BOTNAME", default="Jarvis")


# ====== TTS: NEW SPEAK FUNCTION (RE-INIT EACH CALL) ======
def speak(text: str) -> None:
    """Convert text to speech and also print it on console."""
    print(f"{BOTNAME}: {text}")

    engine = pyttsx3.init("sapi5")     # fresh engine each time (fixes 'only first time speaks' issues on Windows)
    engine.setProperty("rate", 170)    # Speed of speech
    engine.setProperty("volume", 1.0)  # Volume (0.0 to 1.0)

    voices = engine.getProperty("voices")
    # Try to find Microsoft Hazel (UK) first – more Jarvis-like [web:170]
    selected_voice = None
    for v in voices:
        name = v.name.lower()
        if "hazel" in name or "desktop - english (united kingdom)" in name:
            selected_voice = v
            break

    # If Hazel not found, fall back to first available voice
    if selected_voice is None and voices:
        selected_voice = voices[0]

    if selected_voice is not None:
        engine.setProperty("voice", selected_voice.id)

    engine.say(text)
    engine.runAndWait()
    engine.stop()


# ====== LISTEN / STT ======
def listen() -> str:
    """Listen from microphone and return recognized text (lowercased)."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        # timeout + phrase_time_limit so it does not hang forever
        audio = recognizer.listen(source,)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-in")
        print(f"{USER}: {query}")
        return query.lower()
    except Exception as e:
        print("ERROR IN RECOGNITION:", e)
        speak("Could not understand. Say that again...")
        return ""


# ====== CORE FEATURES ======
def greet_user() -> None:
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak(f"Good morning,{USER}.")
    elif 12 <= hour < 18:
        speak(f"Good afternoon,{USER}.")
    else:
        speak(f"Good evening,{USER}.")
    speak(f"I am {BOTNAME}. How can I help you?")


def get_time() -> None:
    now = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"The time is {now}")

def open_whatsapp_app():
    # Try WhatsApp protocol
    subprocess.Popen(["cmd", "/C", "start whatsapp://"], shell=True)

def open_spotify_app():
    spotify_path = r"C:/Users/borad/OneDrive/Desktop/Spotify.lnk"
    os.startfile(spotify_path)


def open_website(url: str, name: str) -> None:
    webbrowser.open(url)
    speak(f"Opening {name}")


def search_wikipedia(topic: str) -> None:
    if not topic.strip():
        speak("Please say the topic to search on Wikipedia.")
        return

    speak(f"Searching Wikipedia for {topic}")
    try:
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "titles": topic,
            },
            timeout=5,
        )
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        if not pages:
            speak("Sorry, I could not find information on that topic.")
            return

        page = next(iter(pages.values()))
        extract = page.get("extract", "")
        if not extract:
            speak("Sorry, there is no readable summary for that topic.")
            return

        summary = ". ".join(extract.split(". ")[:2])
        speak("According to Wikipedia")
        speak(summary)
    except Exception:
        speak("Sorry, there was a problem while searching Wikipedia.")


def handle_query(query: str) -> bool:
    """
    Process a single user query.
    Return False if user wants to exit, True otherwise.
    """
    print("HANDLE_QUERY GOT:", repr(query))  # debug
    if not query:
        return True

    if "wikipedia" in query:
        topic = query.replace("wikipedia", "").strip()
        search_wikipedia(topic)

    elif "open youtube" in query:
        open_website("https://www.youtube.com", "YouTube")

    elif "open google" in query:
        open_website("https://www.google.com", "Google")

    elif "open github" in query:
        open_website("https://github.com", "GitHub")

    elif "time" in query:
        get_time()

    elif "who are you" in query or "what is your name" in query:
        speak(f"My name is {BOTNAME}, your Python assistant.")

    elif "who am i" in query:
        speak(f"You are {USER}, of course.")

    elif "exit" in query or "quit" in query or "stop" in query:
        speak("Goodbye sir")
        return False

    else:
        speak("Sorry, I did not understand that command.")

    return True


# ====== MAIN LOOP ======
def main() -> None:
    speak("Initializing system.")
    greet_user()

    while True:
        print("BEFORE LISTEN")       # debug
        query = listen()
        print("AFTER LISTEN:", query)
        if not handle_query(query):
            break


if __name__ == "__main__":
    main()
