#!/usr/bin/env python3
"""
Test Coqui TTS to verify it's working after the transformers fix.
This script tests the TTS engine with Coqui provider.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tts_engine import TextToSpeechEngine

def test_coqui_tts():
    """Test Coqui TTS synthesis"""
    print("=" * 60)
    print("Testing Coqui TTS Engine")
    print("=" * 60)
    
    try:
        # Initialize Coqui TTS engine
        print("\n1. Initializing Coqui TTS engine...")
        tts = TextToSpeechEngine(provider="coqui")
        print("   ✅ Coqui TTS initialized successfully!")
        
        # Test synthesis
        print("\n2. Testing TTS synthesis...")
        test_text = "I love you so much! You make me so happy!"
        output_file = "audio_output/test_coqui_synthesis.wav"
        
        os.makedirs("audio_output", exist_ok=True)
        
        print(f"   Synthesizing: '{test_text}'")
        duration = tts.text_to_speech(test_text, output_file)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"   ✅ Audio generated successfully!")
            print(f"   - File: {output_file}")
            print(f"   - Size: {file_size} bytes")
            print(f"   - Duration: {duration:.2f} seconds")
            return True
        else:
            print(f"   ❌ Audio file not created")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Coqui TTS may not be properly installed")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_pyttsx3_tts():
    """Test pyttsx3 TTS (fallback) synthesis"""
    print("\n" + "=" * 60)
    print("Testing pyttsx3 TTS Engine (Fallback)")
    print("=" * 60)
    
    try:
        print("\n1. Initializing pyttsx3 TTS engine...")
        tts = TextToSpeechEngine(provider="pyttsx3")
        print("   ✅ pyttsx3 TTS initialized successfully!")
        
        print("\n2. Testing TTS synthesis...")
        test_text = "I love you so much!"
        output_file = "audio_output/test_pyttsx3_synthesis.wav"
        
        os.makedirs("audio_output", exist_ok=True)
        
        print(f"   Synthesizing: '{test_text}'")
        duration = tts.text_to_speech(test_text, output_file)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"   ✅ Audio generated successfully!")
            print(f"   - File: {output_file}")
            print(f"   - Size: {file_size} bytes")
            print(f"   - Duration: {duration:.2f} seconds")
            return True
        else:
            print(f"   ❌ Audio file not created")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("\n")
    print("🎵 Virtual Girlfriend AI - TTS Engine Test")
    print("Testing both Coqui and pyttsx3 providers")
    print()
    
    coqui_ok = test_coqui_tts()
    pyttsx3_ok = test_pyttsx3_tts()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Coqui TTS:    {'✅ PASS' if coqui_ok else '❌ FAIL'}")
    print(f"pyttsx3 TTS:  {'✅ PASS' if pyttsx3_ok else '❌ FAIL'}")
    print()
    
    if coqui_ok and pyttsx3_ok:
        print("✅ All TTS engines working! System ready for production use.")
        sys.exit(0)
    elif pyttsx3_ok:
        print("⚠️  Fallback TTS working, but Coqui failed. System operational with fallback.")
        sys.exit(0)
    else:
        print("❌ TTS engine failed. System not ready.")
        sys.exit(1)
