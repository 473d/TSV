

import cv2
import numpy as np
import speech_recognition as sr
from googletrans import Translator
import threading
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# Initialize the speech recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Define the source and target languages
source_lang = 'en'  # English
target_lang = 'tr'  # Arabic

# Initialize the video capture object
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

# Variables to store the recognized and translated text
recognized_text = ""
translated_text = ""

def recognize_and_translate():
    global recognized_text, translated_text
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            recognized_text = recognizer.recognize_google(audio, language=source_lang)
            print(f"Recognized Speech: {recognized_text}")
            translated_text = translator.translate(recognized_text, src=source_lang, dest=target_lang).text
            print(f"Translated Text: {translated_text}")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

# Start the speech recognition and translation in a separate thread
def start_recognition_thread():
    recognition_thread = threading.Thread(target=recognize_and_translate)
    recognition_thread.daemon = True
    recognition_thread.start()

# Call the recognition function initially
start_recognition_thread()

# Load a TTF font for Unicode support
font_path = "arial.ttf"  # Path to a TTF font file that supports Arabic
font = ImageFont.truetype(font_path, 32)

def draw_text(img, text, position, font, color=(0, 0, 255)):
    """Draw text on an image using PIL and convert back to OpenCV format."""
    reshaped_text = arabic_reshaper.reshape(text)  # Reshape Arabic text
    bidi_text = get_display(reshaped_text)  # Ensure proper right-to-left display
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    draw.text(position, bidi_text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        # Only recognize and translate every 60 frames to reduce load
        frame_count += 1
        if frame_count % 60 == 0:
            start_recognition_thread()

        # Overlay the text on the video frame
        frame = draw_text(frame, recognized_text, (10, 50), font)
        frame = draw_text(frame, translated_text, (10, 100), font)

        # Display the resulting frame
        cv2.imshow('frame', frame)

        # Write the frame to the output video
        out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything when done
cap.release()
out.release()
cv2.destroyAllWindows()
