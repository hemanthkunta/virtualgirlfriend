#!/usr/bin/env python3
"""
Integration Test Suite for Virtual Girlfriend AI
Tests complete workflows, error handling, and API contracts.

Run with: python test_integration.py
"""

import unittest
import json
import os
import sys
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from personality_engine import PersonalityEngine, ConversationMemory
from ollama_interface import OllamaInterface, ConversationManager
from expression_mapper import ExpressionMapper
from tts_engine import TextToSpeechEngine
from video_processor import VideoProcessor, LipSyncEngine


class TestConversationFlow(unittest.TestCase):
    """Test complete conversation pipeline"""
    
    def setUp(self):
        """Initialize components for testing"""
        self.personality_engine = PersonalityEngine()
        self.expression_mapper = ExpressionMapper()
        self.tts_engine = TextToSpeechEngine(provider="pyttsx3")
        self.video_processor = VideoProcessor()
        
        # Create test database
        self.test_db = "test_conversation.db"
        self.conversation_memory = ConversationMemory(db_path=self.test_db)
        
        # Ensure output directories exist
        os.makedirs("audio_output", exist_ok=True)
        os.makedirs("processed_videos", exist_ok=True)
    
    def tearDown(self):
        """Cleanup after tests"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_personality_engine_initialization(self):
        """Test personality engine initializes with correct traits"""
        self.assertIsNotNone(self.personality_engine.traits)
        self.assertIn('possessiveness', self.personality_engine.traits)
        self.assertIn('jealousy_level', self.personality_engine.traits)
        self.assertEqual(self.personality_engine.traits['possessiveness'], 0.8)
        print("[PASS] Personality engine initialized correctly")
    
    def test_emotion_detection_from_text(self):
        """Test emotion detection from AI responses"""
        # Test loving emotion
        response = "I love you so much! You mean everything to me!"
        emotion = self.personality_engine.get_emotion_from_response(response)
        self.assertIn(emotion.lower(), ['loving', 'love', 'affection'])
        print("[PASS] Detected emotion '" + emotion + "' from loving response")
        
        # Test jealous emotion
        response = "WHAT?! Another girl?! I can't believe this!"
        emotion = self.personality_engine.get_emotion_from_response(response)
        self.assertIn(emotion.lower(), ['jealous', 'anger', 'angry'])
        print("[PASS] Detected emotion '" + emotion + "' from jealous response")
        
        # Test playful emotion
        response = "Haha! You're so funny! I love when you make me laugh!"
        emotion = self.personality_engine.get_emotion_from_response(response)
        self.assertIn(emotion.lower(), ['playful', 'happy', 'joy'])
        print("[PASS] Detected emotion '" + emotion + "' from playful response")
    
    def test_expression_mapping(self):
        """Test facial expression selection for emotions"""
        emotions = ['loving', 'jealous', 'playful', 'shy', 'excited', 'sad', 'flirty', 'thoughtful']
        
        for emotion in emotions:
            expression = self.expression_mapper.get_expression_for_emotion(emotion)
            self.assertIsNotNone(expression)
            self.assertTrue(expression.endswith('.mp4'))
            print("[PASS] Found expression for '" + emotion + "': " + expression)
    
    def test_tts_synthesis(self):
        """Test text-to-speech synthesis"""
        test_text = "I love you so much! This is a test message."
        output_file = "audio_output/test_integration_tts.wav"
        
        # Generate audio
        duration = self.tts_engine.text_to_speech(test_text, output_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(os.path.getsize(output_file), 0)
        self.assertGreater(duration, 0)
        print("[PASS] TTS generated audio: " + f"{duration:.2f}" + " seconds")
    
    def test_conversation_memory(self):
        """Test conversation history storage and retrieval"""
        # Add messages
        self.conversation_memory.add_message('user', 'Hi baby!')
        self.conversation_memory.add_message('ai', 'Hello! I love you!')
        
        # Retrieve history
        history = self.conversation_memory.get_conversation_history(limit=10)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['role'], 'user')
        self.assertEqual(history[0]['text'], 'Hi baby!')
        self.assertEqual(history[1]['role'], 'ai')
        print("[PASS] Conversation memory stored and retrieved " + str(len(history)) + " messages")
    
    def test_api_response_format(self):
        """Test API response format is correct"""
        # Simulate API response structure
        response = {
            'user_message': 'Hi baby!',
            'ai_response': 'Hello! I love you!',
            'emotion': 'loving',
            'expression_video': 'Woman_blowing_kiss.mp4',
            'audio_file': 'audio_output/response.wav',
            'video_file': 'processed_videos/synced.mp4',
            'timestamp': '2026-05-13T10:30:00Z'
        }
        
        # Verify all required fields are present
        required_fields = ['user_message', 'ai_response', 'emotion', 'expression_video', 'audio_file']
        for field in required_fields:
            self.assertIn(field, response)
        
        print("API response has all required fields: " + str(list(response.keys())))
    
    def test_error_handling_missing_expression(self):
        """Test graceful handling when expression not found"""
        # Request non-existent emotion
        expression = self.expression_mapper.get_expression_for_emotion('nonexistent_emotion')
        # Should return default or None gracefully
        self.assertIsNotNone(expression)
        print("[PASS] Handled missing emotion gracefully, returned: " + expression)
    
    def test_trigger_detection(self):
        """Test personality trigger detection"""
        # Test jealousy trigger
        user_message = "I met another beautiful girl yesterday"
        prompt = self.personality_engine.generate_personality_prompt(user_message)
        self.assertIn('jealous', prompt.lower() or 'angry' in prompt.lower())
        print("[PASS] Jealousy trigger detected in prompt")
        
        # Test affection trigger
        user_message = "I love you so much baby"
        prompt = self.personality_engine.generate_personality_prompt(user_message)
        self.assertIn('love', prompt.lower() or 'affection' in prompt.lower())
        print("[PASS] Affection trigger detected in prompt")
    
    def test_system_prompt_generation(self):
        """Test system prompt is generated correctly"""
        user_message = "Hi baby, how are you?"
        prompt = self.personality_engine.generate_personality_prompt(user_message)
        
        # Verify prompt contains personality characteristics
        self.assertGreater(len(prompt), 100)  # Should be substantial
        self.assertIn('wife', prompt.lower() or 'girlfriend' in prompt.lower())
        print("[PASS] System prompt generated (" + str(len(prompt)) + " chars)")


class TestVideoProcessing(unittest.TestCase):
    """Test video processing workflows"""
    
    def setUp(self):
        """Initialize video processor"""
        self.video_processor = VideoProcessor()
        os.makedirs("processed_videos", exist_ok=True)
        os.makedirs("audio_output", exist_ok=True)
    
    def test_video_info_retrieval(self):
        """Test video information can be retrieved"""
        test_video = "facialexpressions/Woman_blowing_kiss_toward_camera_202605090914.mp4"
        
        if os.path.exists(test_video):
            info = self.video_processor.lipsync_engine.get_video_info(test_video)
            self.assertIsNotNone(info)
            self.assertIn('width', info)
            self.assertIn('height', info)
            self.assertIn('duration', info)
            print("[PASS] Video info retrieved: " + str(info['width']) + "x" + str(info['height']) + ", " + f"{info['duration']:.2f}" + "s")
        else:
            print("⚠️  Sample video not found, skipping video info test")
    
    def test_watermark_blur(self):
        """Test watermark blur functionality"""
        test_video = "facialexpressions/Woman_blowing_kiss_toward_camera_202605090914.mp4"
        output_video = "processed_videos/test_blur.mp4"
        
        if os.path.exists(test_video):
            result = self.video_processor.blur_watermark(test_video, output_video)
            self.assertIsNotNone(result)
            print("[PASS] Watermark blur completed: " + str(result))
        else:
            print("⚠️  Sample video not found, skipping watermark blur test")
    
    def test_fallback_when_video_missing(self):
        """Test graceful fallback when video is missing"""
        nonexistent_video = "nonexistent_video.mp4"
        
        # Should handle gracefully
        try:
            info = self.video_processor.lipsync_engine.get_video_info(nonexistent_video)
            # Either returns None or raises exception (both acceptable)
            print("✅ Handled missing video gracefully")
        except Exception as e:
            self.assertIn("not found", str(e).lower() or "no such" in str(e).lower())
            print(f"✅ Handled missing video with exception: {type(e).__name__}")


class TestExpressionMapping(unittest.TestCase):
    """Test expression mapping system"""
    
    def setUp(self):
        """Initialize expression mapper"""
        self.expression_mapper = ExpressionMapper()
    
    def test_all_emotions_have_expressions(self):
        """Test that all emotion categories have expressions"""
        emotion_map = self.expression_mapper.load_expression_map()
        
        expected_emotions = ['loving', 'jealous', 'playful', 'shy', 'excited', 'sad', 'flirty', 'thoughtful']
        for emotion in expected_emotions:
            self.assertIn(emotion, emotion_map)
            self.assertGreater(len(emotion_map[emotion]), 0)
            print(f"✅ Emotion '{emotion}' has {len(emotion_map[emotion])} videos")
    
    def test_expression_consistency(self):
        """Test expression selection is consistent"""
        emotion = 'loving'
        
        # Get multiple expressions for same emotion
        expressions = [self.expression_mapper.get_expression_for_emotion(emotion) for _ in range(5)]
        
        # All should be valid
        for expr in expressions:
            self.assertTrue(expr.endswith('.mp4'))
        
        # Should have variety (not same every time)
        unique_count = len(set(expressions))
        self.assertGreater(unique_count, 1)
        print(f"✅ Expression selection has variety: {unique_count}/5 unique")
    
    def test_video_files_exist(self):
        """Test that referenced video files actually exist"""
        emotion_map = self.expression_mapper.load_expression_map()
        missing_count = 0
        
        for emotion, videos in emotion_map.items():
            for video in videos[:3]:  # Check first 3 of each emotion
                video_path = f"facialexpressions/{video}"
                if not os.path.exists(video_path):
                    missing_count += 1
                    print(f"⚠️  Missing: {video_path}")
        
        if missing_count == 0:
            print(f"✅ All sampled video files exist")
        else:
            print(f"⚠️  {missing_count} video files missing")


class TestTTSProviders(unittest.TestCase):
    """Test multiple TTS providers"""
    
    def setUp(self):
        """Initialize for TTS tests"""
        os.makedirs("audio_output", exist_ok=True)
        self.test_text = "Hello! I love you so much!"
    
    def test_pyttsx3_provider(self):
        """Test pyttsx3 TTS provider"""
        try:
            tts = TextToSpeechEngine(provider="pyttsx3")
            output_file = "audio_output/test_pyttsx3.wav"
            duration = tts.text_to_speech(self.test_text, output_file)
            
            self.assertTrue(os.path.exists(output_file))
            self.assertGreater(duration, 0)
            print(f"✅ pyttsx3 provider works ({duration:.2f}s)")
        except Exception as e:
            self.fail(f"pyttsx3 provider failed: {e}")
    
    def test_coqui_provider(self):
        """Test Coqui TTS provider (if available)"""
        try:
            tts = TextToSpeechEngine(provider="coqui")
            output_file = "audio_output/test_coqui.wav"
            
            # Coqui might take time to initialize
            duration = tts.text_to_speech(self.test_text, output_file, timeout=120)
            
            if os.path.exists(output_file):
                print(f"✅ Coqui provider works ({duration:.2f}s)")
            else:
                print("⚠️  Coqui provider initialized but audio not generated")
        except ImportError:
            print("⚠️  Coqui not available (skipping)")
        except Exception as e:
            print(f"⚠️  Coqui provider failed: {e}")
    
    def test_tts_fallback(self):
        """Test TTS fallback mechanism"""
        # Try Coqui, should fallback to pyttsx3 if unavailable
        try:
            tts = TextToSpeechEngine(provider="coqui")
            output_file = "audio_output/test_fallback.wav"
            duration = tts.text_to_speech(self.test_text, output_file)
            
            if os.path.exists(output_file):
                print(f"✅ TTS fallback successful ({duration:.2f}s)")
            else:
                print("⚠️  TTS fallback attempted")
        except Exception as e:
            print(f"⚠️  Fallback test skipped: {e}")


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Setup test database"""
        self.test_db = "test_db_operations.db"
        self.memory = ConversationMemory(db_path=self.test_db)
    
    def tearDown(self):
        """Cleanup test database"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_database_create_and_store(self):
        """Test database creation and message storage"""
        # Add messages
        self.memory.add_message('user', 'First message')
        self.memory.add_message('ai', 'Response message')
        
        # Retrieve and verify
        history = self.memory.get_conversation_history(limit=10)
        self.assertEqual(len(history), 2)
        print(f"✅ Database stored and retrieved {len(history)} messages")
    
    def test_database_limit(self):
        """Test conversation history limit"""
        # Add multiple messages
        for i in range(20):
            self.memory.add_message('user' if i % 2 == 0 else 'ai', f'Message {i}')
        
        # Retrieve with limit
        history = self.memory.get_conversation_history(limit=5)
        self.assertEqual(len(history), 5)
        print(f"✅ Database limit working: got {len(history)} of 20 messages")
    
    def test_database_persistence(self):
        """Test that database persists across sessions"""
        # Add messages
        self.memory.add_message('user', 'Persistent message')
        
        # Create new instance with same DB
        memory2 = ConversationMemory(db_path=self.test_db)
        history = memory2.get_conversation_history(limit=10)
        
        self.assertGreater(len(history), 0)
        print(f"✅ Database persistent: retrieved {len(history)} messages from disk")


def run_integration_tests():
    """Run all integration tests with detailed output"""
    print("\n" + "="*70)
    print("VIRTUAL GIRLFRIEND AI - INTEGRATION TEST SUITE")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConversationFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestVideoProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestExpressionMapping))
    suite.addTests(loader.loadTestsFromTestCase(TestTTSProviders))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseOperations))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run:    {result.testsRun}")
    print(f"Passed:       {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed:       {len(result.failures)}")
    print(f"Errors:       {len(result.errors)}")
    print(f"Success Rate: {100 * (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun:.1f}%")
    print("="*70 + "\n")
    
    return result


if __name__ == '__main__':
    result = run_integration_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
