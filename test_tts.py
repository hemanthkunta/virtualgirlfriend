import sys
import os

# Add virtualgirlfriend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.coqui_tts_engine import CoquiTTSEngine

try:
    print("Testing Coqui TTS...")
    engine = CoquiTTSEngine(reference_audio_path="custom_voice/reference_voice.wav")
    if engine.tts:
        print("Model loaded successfully!")
        path, duration = engine.synthesize("Hello there! I am working fine.")
        print(f"Success! Audio saved to: {path} (Duration: {duration}s)")
    else:
        print("Failed to initialize TTS.")
except Exception as e:
    import traceback
    traceback.print_exc()
