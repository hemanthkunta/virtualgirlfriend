#!/usr/bin/env python3
"""
Virtual Girlfriend AI - Complete Example Workflow
Demonstrates the full pipeline: text → AI response → TTS → video sync
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from personality_engine import PersonalityEngine, ConversationMemory
from ollama_interface import OllamaInterface, ConversationManager
from expression_mapper import ExpressionMapper
from tts_engine import TextToSpeechEngine
from video_processor import VideoProcessor, LipSyncEngine


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def example_complete_workflow():
    """Run complete workflow example"""
    
    print_header("🎬 Virtual Girlfriend AI - Complete Workflow")
    
    # 1. Initialize components
    print("\n1️⃣  Initializing components...")
    try:
        personality_engine = PersonalityEngine()
        print("   ✓ Personality engine initialized")
        
        ollama = OllamaInterface(model_name="mistral")
        print("   ✓ Ollama interface created")
        
        # Check Ollama connection
        if not ollama.check_connection():
            print("   ⚠️  WARNING: Cannot connect to Ollama server!")
            print("   Please start Ollama with: ollama serve")
            return
        
        print("   ✓ Ollama server connected")
        
        conversation_mgr = ConversationManager(ollama)
        expression_mapper = ExpressionMapper()
        print("   ✓ Expression mapper initialized")
        
        tts_engine = TextToSpeechEngine(provider="pyttsx3")
        print("   ✓ Text-to-speech engine initialized")
        
        lipsync_engine = LipSyncEngine()
        video_processor = VideoProcessor()
        print("   ✓ Video processing engines initialized")
        
        conversation_memory = ConversationMemory()
        print("   ✓ Conversation memory initialized")
        
    except Exception as e:
        print(f"   ❌ Error initializing components: {e}")
        return
    
    # 2. User input
    print_header("2️⃣  Processing User Input")
    
    user_message = "Hey babe! I love you so much 💕"
    print(f"User: {user_message}")
    
    # 3. Generate AI response with personality
    print_header("3️⃣  Generating AI Response")
    
    try:
        # Get conversation history for context
        history = conversation_memory.get_conversation_history(limit=3)
        history_text = [f"{msg['user']}" for msg in history]
        
        # Generate personality-driven system prompt
        system_prompt = personality_engine.generate_personality_prompt(
            user_message, 
            history_text
        )
        
        print("System Prompt Generated ✓")
        print(f"Prompt length: {len(system_prompt)} characters")
        
        # Generate response from Ollama
        print("\nCalling Ollama model (mistral)...")
        ai_response = conversation_mgr.generate_response(
            user_message=user_message,
            system_prompt=system_prompt,
            temperature=0.8
        )
        
        print(f"✓ AI Response: {ai_response}")
        
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return
    
    # 4. Emotion detection
    print_header("4️⃣  Detecting Emotion")
    
    emotion = personality_engine.get_emotion_from_response(ai_response)
    print(f"Detected emotion: {emotion.upper()} 💭")
    
    # 5. Select facial expression
    print_header("5️⃣  Selecting Facial Expression")
    
    try:
        video_expression = expression_mapper.get_expression_for_emotion(emotion)
        print(f"Selected video: {video_expression}")
        
        # Get full path
        video_path = os.path.join('facialexpressions', video_expression)
        if os.path.exists(video_path):
            print(f"✓ Video file found: {video_path}")
        else:
            print(f"⚠️  Video file not found: {video_path}")
    
    except Exception as e:
        print(f"❌ Error selecting expression: {e}")
        return
    
    # 6. Text-to-speech
    print_header("6️⃣  Generating Sweet Voice")
    
    try:
        output_audio = f"demo_response.wav"
        audio_path, duration = tts_engine.synthesize(ai_response, output_audio)
        
        print(f"✓ Audio generated: {output_audio}")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Path: {audio_path}")
    
    except Exception as e:
        print(f"❌ Error generating audio: {e}")
        return
    
    # 7. Lip-sync and merge
    print_header("7️⃣  Creating Lip-Synced Video")
    
    try:
        print(f"Video duration before sync: {lipsync_engine.get_video_duration(video_path):.2f}s")
        print(f"Audio duration: {duration:.2f}s")
        
        # Create output path
        output_video = "demo_output_synced.mp4"
        output_path = os.path.join('processed_videos', output_video)
        
        # Merge audio and video
        print("\nMerging audio with video...")
        result_path = lipsync_engine.merge_audio_video(video_path, audio_path, output_path)
        
        print(f"✓ Video created: {output_video}")
        print(f"  Full path: {result_path}")
    
    except Exception as e:
        print(f"❌ Error creating synced video: {e}")
        return
    
    # 8. Save to database
    print_header("8️⃣  Saving to Database")
    
    try:
        conversation_memory.save_conversation(
            user_msg=user_message,
            ai_response=ai_response,
            emotion=emotion,
            video_expr=video_expression,
            language='en'
        )
        print("✓ Conversation saved to database")
    
    except Exception as e:
        print(f"❌ Error saving: {e}")
    
    # 9. Summary
    print_header("✅ Workflow Complete!")
    
    print(f"""
    📝 User Input:        {user_message}
    🤖 AI Response:       {ai_response}
    💭 Emotion Detected:  {emotion}
    👧 Video Expression:  {video_expression}
    🎵 Audio Duration:    {duration:.2f} seconds
    🎬 Output Video:      {output_video}
    
    📁 Files Created:
       - Audio: audio_output/{output_audio}
       - Video: processed_videos/{output_video}
       - Database: virtualgirlfriend.db
    
    Next steps:
    1. Check the synced video in processed_videos/
    2. Run 'python app.py' to start the Flask server
    3. Access the web interface at http://localhost:5000
    """)


def example_simple_chat():
    """Simple chat example"""
    
    print_header("💬 Simple Chat Example")
    
    try:
        ollama = OllamaInterface(model_name="mistral")
        
        if not ollama.check_connection():
            print("❌ Cannot connect to Ollama server!")
            return
        
        personality_engine = PersonalityEngine()
        conversation_mgr = ConversationManager(ollama)
        
        # Test different messages
        test_messages = [
            "Hi baby, how's your day going?",
            "You're so beautiful 😍",
            "I met this girl at work today",
            "I missed you so much!",
        ]
        
        for msg in test_messages:
            print(f"\n👤 User: {msg}")
            
            system_prompt = personality_engine.generate_personality_prompt(msg, [])
            response = conversation_mgr.generate_response(msg, system_prompt, temperature=0.8)
            emotion = personality_engine.get_emotion_from_response(response)
            
            print(f"🤖 AI ({emotion}): {response}")
            print("-" * 50)
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_video_processing():
    """Example of video watermark processing"""
    
    print_header("🎬 Video Processing Example")
    
    try:
        video_processor = VideoProcessor()
        expression_mapper = ExpressionMapper()
        
        # Get a sample video
        video_file = expression_mapper.get_expression_for_emotion('loving')
        video_path = os.path.join('facialexpressions', video_file)
        
        if not os.path.exists(video_path):
            print(f"⚠️  Video not found: {video_path}")
            return
        
        print(f"Processing video: {video_file}")
        print(f"Full path: {video_path}")
        
        # Get video info
        info = video_processor._VideoProcessor__class__.get_video_info
        
        print("\nVideo processing pipeline:")
        print("1. Blur old watermark from original")
        print("2. Add new project watermark")
        print("3. Save processed video")
        print("\nThis is done automatically before syncing with audio")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_list_videos():
    """List all available facial expression videos"""
    
    print_header("📹 Available Facial Expressions")
    
    try:
        expression_mapper = ExpressionMapper()
        
        print("\nEmotions and their associated videos:\n")
        
        for emotion, videos in expression_mapper.expression_map.items():
            print(f"  {emotion.upper()}: {len(videos)} videos")
            for i, video in enumerate(videos[:3], 1):
                print(f"    {i}. {video}")
            if len(videos) > 3:
                print(f"    ... and {len(videos) - 3} more")
        
        print(f"\n✓ Total expressions: {sum(len(v) for v in expression_mapper.expression_map.values())}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Virtual Girlfriend AI - Example Workflows"
    )
    parser.add_argument(
        'mode',
        choices=['full', 'chat', 'video', 'list'],
        help='Example mode to run'
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs('audio_input', exist_ok=True)
    os.makedirs('audio_output', exist_ok=True)
    os.makedirs('processed_videos', exist_ok=True)
    
    if args.mode == 'full':
        example_complete_workflow()
    elif args.mode == 'chat':
        example_simple_chat()
    elif args.mode == 'video':
        example_video_processing()
    elif args.mode == 'list':
        example_list_videos()
