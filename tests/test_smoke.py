import os
import unittest

from src.expression_mapper import ExpressionMapper
from src.personality_engine import PersonalityEngine
from src.tts_engine import TextToSpeechEngine
from src.video_processor import LipSyncEngine, VideoProcessor


class SmokeTest(unittest.TestCase):
    def test_personality_engine_initializes(self):
        engine = PersonalityEngine()
        prompt = engine.generate_personality_prompt("Hello", [])
        self.assertIsInstance(prompt, str)
        self.assertTrue(prompt)

    def test_expression_mapper_initializes(self):
        mapper = ExpressionMapper()
        emotion = mapper.get_expression_for_emotion("happy")
        self.assertIsInstance(emotion, str)
        self.assertTrue(emotion)

    def test_tts_fallback_synthesizes_audio(self):
        engine = TextToSpeechEngine(provider="pyttsx3")
        output_file, duration = engine.synthesize("Sample smoke test text.", "smoke_test.wav")
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(duration, 0)

    def test_video_engines_initialize(self):
        video_processor = VideoProcessor()
        lipsync_engine = LipSyncEngine()
        self.assertIsNotNone(video_processor)
        self.assertIsNotNone(lipsync_engine)


if __name__ == "__main__":
    unittest.main()
