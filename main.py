import streamlit as st
import requests
import json
from gtts import gTTS
import time
import speech_recognition as sr
import re  # Import regex for text splitting

# Replace with your valid Gemini API Key
GEMINI_API_KEY = "AIzaSyDgFbt8YURcFF3KFf6DR1PBr6D784YmWMs"


def speak_text(text):
    """Ensure full speech output by processing in paragraph chunks."""
    try:
        # Split text into paragraph chunks (every 2-3 sentences)
        paragraphs = re.split(r'(\.|\?|!)(\s+)', text)  # Keep punctuation
        full_chunks = []

        # Merge sentence parts into full chunks
        chunk = ""
        for part in paragraphs:
            chunk += part
            if len(chunk) > 3000:  # Adjust chunk size dynamically
                full_chunks.append(chunk.strip())
                chunk = ""

        if chunk:
            full_chunks.append(chunk.strip())

        # Speak each chunk fully before moving on
        for chunk in full_chunks:
            engine.say(chunk)
            engine.runAndWait()  # Ensure speech completes before moving on
            time.sleep(0.7)  # Add a small delay to prevent cutoffs

    except Exception as e:
        st.error(f"Error in text-to-speech: {e}")

def get_medical_response(user_input):
    """Query the Gemini API and return the AI-generated response."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"I have these symptoms: {user_input}. What could be the cause and treatment?"}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()

        if "candidates" in response_json and len(response_json["candidates"]) > 0:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "⚠ No valid response received."
    except requests.exceptions.RequestException as e:
        return f"🚨 API Request Error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected Error: {str(e)}"

def recognize_speech():
    """Capture audio from the microphone and convert it to text using SpeechRecognition."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Please speak your symptoms.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.success(f"✅ Recognized: {text}")
            return text
        except sr.UnknownValueError:
            st.error("⚠ Sorry, I could not understand the audio. Please try again.")
            return ""
        except sr.RequestError:
            st.error("⚠ Could not request results. Please check your internet connection.")
            return ""

def main():
    st.set_page_config(page_title="Medical Assistant Chatbot", page_icon="🩺")
    st.title("🩺 Medical Assistant Chatbot")

    st.write("💡 *Enter your symptoms or use voice input to receive possible causes and treatments.*")

    # Welcome message (spoken only once)
    if "welcome_spoken" not in st.session_state:
        welcome_message = "Hello! I am your medical assistant. You can enter your symptoms or speak them out. How can I help you today?"
        speak_text(welcome_message)
        st.session_state.welcome_spoken = True

    # Text input field with stored voice-to-text data
    user_input = st.text_area("🔍 Enter your symptoms:", st.session_state.get("user_input", ""))

    if st.button("💬 Get Diagnosis"):
        if not user_input.strip():
            st.error("🚨 Please enter or speak your symptoms before submitting.")
        else:
            with st.spinner("🔄 Processing your request..."):
                response = get_medical_response(user_input)
            st.success("✅ *Response from the Medical Assistant:*")
            st.write(response)

            # Speak the response fully (Even for 1500+ words)
            speak_text(response)

if __name__ == "__main__":
    main()
