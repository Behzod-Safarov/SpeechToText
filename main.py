import speech_recognition as sr
import pvporcupine
from pvrecorder import PvRecorder
from playsound import playsound
import logging
from datetime import datetime
import time

# Set up logging
logging.basicConfig(
    filename="/var/log/speech_to_text.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Porcupine setup
ACCESS_KEY = "aqOlQV8dG4UhRr4hZdSvenx8GiRBj7bW7N6gXSBvAtD1dH"  # Your Picovoice AccessKey
HOTWORD_PATH = "/home/pi/SPEECHTOTEXT/hotword/hotword.ppn"  # Path to custom hotword file
SOUND_FILE = "/home/pi/SPEECHTOTEXT/sounds/sound.wav"  # Path to activation sound

# Initialize recognizer for speech-to-text
recognizer = sr.Recognizer()

def speech_to_text():
    # Initialize Porcupine with custom hotword
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[HOTWORD_PATH]
    )
    recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)  # -1 auto-selects default mic

    logging.info("Speech-to-Text service with hotword detection started.")
    print("Service started. Say your hotword to activate...")

    try:
        recorder.start()
        while True:
            # Listen for hotword
            pcm = recorder.read()
            result = porcupine.process(pcm)

            if result >= 0:  # Hotword detected
                logging.info("Hotword detected!")
                print("Hotword detected!")
                
                # Play activation sound
                playsound(SOUND_FILE)
                
                # Start speech-to-text
                with sr.Microphone() as source:
                    logging.info("Adjusting for ambient noise...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    logging.info("Listening for speech...")
                    print("Listening for your command...")

                    # Capture audio
                    audio = recognizer.listen(source, timeout=None)

                # Recognize speech
                try:
                    logging.info("Processing audio...")
                    text = recognizer.recognize_google(audio)
                    logging.info(f"Recognized: {text}")
                    print(f"You said: {text}")

                    # Save to file
                    with open("/home/pi/SPEECHTOTEXT/speech_output.txt", "a") as f:
                        f.write(f"{datetime.now()}: {text}\n")

                except sr.UnknownValueError:
                    logging.warning("Could not understand audio.")
                    print("Couldn’t understand what you said.")
                except sr.RequestError as e:
                    logging.error(f"Google Speech Recognition error: {e}")
                    print(f"Service error: {e}")

            time.sleep(0.01)  # Small delay to avoid high CPU usage

    except KeyboardInterrupt:
        logging.info("Service stopped by user.")
        print("Stopping service...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
    finally:
        recorder.stop()
        porcupine.delete()
        recorder.delete()

if __name__ == "__main__":
    speech_to_text()