import sys
from faster_whisper import WhisperModel

def transcribe_audio(file_path, output_txt):
    print(f"Loading Whisper model... (this may take a moment on the first run)")
    # 'base' or 'small' is fast and highly accurate for English. Use 'large-v3' for maximum accuracy.
    model = WhisperModel("base", device="cpu", compute_type="float32")

    print(f"Transcribing {file_path}...")
    segments, info = model.transcribe(file_path, beam_size=5)

    print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")

    with open(output_txt, "w", encoding="utf-8") as f:
        for segment in segments:
            timestamp = f"[{segment.start:.2f}s -> {segment.end:.2f}s]"
            line = f"{timestamp} {segment.text}\n"
            print(line, end="") # Print to terminal
            f.write(line)

    print(f"\nTranscription saved to {output_txt}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <path_to_mp3>")
        sys.exit(1)
    
    mp3_file = sys.argv[1]
    output_file = mp3_file.rsplit('.', 1)[0] + "_transcript.txt"
    transcribe_audio(mp3_file, output_file)
