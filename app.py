import os
import json
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import uuid
from typing import Dict, Tuple

# Import custom modules
from src.personality_engine import PersonalityEngine, ConversationMemory
from src.ollama_interface import OllamaInterface, ConversationManager
from src.expression_mapper import ExpressionMapper
from src.tts_engine import TextToSpeechEngine, AudioProcessor
from src.video_processor import VideoProcessor, LipSyncEngine

# Initialize Flask app
app = Flask(__name__)

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO').upper(),
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Configure CORS to allow requests from frontend
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file upload

# Initialize components
conversation_memory = ConversationMemory(
    database_url=os.getenv(
        'DATABASE_URL',
        f"sqlite:///{os.getenv('DATABASE_PATH', 'virtualgirlfriend.db')}"
    )
)
personality_engine = PersonalityEngine()
expression_mapper = ExpressionMapper()
ollama = OllamaInterface(
    base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
    model_name=os.getenv('OLLAMA_MODEL', 'llama3.2:1b')
)
conversation_mgr = ConversationManager(ollama)

# Initialize TTS with error handling
try:
    from src.tts_engine import get_recommended_tts_config
    recommended_config = get_recommended_tts_config()
    logger.info("Using TTS Provider: %s", recommended_config['provider'])
    tts_engine = TextToSpeechEngine(
        provider=recommended_config['provider'],
        voice_id=recommended_config.get('voice_id')
    )
except Exception as e:
    logger.warning("TTS initialization failed: %s", e)
    logger.warning("Falling back to silent mode. Audio synthesis will not work until configured.")
    tts_engine = None

audio_processor = AudioProcessor()
video_processor = VideoProcessor()
lipsync_engine = LipSyncEngine()

# State
current_user_session = {
    'language': 'en',
    'user_id': str(uuid.uuid4()),
    'conversation_history': []
}


@app.route('/api/status', methods=['GET'])
def get_status():
    """Check system status"""
    ollama_connected = ollama.check_connection()
    available_models = ollama.list_available_models() if ollama_connected else []
    
    return jsonify({
        'status': 'ready' if ollama_connected else 'error',
        'ollama_connected': ollama_connected,
        'available_models': available_models,
        'user_session': current_user_session
    })


@app.route('/api/set-language', methods=['POST'])
def set_language():
    """Set user language preference"""
    data = request.json
    language = data.get('language', 'en')
    
    current_user_session['language'] = language
    
    return jsonify({
        'success': True,
        'language': language,
        'message': f'Language set to {language}'
    })


@app.route('/api/chat/text', methods=['POST'])
def chat_text(override_message=None, override_language=None, override_persona=None):
    """
    Handle text input chat
    """
    try:
        data = request.json or {}
        user_message = override_message or data.get('user_message', '')
        language = override_language or data.get('language', current_user_session['language'])
        persona = override_persona or data.get('persona', 'girlfriend')
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Generate AI response with personality
        print(f"User: {user_message}")
        
        # Get conversation context
        history = conversation_memory.get_conversation_history(limit=3)
        history_text = [f"{msg['user']}\n{msg['ai']}" for msg in history]
        
        # Generate personality prompt
        system_prompt = personality_engine.generate_personality_prompt(
            user_message, 
            history_text,
            persona
        )
        
        # Get AI response from Ollama
        ai_response = conversation_mgr.generate_response(
            user_message=user_message,
            system_prompt=system_prompt,
            temperature=0.8
        )
        
        print(f"AI: {ai_response}")
        
        # Split response into sentences for dynamic expressions
        import re
        # Basic sentence splitting keeping punctuation
        sentences = re.split(r'(?<=[.!?])\s+', ai_response)
        
        segments = []
        for sentence in sentences:
            if not sentence.strip(): continue
            seg_emotion = personality_engine.get_emotion_from_response(sentence)
            seg_video = expression_mapper.get_expression_for_emotion(seg_emotion)
            
            seg_audio_file = f"response_{uuid.uuid4().hex[:8]}.wav"
            try:
                seg_audio_path, seg_duration = tts_engine.synthesize(sentence, seg_audio_file)
            except Exception as e:
                print(f"TTS synthesis failed for segment: {e}")
                continue
                
            segments.append({
                'text': sentence,
                'emotion': seg_emotion,
                'video_expression': seg_video,
                'audio_file': os.path.basename(seg_audio_path),
                'duration': seg_duration
            })
            
        # Fallback if no segments generated
        if not segments:
            emotion = personality_engine.get_emotion_from_response(ai_response)
            video_expression = expression_mapper.get_expression_for_emotion(emotion)
            output_audio = f"response_{uuid.uuid4().hex[:8]}.wav"
            audio_path, duration = tts_engine.synthesize(ai_response, output_audio)
            segments.append({
                'text': ai_response,
                'emotion': emotion,
                'video_expression': video_expression,
                'audio_file': os.path.basename(audio_path),
                'duration': duration
            })
        
        # We still store the overall emotion for history
        emotion = personality_engine.get_emotion_from_response(ai_response)
        video_expression = segments[0]['video_expression'] if segments else expression_mapper.get_expression_for_emotion(emotion)
        
        # Save to conversation memory
        conversation_memory.save_conversation(
            user_msg=user_message,
            ai_response=ai_response,
            emotion=emotion,
            video_expr=video_expression,
            language=language
        )
        
        return jsonify({
            'success': True,
            'ai_response': ai_response,
            'emotion': emotion,
            'video_expression': video_expression,
            'audio_file': segments[0]['audio_file'] if segments else '',
            'duration': sum(s['duration'] for s in segments) if segments else 0,
            'language': language,
            'segments': segments
        })
    
    except Exception as e:
        logger.exception("Error in chat_text")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/audio', methods=['POST'])
def chat_audio():
    """
    Handle audio input (speech-to-text then chat)
    
    Multipart form:
        - audio: Audio file (WAV, MP3, etc.)
        - language: Language code
    
    Response:
        {
            "transcribed_text": "Hi baby",
            "ai_response": "Hey honey!",
            ...same as /api/chat/text response
        }
    """
    try:
        # Get audio file
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', current_user_session['language'])
        
        # Save temporary audio file
        temp_audio = f"temp_audio_{uuid.uuid4().hex[:8]}.wav"
        audio_path = os.path.join('audio_input', temp_audio)
        audio_file.save(audio_path)
        
        # Convert speech to text
        print("Transcribing audio...")
        transcribed_text = audio_processor.speech_to_text_whisper(audio_path)
        print(f"Transcribed: {transcribed_text}")
        
        # Now process as text chat
        persona = request.form.get('persona', 'girlfriend')
        
        # Call chat_text with the transcribed text
        response = chat_text(override_message=transcribed_text, override_language=language, override_persona=persona)
        response_json = response.get_json()
        
        # Add transcribed text to response
        response_json['transcribed_text'] = transcribed_text
        
        # Clean up temp file
        try:
            os.remove(audio_path)
        except:
            pass
        
        return jsonify(response_json)
    
    except Exception as e:
        logger.exception("Error in chat_audio")
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/sync', methods=['POST'])
def sync_audio_video():
    """
    Merge audio and video with lip-sync
    
    Request:
        {
            "video_file": "Woman_blowing_kiss_toward_camera.mp4",
            "audio_file": "response_xxxxx.wav"
        }
    
    Response:
        {
            "output_video": "synced_video_xxxxx.mp4",
            "duration": 5.2
        }
    """
    try:
        data = request.json
        video_file = data.get('video_file')
        audio_file = data.get('audio_file')
        
        if not video_file or not audio_file:
            return jsonify({'error': 'Missing video or audio file'}), 400
        
        # Get full paths
        video_path = os.path.join('facialexpressions', video_file)
        audio_path = os.path.join('audio_output', audio_file)
        
        # Generate unique output filename
        output_video = f"synced_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join('processed_videos', output_video)
        
        print(f"Syncing video {video_file} with audio {audio_file}")
        
        # Merge audio and video using API
        result_path = lipsync_engine.generate_api_lipsync(video_path, audio_path, output_path)
        
        # Get duration
        duration = lipsync_engine.get_audio_duration(audio_path)
        
        return jsonify({
            'success': True,
            'output_video': os.path.basename(result_path),
            'duration': duration,
            'video_path': result_path
        })
    
    except Exception as e:
        logger.exception("Error in sync_audio_video")
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/process', methods=['POST'])
def process_video():
    """
    Process facial expression video (blur watermark, add new watermark)
    
    Request:
        {
            "video_file": "Girl_giggling_with_joy_202605090914.mp4",
            "blur_old": true,
            "add_watermark": true
        }
    """
    try:
        data = request.json
        video_file = data.get('video_file')
        blur_old = data.get('blur_old', True)
        add_watermark = data.get('add_watermark', True)
        
        if not video_file:
            return jsonify({'error': 'Missing video file'}), 400
        
        video_path = os.path.join('facialexpressions', video_file)
        
        print(f"Processing video: {video_file}")
        
        # Process video
        processed_path = video_processor.process_expression_video(
            video_path,
            blur_watermark=blur_old,
            add_watermark=add_watermark
        )
        
        return jsonify({
            'success': True,
            'processed_video': os.path.basename(processed_path),
            'output_path': processed_path
        })
    
    except Exception as e:
        logger.exception("Error in process_video")
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversation/history', methods=['GET'])
def get_conversation_history():
    """Get conversation history"""
    limit = request.args.get('limit', 10, type=int)
    history = conversation_memory.get_conversation_history(limit)
    
    return jsonify({
        'success': True,
        'history': history,
        'count': len(history)
    })


@app.route('/api/conversation/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history and start fresh"""
    conversation_memory.conversation_history = []
    conversation_mgr.clear_history()
    
    return jsonify({
        'success': True,
        'message': 'Conversation history cleared'
    })


@app.route('/api/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve audio file"""
    try:
        audio_path = os.path.join('audio_output', filename)
        return send_file(audio_path, mimetype='audio/wav')
    except:
        return jsonify({'error': 'Audio not found'}), 404


@app.route('/api/video/<filename>', methods=['GET'])
def serve_video(filename):
    """Serve video file"""
    try:
        video_path = os.path.join('processed_videos', filename)
        return send_file(video_path, mimetype='video/mp4')
    except:
        return jsonify({'error': 'Video not found'}), 404


@app.route('/api/expression/<filename>', methods=['GET'])
def serve_expression(filename):
    """Serve un-processed expression video for idle state"""
    try:
        video_path = os.path.join('facialexpressions', filename)
        return send_file(video_path, mimetype='video/mp4')
    except:
        return jsonify({'error': 'Video not found'}), 404

@app.route('/api/expressions/list', methods=['GET'])
def list_expressions():
    """List all available facial expressions"""
    facialexpressions_dir = 'facialexpressions'
    
    videos = []
    if os.path.exists(facialexpressions_dir):
        videos = [f for f in os.listdir(facialexpressions_dir) 
                 if f.endswith('.mp4')]
    
    # Map videos to emotions
    mapped = {}
    for emotion, video_list in expression_mapper.expression_map.items():
        mapped[emotion] = [v for v in video_list if os.path.exists(
            os.path.join(facialexpressions_dir, v)
        )]
    
    return jsonify({
        'total_videos': len(videos),
        'all_videos': sorted(videos),
        'emotion_mapping': mapped
    })


@app.route('/api/models/list', methods=['GET'])
def list_models():
    """List available Ollama models"""
    models = ollama.list_available_models()
    return jsonify({'models': models})


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': str(uuid.uuid4())})


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('audio_input', exist_ok=True)
    os.makedirs('audio_output', exist_ok=True)
    os.makedirs('processed_videos', exist_ok=True)
    
    # Check Ollama connection
    if not ollama.check_connection():
        print("⚠️  WARNING: Ollama server is not running!")
        print("Please start Ollama with: ollama serve")
        print("And pull a model: ollama pull mistral")
    
    # Start Flask app
    print("🚀 Virtual Girlfriend AI - Starting server...")
    print("📝 API Documentation:")
    print("   POST /api/chat/text - Send text message")
    print("   POST /api/chat/audio - Send voice message")
    print("   POST /api/video/sync - Sync audio with facial expression")
    print("   GET  /api/conversation/history - Get chat history")
    print("")
    
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')
    app.run(debug=debug_mode, port=int(os.getenv('PORT', '5000')), host='0.0.0.0')
