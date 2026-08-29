from faster_whisper import WhisperModel

# Load the model once (small = fast, good enough for a hackathon demo)
model = WhisperModel("small", device="cpu", compute_type="int8")

def transcribe_audio(audio_path):
    segments, info = model.transcribe(audio_path)
    full_text = " ".join(segment.text.strip() for segment in segments)

    return {
        "transcript": full_text.strip()
    }

# Quick test — only runs when you run this file directly
if __name__ == "__main__":
    result = transcribe_audio("ml/speech/Tester.m4a")  # change to match your actual filename
    print(result)