# 🎬 Virtual Girlfriend AI - Complete Implementation Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
# Make sure you have Python 3.9+
python --version

# Install required packages
pip install -r requirements.txt

# Install FFmpeg (for video processing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### Step 2: Install & Run Ollama
```bash
# Download Ollama from https://ollama.ai
# Or via brew on macOS:
brew install ollama

# Start Ollama server
ollama serve

# In another terminal, pull a model:
ollama pull mistral
# OR: ollama pull neural-chat
# OR: ollama pull dolphin-mixtral
```

### Step 3: Configure Environment
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your settings (most defaults are fine)
nano .env
```

### Step 4: Start the Application
```bash
# Create required directories
mkdir -p audio_input audio_output processed_videos

# Run the Flask server
python app.py

# Server starts on http://localhost:5000
```

---

## 🏗️ Project Architecture

```
virtualgirlfriend/
├── 📂 facialexpressions/          ← Your 48 facial expression videos
│   ├── Woman_blowing_kiss_toward_camera_202605090914.mp4
│   ├── Woman_with_playful_smirk_202605090914.mp4
│   └── ... (43 more videos)
│
├── 📂 src/                        ← Core Python modules
│   ├── personality_engine.py      ← Wife roleplay behavior
│   ├── ollama_interface.py        ← Ollama AI model integration
│   ├── expression_mapper.py       ← Emotion → Video expression mapping
│   ├── tts_engine.py              ← Text-to-speech synthesis
│   ├── audio_processor.py         ← Speech recognition & audio processing
│   ├── lipsync_engine.py          ← Audio-video synchronization
│   └── video_processor.py         ← Video editing (watermarks, etc.)
│
├── 📂 frontend/                   ← React web interface (create-react-app)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── package.json
│
├── 📂 config/
│   ├── app.conf                   ← Configuration file
│   └── languages.json             ← Language settings
│
├── 📂 audio_input/                ← User recorded voice
├── 📂 audio_output/               ← Generated AI voice response
├── 📂 processed_videos/           ← Final synced video outputs
│
├── app.py                         ← Main Flask API server
├── requirements.txt               ← Python dependencies
├── .env.example                   ← Environment variables template
├── PROJECT_ARCHITECTURE.md        ← Full system design
└── README.md                      ← This file
```

---

## 🔧 How It Works - The Complete Flow

### User Interaction Flow

```
┌─────────────────────────────────────────────────────────┐
│  USER (Frontend Web Interface)                           │
│  - Selects language                                      │
│  - Types text OR records voice message                   │
└─────────────┬───────────────────────────────────────────┘
              │
              ↓ (HTTP POST to /api/chat/text or /api/chat/audio)
┌─────────────────────────────────────────────────────────┐
│  SPEECH-TO-TEXT (if voice input)                         │
│  - Whisper model converts audio → text                   │
│  - Result: "Hi baby, I missed you"                       │
└─────────────┬───────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────────┐
│  PERSONALITY ENGINE                                      │
│  - Analyzes user message for triggers                    │
│  - Detects: jealousy triggers, affection, etc.           │
│  - Generates personalized system prompt                  │
└─────────────┬───────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────────┐
│  OLLAMA AI MODEL                                         │
│  - Receives: personality prompt + user message           │
│  - Uses conversation history for context                │
│  - Generates response: "Hey babe! I missed you so much!  │
│    Don't make me jealous talking about other girls 😤"   │
└─────────────┬───────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────────┐
│  EMOTION DETECTION                                       │
│  - Extract emotion from AI response                      │
│  - Keywords/emojis detect: "angry", "loving", etc.       │
│  - Result: "jealous"                                     │
└─────────────┬───────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────────┐
│  EXPRESSION MAPPER                                       │
│  - Maps emotion → facial expression video               │
│  - For "jealous": select from grumpy, eye-roll, pout    │
│  - Result: "Woman_with_controlled_anger_202605090914.mp4"│
└─────────────┬───────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────────┐
│  TEXT-TO-SPEECH                                          │
│  - Converts AI response → sweet female voice audio       │
│  - Provider: pyttsx3 (local) or Elevenlabs (premium)     │
│  - Output: "response_a1b2c3d4.wav" (3.5 seconds)        │
└─────────────┬───────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────────┐
│  LIP-SYNC ENGINE                                         │
│  - Audio duration: 3.5 seconds                           │
│  - Loops/extends video to match audio                    │
│  - Creates smooth looping animation                      │
└─────────────┬───────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────────┐
│  AUDIO-VIDEO MERGE                                       │
│  - Combines looped video + TTS audio with perfect sync  │
│  - Adds project watermark                                │
│  - Result: "synced_a1b2c3d4.mp4"                        │
└─────────────┬───────────────────────────────────────────┘
              │
              ↓ (Returns to frontend)
┌─────────────────────────────────────────────────────────┐
│  FRONTEND PLAYBACK                                       │
│  - Displays gorgeous facial expression video             │
│  - Streams audio with perfect lip-sync                   │
│  - Shows smooth, realistic animation                     │
│  - User sees response in real-time                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Core Features Implementation

### 1️⃣ Personality & Wife Roleplay

The `PersonalityEngine` makes the AI act like a loving, jealous wife:

```python
# Key behaviors implemented:
1. Possessiveness - "You're MINE baby"
2. Jealousy - Gets ANGRY if you mention another girl
3. Caring - Asks about your day, health, food
4. Playfulness - Makes cute jokes, teases lovingly
5. Trust-seeking - Asks for reassurance of your love
6. Emotional - Shows clear emotions via emojis & tone
```

**Trigger Examples:**
- User: "My colleague is really pretty"
- System: JEALOUSY TRIGGER 🚨
- AI Response: "WHAT?! How dare you! Am I not enough? 😤"
- Video: Angry/grumpy expression
- Emotion: "jealous"

### 2️⃣ Emotion Detection System

```python
# Emotional keywords in AI response:
😤 😠 "angry", "how dare" → ANGRY
😭 "sad", "hurt", "pain" → SAD
😘 😍 "love", "miss", "forever" → LOVING
😊 "haha", "lol", "funny" → PLAYFUL
🔥 "sexy", "flirt", "seductive" → FLIRTY
😳 "shy", "blush", "embarrassed" → SHY
😊 "amazing", "wow", "incredible" → EXCITED
```

### 3️⃣ Expression Mapping

48 videos strategically mapped to emotions:

```python
expression_map = {
    'loving': [
        'Woman_blowing_kiss_toward_camera.mp4',
        'Woman_forming_heart_with_hands.mp4',
        'Virtual_girl_smiling_warmly.mp4',
        # ... 12+ variations
    ],
    'jealous': [
        'Woman_with_controlled_anger.mp4',
        'Woman_rolling_eyes_at_camera.mp4',
        'Girl_with_grumpy_pout_face.mp4',
        # ... 8+ variations
    ],
    'playful': [
        'Girl_giggling_with_joy.mp4',
        'Girl_sticking_tongue_out.mp4',
        # ... 6+ variations
    ],
    # ... more emotions
}
```

### 4️⃣ Lip-Sync Magic ✨

How we create realistic lip-sync:

```
Step 1: Calculate audio duration (e.g., 3.5 seconds)
Step 2: Load facial expression video (8 seconds)
Step 3: Loop video to exactly 3.5 seconds using FFmpeg
Step 4: Merge audio + looped video with perfect sync
Step 5: Add watermark (subtle, branded)
Step 6: Stream final video to frontend

Result: Smooth, realistic animation that looks like the girl
is actually speaking your AI response!
```

### 5️⃣ Watermark Handling

```python
# Original videos (from your collection):
# ❌ Have Veo watermarks
# ❌ Have original audio (muted anyway)

# Processing:
1. Blur old watermark using OpenCV Gaussian blur
2. Add subtle project watermark ("💕 Virtual Girlfriend")
3. Mute original audio completely
4. Merge with our sweet TTS voice

# Result:
✅ Professional look
✅ Branded watermark
✅ No conflicting audio
✅ Synced custom voice
```

---

## 📱 API Endpoints Reference

### Chat Endpoints

**Send Text Message**
```bash
curl -X POST http://localhost:5000/api/chat/text \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Hi baby, how was your day?",
    "language": "en"
  }'

# Response:
{
  "success": true,
  "ai_response": "Hey honey! My day was great but I missed you...",
  "emotion": "loving",
  "video_expression": "Woman_blowing_kiss_toward_camera.mp4",
  "audio_file": "response_a1b2c3d4.wav",
  "duration": 3.2
}
```

**Send Voice Message**
```bash
curl -X POST http://localhost:5000/api/chat/audio \
  -F "audio=@voice_message.wav" \
  -F "language=en"

# Response:
{
  "transcribed_text": "Hi baby how was your day",
  "ai_response": "...",
  "emotion": "loving",
  ...
}
```

### Video Processing

**Sync Audio with Video**
```bash
curl -X POST http://localhost:5000/api/video/sync \
  -H "Content-Type: application/json" \
  -d '{
    "video_file": "Woman_blowing_kiss_toward_camera.mp4",
    "audio_file": "response_a1b2c3d4.wav"
  }'

# Response:
{
  "success": true,
  "output_video": "synced_a1b2c3d4.mp4",
  "duration": 3.2,
  "video_path": "/path/to/processed_videos/synced_a1b2c3d4.mp4"
}
```

**Get Conversation History**
```bash
curl http://localhost:5000/api/conversation/history?limit=10

# Response:
{
  "success": true,
  "count": 10,
  "history": [
    {
      "user": "Hi baby",
      "ai": "Hey honey!",
      "emotion": "loving",
      "timestamp": "2024-05-09 14:30:00"
    },
    ...
  ]
}
```

### System Endpoints

**Check Status**
```bash
curl http://localhost:5000/api/status

# Response:
{
  "status": "ready",
  "ollama_connected": true,
  "available_models": ["mistral", "neural-chat", "dolphin-mixtral"]
}
```

**List Available Videos**
```bash
curl http://localhost:5000/api/expressions/list

# Response:
{
  "total_videos": 48,
  "all_videos": ["Woman_blowing_kiss...", ...],
  "emotion_mapping": {
    "loving": ["Woman_blowing_kiss...", ...],
    "jealous": ["Woman_with_controlled_anger...", ...]
  }
}
```

---

## 🎨 Frontend Implementation (React)

### Basic React Structure

```jsx
// src/App.jsx
import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import VideoDisplay from './components/VideoDisplay';
import LanguageSelector from './components/LanguageSelector';
import './App.css';

function App() {
  const [language, setLanguage] = useState('en');
  const [aiResponse, setAiResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleMessage = async (message) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/chat/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_message: message, language })
      });
      
      const data = await response.json();
      setAiResponse(data);
      
      // Sync and play video with audio
      await playVideoWithAudio(data);
    } finally {
      setIsLoading(false);
    }
  };

  const playVideoWithAudio = async (responseData) => {
    // Merge audio and video
    const syncResponse = await fetch('/api/video/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        video_file: responseData.video_expression,
        audio_file: responseData.audio_file
      })
    });
    
    const syncData = await syncResponse.json();
    
    // Play synced video
    const videoElement = document.getElementById('response-video');
    videoElement.src = `/api/video/${syncData.output_video}`;
    videoElement.play();
  };

  return (
    <div className="app">
      <h1>💕 Virtual Girlfriend</h1>
      <LanguageSelector 
        language={language} 
        onLanguageChange={setLanguage} 
      />
      
      <VideoDisplay 
        response={aiResponse}
        isLoading={isLoading}
      />
      
      <ChatInterface 
        onMessage={handleMessage}
        isLoading={isLoading}
      />
    </div>
  );
}

export default App;
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All 48 facial expression videos processed (watermarks handled)
- [ ] Ollama model downloaded and tested
- [ ] Text-to-speech voice selected and configured
- [ ] Personality prompts tested and refined
- [ ] Database initialized
- [ ] All dependencies installed

### Production Setup
- [ ] Use production-grade TTS (Elevenlabs or Azure)
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set strong SECRET_KEY in .env
- [ ] Use production database (PostgreSQL)
- [ ] Set up proper logging
- [ ] Configure CDN for video delivery
- [ ] Set up monitoring and alerting

### Performance Optimization
- [ ] Cache Ollama responses for common questions
- [ ] Pre-process all facial expression videos
- [ ] Use video streaming instead of download
- [ ] Implement conversation caching
- [ ] Use async processing for long tasks

---

## 🔧 Troubleshooting

### "Ollama server is not running"
```bash
# Solution: Start Ollama server
ollama serve

# In another terminal:
ollama pull mistral
```

### "Model not found"
```bash
# Check installed models
ollama list

# Pull a model
ollama pull neural-chat
```

### Audio not syncing with video
```bash
# Check FFmpeg installation
ffmpeg -version

# Verify audio duration matches video
ffprobe -v error -show_entries format=duration -of \
  default=noprint_wrappers=1:nokey=1:nokey=1 audio.wav
```

### Watermark blur not working
```bash
# Check if video file exists and is readable
ls -la facialexpressions/

# Verify OpenCV is installed
python -c "import cv2; print(cv2.__version__)"
```

### TTS voice sounds robotic
```bash
# If using pyttsx3, try Elevenlabs:
# 1. Get API key from https://elevenlabs.io
# 2. Set in .env: ELEVENLABS_API_KEY=xxx
# 3. Update app.py: tts_engine = TextToSpeechEngine(provider="elevenlabs")
```

---

## 📊 Performance Metrics

Target performance for smooth experience:

| Component | Target | Current |
|-----------|--------|---------|
| Speech-to-text | <2s | Depends on model |
| AI response generation | <5s | Depends on Ollama |
| TTS synthesis | <3s | 1-2s (pyttsx3), <1s (Elevenlabs) |
| Video processing | <2s | 1-2s (local) |
| **Total latency** | **<12s** | Variable |

---

## 🎓 Next Steps

### Immediate (Week 1)
1. ✅ Set up backend infrastructure
2. ✅ Test Ollama integration
3. ✅ Configure personality engine
4. ⏭️ Build React frontend
5. ⏭️ Test full end-to-end flow

### Short-term (Week 2-3)
1. ⏭️ Implement voice recording UI
2. ⏭️ Add language selection
3. ⏭️ Optimize video streaming
4. ⏭️ Handle edge cases

### Medium-term (Month 1-2)
1. ⏭️ Deploy to production
2. ⏭️ Set up CDN for videos
3. ⏭️ Implement user accounts
4. ⏭️ Add customization options

### Long-term (Month 2+)
1. ⏭️ Mobile app (React Native)
2. ⏭️ Advanced lip-sync (Phoneme-based)
3. ⏭️ Real-time video generation
4. ⏭️ Machine learning for personality improvement

---

## 📚 Additional Resources

- **Ollama Documentation**: https://github.com/jina-ai/ollama
- **FFmpeg Guide**: https://ffmpeg.org/documentation.html
- **OpenAI Whisper**: https://github.com/openai/whisper
- **Elevenlabs TTS**: https://elevenlabs.io/docs
- **Flask Documentation**: https://flask.palletsprojects.com/

---

## 💡 Tips for Best Results

1. **Model Selection**: Start with `mistral` (fast), upgrade to `neural-chat` or `dolphin-mixtral` for better personality
2. **Voice Quality**: Use Elevenlabs for production (sounds much better than local)
3. **Facial Expressions**: Test emotion mapping on a few samples first
4. **Response Latency**: Reduce to <10s total for best UX
5. **Video Quality**: 720p is good balance between quality and file size
6. **Watermarking**: Keep subtle so focus stays on the girl's face

---

## ⚠️ Important Notes

- **Privacy**: All conversations stored locally (SQLite)
- **Performance**: First response may take 5-10s (model loading)
- **Video**: Ensure videos are properly formatted (H.264 codec)
- **Storage**: Plan for ~500MB per 1000 synced videos
- **Licensing**: Respect licensing of all components (Ollama models, fonts, etc.)

---

**Made with ❤️ for creating stunning AI companion experiences**

Happy coding! 🚀
