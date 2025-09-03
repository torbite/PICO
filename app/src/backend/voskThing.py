import pico_main
import sounddevice as sd
import queue
import vosk
import json

# Load the Vosk model (folder)
model = vosk.Model("../../voskModels/English")
recognizer = vosk.KaldiRecognizer(model, 16000)

# Queue for audio chunks
q = queue.Queue()

# Audio callback
def callback(indata, frames, time, status):
    if status:
        print("Audio Status:", status)
    q.put(bytes(indata))

# Start stream and recognition loop
WaitingForPicoResponse = False
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("🎤 Listening... Press Ctrl+C to stop.")
    
    
    while True:
        if WaitingForPicoResponse:
            continue

        data = q.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            print(text)
            print(text != '' and '<' not in text and '>' not in text)
            if text != '' and '<' not in text and '>' not in text:
                # a = input()
                # if a == '':
                #     continue
                print("📝 You said:", text)
                WaitingForPicoResponse = True
                try:
                    
                    for resp in pico_main.getPicoResponse(text):
                        if resp and resp != "error":
                            print("PICO:", resp, flush=True)
                finally:
                    WaitingForPicoResponse = False
        else:
            partial = json.loads(recognizer.PartialResult())
            print("... ", partial.get("partial", ""), end='\r')