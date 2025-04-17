import speech_recognition as sr
from pydub import AudioSegment
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64
import io

def transcribe_audio(audio_data):
       """
       Transcribe base64-encoded WebM audio to text using Google Speech Recognition.
       Returns the transcribed text or None if it fails.
       """
       try:
           audio_bytes = base64.b64decode(audio_data, validate=True)
           webm_audio = io.BytesIO(audio_bytes)
           try:
               audio = AudioSegment.from_file(webm_audio, format="webm")
           except Exception as e:
               print(f"Failed to process WebM audio: {e}")
               return None
           wav_io = io.BytesIO()
           audio.export(wav_io, format="wav")
           wav_io.seek(0)
           recognizer = sr.Recognizer()
           with sr.AudioFile(wav_io) as source:
               audio_data = recognizer.record(source)
               for attempt in range(3):  # Retry up to 3 times
                   try:
                       text = recognizer.recognize_google(audio_data)
                       return text
                   except sr.RequestError as e:
                       print(f"Retry {attempt + 1}/3: Google API request failed: {e}")
                       if attempt == 2:
                           return None
                   except sr.UnknownValueError:
                       print("Google could not understand audio")
                       return None
       except base64.binascii.Error as e:
           print(f"Invalid base64 audio data: {e}")
           return None
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
           for attempt in range(3):
               try:
                   tts = gTTS(text=text, lang=language, slow=False)
                   mp3_io = io.BytesIO()
                   tts.write_to_fp(mp3_io)
                   mp3_io.seek(0)
                   audio_bytes = mp3_io.read()
                   if len(audio_bytes) == 0:
                       print("Empty TTS audio generated")
                       return None
                   base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
                   return base64_audio
               except Exception as e:
                   print(f"Retry {attempt + 1}/3: TTS error: {e}")
                   if attempt == 2:
                       return None
       except Exception as e:
           print(f"TTS error: {e}")
           return None