import speech_recognition as sr
from pydub import AudioSegment
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64
import io
import os

def transcribe_audio(audio_data):
    """
    Transcribe base64-encoded WebM audio to text using Google Speech Recognition.
    Returns the transcribed text or None if it fails.
    """
    try:
        audio_bytes = base64.b64decode(audio_data)
        webm_audio = io.BytesIO(audio_bytes)
        audio = AudioSegment.from_file(webm_audio, format="webm")
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

def translate_text(text, target_language):
    """
    Translate text to the target language using Google Translate.
    Returns the translated text or None if it fails.
    """
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def text_to_speech(text, language):
    """
    Convert text to audio using gTTS and return as base64-encoded MP3.
    Returns base64 string or None if it fails.
    """
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        mp3_io = io.BytesIO()
        tts.write_to_fp(mp3_io)
        mp3_io.seek(0)
        audio_bytes = mp3_io.read()
        base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        return base64_audio
    except Exception as e:
        print(f"TTS error: {e}")
        return None
