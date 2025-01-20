import openai
import speech_recognition as sr
import pyttsx3
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# Initialize text-to-speech engine
engine = pyttsx3.init()
def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()

# Listen for user input
def listen():
    """Captures audio input and converts it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source)
            user_input = recognizer.recognize_google(audio)
            print(f"You said: {user_input}")
            return user_input
        except sr.UnknownValueError:
            return "I didn't catch that. Could you repeat?"
        except sr.RequestError:
            return "Speech recognition service is unavailable."

# Reminder storage
reminders = []

def add_reminder(reminder_text, reminder_time):
    """Adds a reminder to the reminders list."""
    reminders.append((reminder_text, reminder_time))
    speak(f"Reminder set for {reminder_time}.")
    print(f"Reminder added: '{reminder_text}' at {reminder_time}")
    update_output(f"Reminder added: '{reminder_text}' at {reminder_time}")

def check_reminders():
    """Continuously checks for due reminders."""
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for reminder in reminders:
            if reminder[1] == now:
                speak(f"Reminder alert: {reminder[0]}")
                print(f"Reminder alert: {reminder[0]}")
                update_output(f"Reminder alert: {reminder[0]}")
                reminders.remove(reminder)
        time.sleep(30)  # Check every 30 seconds

def parse_reminder(user_input):
    """Parses the user's input for reminders."""
    try:
        # Example input: "Remind me to call John at 5:30 PM"
        if "remind me to" in user_input.lower() and "at" in user_input.lower():
            parts = user_input.lower().split("at")
            reminder_text = parts[0].replace("remind me to", "").strip()
            reminder_time = parts[1].strip()
            
            # Convert to 24-hour time format
            reminder_time = datetime.strptime(reminder_time, "%I:%M %p").strftime("%H:%M")
            
            # Append today's date
            reminder_datetime = f"{datetime.now().strftime('%Y-%m-%d')} {reminder_time}"
            
            add_reminder(reminder_text, reminder_datetime)
        else:
            speak("I didn't understand the reminder format. Please say it like 'Remind me to call John at 5:30 PM.'")
            update_output("I didn't understand the reminder format.")
    except Exception as e:
        speak("Something went wrong while setting the reminder. Please try again.")
        update_output(f"Error: {e}")

# OpenAI API integration
def chat_with_openai(prompt):
    """Communicates with OpenAI's API for chatbot responses."""
    try:
        openai.api_key = ""  # Add your OpenAI API key here
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response['choices'][0]['message']['content']
        return reply
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "I'm having trouble connecting to OpenAI right now."

# GUI Output Window
def update_output(text):
    """Updates the output window with new text."""
    output_text.insert(tk.END, text + "\n")
    output_text.see(tk.END)

# Main program
if __name__ == "__main__":
    # Create a GUI window
    root = tk.Tk()
    root.title("TARS Output")
    
    # Create a ScrolledText widget
    output_text = ScrolledText(root, wrap=tk.WORD, width=80, height=20)
    output_text.pack(padx=10, pady=10)
    
    # Start the reminder checker in a separate thread
    threading.Thread(target=check_reminders, daemon=True).start()

    speak("Hello, I am TARS. You can ask me to set reminders or have a conversation. Say 'exit' to quit.")
    update_output("TARS is ready. Listening...")

    while True:
        user_input = listen()

        if "exit" in user_input.lower():
            speak("Goodbye! Shutting down TARS.")
            update_output("Goodbye! Shutting down TARS.")
            break

        if "remind me" in user_input.lower():
            parse_reminder(user_input)
        else:
            response = chat_with_openai(user_input)
            speak(response)
            update_output(f"TARS: {response}")

    root.mainloop()
