import socket
import wave
import datetime
import speech_recognition as sr
from googletrans import Translator

HOST = '0.0.0.0'
PORT = 5000

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = f"record_{timestamp}.wav"

CHANNELS = 1
SAMPLE_WIDTH = 2
SAMPLE_RATE = 16000

print("🎙 Menunggu koneksi ESP32...")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

conn, addr = server.accept()
print(f"✅ Terhubung dari {addr}")

frames = bytearray()

try:
    while True:
        data = conn.recv(512)
        if not data:
            break
        frames.extend(data)
except KeyboardInterrupt:
    pass
finally:
    conn.close()
    server.close()

# Simpan file audio
with wave.open(OUTPUT_FILE, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(SAMPLE_WIDTH)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(frames)

print(f"✅ Audio tersimpan sebagai {OUTPUT_FILE}")

# ============= SPEECH TO TEXT =============
print("🧠 Mengubah suara bahasa Inggris menjadi teks...")
recognizer = sr.Recognizer()

with sr.AudioFile(OUTPUT_FILE) as source:
    audio = recognizer.record(source)

try:
    # Speech-to-text dari bahasa Inggris 🇬🇧
    text_en = recognizer.recognize_google(audio, language="en-US")
    print("📄 Hasil transkripsi (English):")
    print(text_en)

    # Translasi ke Bahasa Indonesia 🇮🇩
    translator = Translator()
    translated = translator.translate(text_en, src='en', dest='id').text

    print("\n🇮🇩 Hasil terjemahan:")
    print(translated)

    # Simpan dua versi (EN & ID)
    with open(f"{OUTPUT_FILE.replace('.wav', '_translated.txt')}", "w", encoding="utf-8") as f:
        f.write("=== English ===\n")
        f.write(text_en + "\n\n")
        f.write("=== Indonesian ===\n")
        f.write(translated)

    print("💾 File teks disimpan!")

except sr.UnknownValueError:
    print("⚠️ Suara tidak terdeteksi atau tidak bisa dikenali.")
except sr.RequestError as e:
    print(f"❌ Error koneksi ke Google Speech API: {e}")
except Exception as e:
    print(f"⚠️ Error lain: {e}")
