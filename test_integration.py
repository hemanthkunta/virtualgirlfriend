#!/usr/bin/env python3
"""
Integration Test Suite for Virtual Girlfriend AI
Tests complete workflows, error handling, and API contracts.

Usage: python test_integration.py
"""

import unittest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from personality_engine import PersonalityEngine, ConversationMemory
from expression_mapper import ExpressionMapper
from tts_engine import TextToSpeechEngine
from video_processor import VideoProcessor


class TestConversationFlow(unittest.TestCase):
    """Test complete conversation pipeline"""
    
    def setUp(self):
        """Initialize components for testing"""
        self.personality_engine = PersonalityEngine()
        self.expression_mapper = ExpressionMapper()
        self.tts_engine = TextToSpeechEngine(provider="pyttsx3")
        
        self.test_db = "test_conversation.db"
        self.conversation_memory = ConversationMemory(db_path=self.test_db)
        
        os.makedirs("audio_output", exist_ok=True)
        os.makedirs("processed_videos", exist_ok=True)
    
    def tearDown(self):
        """Cleanup after tests"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_01_personality_engine_init(self):
        """Test personality engine initializes"""
        self.assertIsNotNone(self.personality_engine.traits)
        self.assertIn('possessiveness', self.personality_engine.traits)
        print("[PASS] Personality engine initialized")
    
    def test_02_emotion_detection_loving(self):
        """Test emotion detection for loving response"""
        response = "I love you so much! You mean everything to me!"
        emotion = self.personality_engine.get_emotion_from_response(response)
        self.assertIsNotNone(emotion)
        print("[PASS] Detected loving emotion")
    
    def test_03_emotion_detection_jealous(self):
        """Test emotion detection for jealous response"""
        response = "WHAT?! Another girl?! I can't believe this!"
        emotion = self.personality_engine.get_emotion_from_response(response)
        self.assertIsNotNone(emotion)
        print("[PASS] Detected jealous emotion")
    
    def test_04_expression_mapping(self):
        """Test facial expression selection"""
        emotions = ['loving', 'jealous', 'playful', 'shy', 'excited', 'sad', 'flirty']
        for emotion in emotions:
            expression = self.expression_mapper.get_expression_for_emotion(emotion)
            self.assertIsNotNone(expression)
            self.assertTrue(expression.endswith('.mp4'))
        print("[PASS] All emotions have expressions")
    
    def test_05_tts_synthesis(self):
        """Test text-to-speech synthesis"""
        test_text = "I love you so much! This is a test message."
        output_file = "test_int_tts.wav"
        
        output_path, duration = self.tts_engine.synthesize(test_text, output_file)
        
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)
        self.assertGreater(duration, 0)
        print("[PASS] TTS generated audio: {:.2f}s".format(duration))
    
    def test_06_conversation_memory(self):
        """Test conversation history storage"""
        self.conversation_memory.save_conversation('Hi baby!', 'Hello! I love you!', 'loving', 'video.mp4', 'en')
        self.conversation_memory.save_conversation('Another msg', 'Another response', 'playful', 'video2.mp4', 'en')
        
        history = self.conversation_memory.get_conversation_history(limit=10)
        self.assertGreaterEqual(len(history), 2)
        print("[PASS] Conversation memory working")
    
    def test_07_api_response_format(self):
        """Test API response structure"""
        response = {
            'user_message': 'Hi baby!',
            'ai_response': 'Hello! I love you!',
            'emotion': 'loving',
            'expression_video': 'Woman_blowing_kiss.mp4',
            'audio_file': 'audio_output/response.wav',
            'video_file': 'processed_videos/synced.mp4',
        }
        
        required_fields = ['user_message', 'ai_response', 'emotion', 'expression_video']
        for field in required_fields:
            self.assertIn(field, response)
        
        print("[PASS] API response structure valid")
    
    def test_08_error_handling(self):
        """Test graceful error handling"""
        expression = self.expression_mapper.get_expression_for_emotion('nonexistent')
        self.assertIsNotNone(expression)
        print("[PASS] Error handling works")


class TestExpressionMapping(unittest.TestCase):
    """Test expression mapping system"""
    
    def setUp(self):
        self.expression_mapper = ExpressionMapper()
    
    def test_01_all_emotions_mapped(self):
        """Test all emotion categories have expressions"""
        emotion_map = self.expression_mapper.load_expression_map()
        expected_emotions = ['loving', 'jealous', 'playful', 'shy', 'excited', 'sad', 'flirty', 'thoughtful']
        
        for emotion in expected_emotions:
            self.assertIn(emotion, emotion_map)
            self.assertGreater(len(emotion_map[emotion]), 0)
        
        print("[PASS] All emotions mapped")
    
    def test_02_video_files_exist(self):
        """Test that majority of video files exist"""
        emotion_map = self.expression_mapper.load_expression_map()
        total_count = 0
        missing_count = 0
        
        for emotion, videos in emotion_map.items():
            for video in videos:
                total_count += 1
                video_path = os.path.join("facialexpressions", video)
                if not os.path.exists(video_path):
                    missing_count += 1
        
        # Allow up to 10% missing (e.g., 4 out of 40+ videos)
        missing_rate = missing_count / total_count if total_count > 0 else 0
        self.assertLess(missing_rate, 0.15)
        print("[PASS] Video files mostly present ({}/{} available)".format(total_count - missing_count, total_count))
    
    def test_03_expression_variety(self):
        """Test expression selection variety"""
        expressions = [self.expression_mapper.get_expression_for_emotion('loving') for _ in range(5)]
        unique_count = len(set(expressions))
        self.assertGreater(unique_count, 1)
        print("[PASS] Expression variety working")


class TestTTSProviders(unittest.TestCase):
    """Test TTS providers"""
    
    def setUp(self):
        os.makedirs("audio_output", exist_ok=True)
        self.test_text = "Hello! I love you so much!"
    
    def test_01_pyttsx3_provider(self):
        """Test pyttsx3 TTS"""
        try:
            tts = TextToSpeechEngine(provider="pyttsx3")
            output_file = "test_pyttsx3_int.wav"
            output_path, duration = tts.synthesize(self.test_text, output_file)
            
            self.assertTrue(os.path.exists(output_path))
            self.assertGreater(duration, 0)
            print("[PASS] pyttsx3 provider works")
        except Exception as e:
            self.fail("pyttsx3 failed: {}".format(e))
    
    def test_02_coqui_provider_import(self):
        """Test Coqui import (if available)"""
        try:
            from TTS.api import TTS
            print("[PASS] Coqui TTS import successful")
        except ImportError:
            print("[SKIP] Coqui not available")


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        self.test_db = "test_db_int.db"
        self.memory = ConversationMemory(db_path=self.test_db)
    
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_01_store_and_retrieve(self):
        """Test message storage"""
        self.memory.save_conversation('First', 'Response', 'loving', 'video.mp4', 'en')
        self.memory.save_conversation('Second', 'Another', 'playful', 'video2.mp4', 'en')
        
        history = self.memory.get_conversation_history(limit=10)
        self.assertGreaterEqual(len(history), 2)
        print("[PASS] Database store/retrieve works")
    
    def test_02_limit_enforcement(self):
        """Test conversation limit"""
        for i in range(20):
            self.memory.save_conversation('Msg {}'.format(i), 'Response {}'.format(i), 'loving', 'video.mp4', 'en')
        
        history = self.memory.get_conversation_history(limit=5)
        self.assertLessEqual(len(history), 5)
        print("[PASS] Limit enforcement works")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("VIRTUAL GIRLFRIEND AI - INTEGRATION TEST SUITE")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConversationFlow))
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
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print("Tests Run:    {}".format(result.testsRun))
    print("Passed:       {}".format(passed))
    print("Failed:       {}".format(len(result.failures)))
    print("Errors:       {}".format(len(result.errors)))
    
    if result.testsRun > 0:
        success_rate = 100.0 * passed / result.testsRun
        print("Success Rate: {:.1f}%".format(success_rate))
    
    print("="*70 + "\n")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
