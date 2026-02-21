import speech_recognition as sr
import pyttsx3
import tkinter as tk
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import numpy as np
import os
import threading
import time

# ---------------- ABUSE WORD LIST ----------------
abuse_words = [

    # Hindi / Hinglish (common insults)
    "pagal",
    "bewakoof",
    "gadha",
    "ullu",
    "nalayak",
    "kamina",
    "harami",
    "bakwas",
    "faltu",
    "chutiya",      # commonly used insult
    "kutte",
    "kutta",
    "saala",
    "saali",
    "idiot",
    "stupid",
    "fool",
    "loser",
    "mental",

    # Street slang (mild–moderate)
    "nonsense",
    "bakchod",
    "bakchodi",
    "faltugiri",
    "ghatiya",
    "cheap",

    # Regional (commonly understood across India)
    "ullu ka pattha",
    "gadha insaan",
    "pagal aadmi",
    "bewakoof insaan"
]


abuse_count = 0
listening = False

engine = pyttsx3.init()
recognizer = sr.Recognizer()

# ---------------- FUNCTIONS ----------------
def count_abuse_words(text, abuse_list):
    count = 0
    for word in abuse_list:
        count += text.count(word)
    return count

def red_alert(count):
    alert = tk.Toplevel()
    alert.title("ABUSE ALERT")
    alert.geometry("300x200")
    alert.configure(bg="red")

    label = tk.Label(
        alert,
        text=f"Abusive Word Detected\nTotal Count: {count}",
        fg="white",
        bg="red",
        font=("Arial", 16, "bold")
    )
    label.pack(expand=True)

    alert.after(2000, alert.destroy)

def record_audio(duration=4, fs=16000):
    print("Recording...")
    recording = sd.rec(
        int(duration * fs),
        samplerate=fs,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    # Convert float32 → int16 (VERY IMPORTANT)
    audio_int16 = np.int16(recording / np.max(np.abs(recording)) * 32767)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav.write(temp_file.name, fs, audio_int16)
    return temp_file.name

def listen_loop():
    global abuse_count, listening

    while listening:
        audio_file = record_audio()

        try:
            with sr.AudioFile(audio_file) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.record(source)


            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)
            text = text.lower().replace("-", " ").strip()


            found = count_abuse_words(text, abuse_words)

            if found > 0:
                abuse_count += found
                engine.say("Warning. Abusive language detected")
                engine.runAndWait()
                red_alert(abuse_count)
                count_label.config(text=f"Abuse Count: {abuse_count}")
            else:
                print("No abuse detected")

        except:
            print("Voice not clear")

        os.remove(audio_file)
        time.sleep(0.5)

def start_listening():
    global listening
    if not listening:
        listening = True
        status_label.config(text="Status: Listening", fg="green")
        threading.Thread(target=listen_loop, daemon=True).start()

def stop_listening():
    global listening
    listening = False
    status_label.config(text="Status: Stopped", fg="red")

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Abuse Word Detection System")
root.geometry("420x350")

title = tk.Label(
    root,
    text="Abuse Word Detection",
    font=("Arial", 18, "bold")
)
title.pack(pady=10)

status_label = tk.Label(
    root,
    text="Status: Stopped",
    font=("Arial", 12),
    fg="red"
)
status_label.pack(pady=5)

count_label = tk.Label(
    root,
    text="Abuse Count: 0",
    font=("Arial", 14, "bold")
)
count_label.pack(pady=10)

start_btn = tk.Button(
    root,
    text="START",
    font=("Arial", 14),
    bg="green",
    fg="white",
    width=12,
    command=start_listening
)
start_btn.pack(pady=10)

stop_btn = tk.Button(
    root,
    text="STOP",
    font=("Arial", 14),
    bg="red",
    fg="white",
    width=12,
    command=stop_listening
)
stop_btn.pack(pady=5)

root.mainloop()

