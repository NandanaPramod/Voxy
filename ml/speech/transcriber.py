from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")

def transcribe_audio(audio_path):
    segments, info = model.transcribe(audio_path, language="en")
    full_text = " ".join(segment.text.strip() for segment in segments)

    return {
        "transcript": full_text.strip()
    }

if __name__ == "__main__":
    result = transcribe_audio("ml/speech/Tester.m4a")
    print(result)