import os
from typing import Tuple, Dict
import json
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import sys
import shutil

load_dotenv()

class TextToSpeechEngine:
    """Convert text to speech with sweet female voice"""
    
    def __init__(self, provider: str = "pyttsx3", voice_id: str = None):
        """
        Initialize TTS engine
        
        """
        self.provider = provider
        self.voice_id = voice_id or "default_sweet_female"
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'audio_output')
        self.reference_audio_path = os.path.join(os.path.dirname(__file__), '..', 'custom_voice', 'reference_voice.wav')
        os.makedirs(self.output_dir, exist_ok=True)
        
        if provider == "pyttsx3":
            self.init_pyttsx3()
        elif provider == "elevenlabs":
            self.init_elevenlabs()
        elif provider == "coqui":
            self.init_coqui()
    
    def init_pyttsx3(self):
        """Initialize pyttsx3 for local text-to-speech"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()

            # Set female voice if available
            try:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if 'female' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            except Exception:
                pass

            # Set voice parameters for sweet voice
            try:
                self.engine.setProperty('rate', 150)  # Speed
                self.engine.setProperty('volume', 0.9)  # Volume
            except Exception:
                pass

        except Exception as e:
            # Graceful fallback when pyttsx3 or its native dependencies are missing
            print(f"Warning: pyttsx3 unavailable: {e}")
            self.engine = None
    
    def init_elevenlabs(self):
        """Initialize Elevenlabs API for premium voice"""
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.elevenlabs_api_key:
            print("Warning: ELEVENLABS_API_KEY not set. Falling back to pyttsx3")
            self.provider = "pyttsx3"
            self.init_pyttsx3()
            
    def init_coqui(self):
        """Initialize Coqui XTTS for local voice cloning"""
        try:
            from src.coqui_tts_engine import CoquiTTSEngine
            self.coqui_engine = CoquiTTSEngine(self.reference_audio_path)
        except Exception as e:
            print(f"Failed to initialize Coqui TTS: {e}")
            self.provider = "pyttsx3"
            self.init_pyttsx3()
    
    def text_to_speech_pyttsx3(self, text: str, output_file: str) -> Tuple[str, float]:
        """
        Convert text to speech using pyttsx3 (local)
        
        Returns:
            Tuple of (output_file_path, duration_in_seconds)
        """
        output_path = os.path.join(self.output_dir, output_file)

        # If pyttsx3 engine is available, use it
        if getattr(self, 'engine', None):
            try:
                self.engine.save_to_file(text, output_path)
                self.engine.runAndWait()
            except Exception as e:
                print(f"pyttsx3 save error, will try macOS 'say' or silent fallback: {e}")
                self.engine = None

        # If engine is not available, try macOS `say`
        if not getattr(self, 'engine', None):
            if sys.platform == 'darwin' and shutil.which('say'):
                # Use say to create AIFF, then convert to WAV via ffmpeg if available
                aiff_path = output_path + '.aiff'
                try:
                    subprocess.run(['say', text, '-o', aiff_path], check=True)
                    if shutil.which('ffmpeg'):
                        subprocess.run(['ffmpeg', '-y', '-i', aiff_path, output_path], check=True)
                        try:
                            os.remove(aiff_path)
                        except Exception:
                            pass
                    else:
                        # If ffmpeg not available, return the AIFF file path
                        output_path = aiff_path
                except Exception as e:
                    print(f"macOS say error: {e}")
                    # Fall through to silent fallback

        # If still no audio produced, write a short silent WAV as fallback
        if not os.path.exists(output_path):
            try:
                self._write_silent_wav(output_path, text)
            except Exception as e:
                raise Exception(f"Failed to synthesize audio: {e}")

        # Estimate duration (rough approximation)
        word_count = len(text.split())
        estimated_duration = (word_count / 2.5) + 0.5  # +0.5 for silence

        return output_path, estimated_duration

    def _write_silent_wav(self, path: str, text: str, sr: int = 22050):
        """Create a silent WAV file approximately matching speech length"""
        try:
            import soundfile as sf
            import numpy as np

            word_count = len(text.split())
            duration = max(0.8, (word_count / 2.5) + 0.5)
            samples = int(duration * sr)
            data = np.zeros((samples, ), dtype='int16')
            # Write as 16-bit PCM
            sf.write(path, data, sr, subtype='PCM_16')
        except Exception:
            # Last-resort binary write of minimal WAV header + silence using wave
            import wave
            import struct
            duration = 1.0
            sr = 22050
            nframes = int(duration * sr)
            with wave.open(path, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                silence = struct.pack('<h', 0) * nframes
                wf.writeframes(silence)
    
    def text_to_speech_elevenlabs(self, text: str, output_file: str) -> Tuple[str, float]:
        """
        Convert text to speech using Elevenlabs API (premium quality)
        
        Best voices for virtual girlfriend:
        - bella (young, friendly, sweet)
        - alice (warm, caring)
        - nova (energetic, playful)
        """
        import requests
        
        output_path = os.path.join(self.output_dir, output_file)
        
        # Voice mapping
        voice_mapping = {
            'bella': '4AZE7E7u9WwHVzVSVxFq',
            'alice': 'Xb7hH8MSUJpSbvAppyhc',
            'nova': '79a125e8-cd45-4c13-8a67-188112f4dd22',
            'default_sweet_female': '4AZE7E7u9WwHVzVSVxFq'  # Bella
        }
        
        voice_id = voice_mapping.get(self.voice_id, voice_mapping['default_sweet_female'])
        
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                # Get actual duration from audio file
                import soundfile as sf
                data, samplerate = sf.read(output_path)
                duration = len(data) / samplerate
                
                return output_path, duration
            else:
                raise Exception(f"Elevenlabs API error: {response.status_code}")
        
        except Exception as e:
            print(f"Elevenlabs error, falling back to pyttsx3: {e}")
            return self.text_to_speech_pyttsx3(text, output_file)
    
    def synthesize(self, text: str, output_file: str = None) -> Tuple[str, float]:
        """
        Main synthesis function
        
        Returns:
            Tuple of (output_file_path, duration_in_seconds)
        """
        if output_file is None:
            # Generate unique filename
            import uuid
            output_file = f"speech_{uuid.uuid4().hex[:8]}.wav"
        
        if self.provider == "pyttsx3":
            return self.text_to_speech_pyttsx3(text, output_file)
        elif self.provider == "elevenlabs":
            return self.text_to_speech_elevenlabs(text, output_file)
        elif self.provider == "coqui":
            if hasattr(self, 'coqui_engine') and self.coqui_engine.tts:
                return self.coqui_engine.synthesize(text, output_file)
            else:
                return self.text_to_speech_pyttsx3(text, output_file)
        else:
            raise ValueError(f"Unknown TTS provider: {self.provider}")
    
    def get_audio_duration(self, audio_file_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            import soundfile as sf
            data, samplerate = sf.read(audio_file_path)
            return len(data) / samplerate
        except:
            import librosa
            y, sr = librosa.load(audio_file_path)
            return len(y) / sr


class AudioProcessor:
    """Process user audio input - recording and speech-to-text"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.audio_dir = os.path.join(os.path.dirname(__file__), '..', 'audio_input')
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def record_audio(self, duration: int = 10, device: int = None) -> str:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            device: Audio device ID (None = default)
            
        Returns:
            Path to recorded audio file
        """
        try:
            import sounddevice as sd
            import soundfile as sf
            
            print(f"Recording for {duration} seconds... Speak now!")
            
            # Record audio
            audio_data = sd.rec(int(duration * self.sample_rate), 
                               samplerate=self.sample_rate, 
                               channels=1, 
                               device=device)
            sd.wait()
            
            # Save to file
            import uuid
            output_file = os.path.join(self.audio_dir, f"user_audio_{uuid.uuid4().hex[:8]}.wav")
            sf.write(output_file, audio_data, self.sample_rate)
            
            print(f"Recording saved to {output_file}")
            return output_file
        
        except Exception as e:
            raise Exception(f"Error recording audio: {e}")
    
    def speech_to_text_whisper(self, audio_file: str) -> str:
        """
        Convert speech to text using OpenAI Whisper
        """
        try:
            import whisper
            
            # Load Whisper model (download on first use)
            print("Loading Whisper model...")
            model = whisper.load_model("base")  # 'tiny', 'base', 'small', 'medium', 'large'
            
            # Transcribe
            print("Transcribing audio...")
            result = model.transcribe(audio_file)
            
            text = result['text'].strip()
            confidence = result.get('segments', [{}])[0].get('confidence', 0) if result.get('segments') else 0
            
            print(f"Transcription: {text} (confidence: {confidence})")
            return text
        
        except Exception as e:
            raise Exception(f"Whisper transcription error: {e}")
    
    def get_list_audio_devices(self):
        """List available audio input devices"""
        try:
            import sounddevice as sd
            print("Available audio devices:")
            print(sd.query_devices())
        except:
            print("sounddevice not installed")


# Configuration presets for different TTS providers
TTS_CONFIGS = {
    'pyttsx3_local': {
        'provider': 'pyttsx3',
        'voice_id': 'default_sweet_female',
        'cost': 0,
        'quality': 'good',
        'requires_api_key': False,
        'latency': 'low'
    },
    'elevenlabs_bella': {
        'provider': 'elevenlabs',
        'voice_id': 'bella',
        'cost': 'paid',
        'quality': 'excellent',
        'requires_api_key': True,
        'latency': 'medium',
        'description': 'Young, friendly, perfect for girlfriend AI'
    },
    'elevenlabs_alice': {
        'provider': 'elevenlabs',
        'voice_id': 'alice',
        'cost': 'paid',
        'quality': 'excellent',
        'requires_api_key': True,
        'latency': 'medium',
        'description': 'Warm, caring voice'
    },
    'coqui_custom': {
        'provider': 'coqui',
        'voice_id': 'custom_hyderabadi',
        'cost': 'free',
        'quality': 'excellent',
        'requires_api_key': False,
        'latency': 'medium',
        'description': 'Local custom voice model'
    }
}

def get_recommended_tts_config() -> Dict:
    """Get recommended TTS configuration for virtual girlfriend"""
    # Start with local, upgrade to Elevenlabs if API key available
    reference_audio = os.path.join(os.path.dirname(__file__), '..', 'custom_voice', 'reference_voice.wav')
    if os.path.exists(reference_audio):
         return TTS_CONFIGS['coqui_custom']
    elif os.getenv('ELEVENLABS_API_KEY'):
        return TTS_CONFIGS['elevenlabs_bella']
    else:
        return TTS_CONFIGS['pyttsx3_local']
