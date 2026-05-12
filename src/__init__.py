# Virtual Girlfriend AI - Source Package
# Initialization file for src module

from .personality_engine import PersonalityEngine, ConversationMemory
from .ollama_interface import OllamaInterface, ConversationManager
from .expression_mapper import ExpressionMapper
from .tts_engine import TextToSpeechEngine, AudioProcessor
from .video_processor import VideoProcessor, LipSyncEngine

__version__ = "1.0.0"
__author__ = "Virtual Girlfriend AI Team"

__all__ = [
    'PersonalityEngine',
    'ConversationMemory',
    'OllamaInterface',
    'ConversationManager',
    'ExpressionMapper',
    'TextToSpeechEngine',
    'AudioProcessor',
    'VideoProcessor',
    'LipSyncEngine',
]
