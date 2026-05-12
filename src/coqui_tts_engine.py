import os
import torch
from typing import Tuple

class CoquiTTSEngine:
    """Local, high-quality Voice Cloning using Coqui XTTSv2"""
    
    def __init__(self, reference_audio_path: str = None):
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'audio_output')
        os.makedirs(self.output_dir, exist_ok=True)
        self.reference_audio_path = reference_audio_path
        
        print("Loading Coqui XTTSv2 Model... (This might take a while on first run)")
        try:
            from TTS.api import TTS
            import torch
            
            # Fix PyTorch 2.6 UnpicklingError permanently by allowing weights_only=False
            _original_load = torch.load
            def _patched_load(*args, **kwargs):
                kwargs['weights_only'] = False
                return _original_load(*args, **kwargs)
            torch.load = _patched_load
            
            # Get device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if torch.backends.mps.is_available():
                device = "mps"
            
            # Init TTS
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            self.language = "en" # XTTS supports en, fr, de, es, it, pt, pl, tr, ru, nl, cs, ar, zh, hu, ko, ja, hi
            self.device = device
            print(f"XTTSv2 loaded successfully on {device}!")
        except Exception as e:
            print(f"Error initializing TTS: {e}")
            import traceback
            traceback.print_exc()
            self.tts = None
            
    def synthesize(self, text: str, output_file: str = None) -> Tuple[str, float]:
        if not self.tts:
            raise Exception("Coqui TTS is not installed or loaded.")
            
        if not self.reference_audio_path or not os.path.exists(self.reference_audio_path):
            raise FileNotFoundError("Reference audio not found. Please provide a path to a .wav file with the desired voice.")
            
        if output_file is None:
            import uuid
            output_file = f"speech_{uuid.uuid4().hex[:8]}.wav"
            
        output_path = os.path.join(self.output_dir, output_file)
        
        print(f"Generating speech with custom voice...")
        
        # We can use "hi" (Hindi) or "en" (English) depending on the slang
        # If the input is English text with Hyderabadi slang words, "en" or "hi" might work
        
        self.tts.tts_to_file(
            text=text,
            speaker_wav=self.reference_audio_path,
            language=self.language,
            file_path=output_path
        )
        
        # Get duration
        import soundfile as sf
        data, samplerate = sf.read(output_path)
        duration = len(data) / samplerate
        
        return output_path, duration
