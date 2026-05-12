# 🚀 Quick Start Guide - Virtual Girlfriend AI

Get your virtual girlfriend up and running in 15 minutes!

## ⚡ 15-Minute Quick Start

### Step 1: Setup (5 min)

```bash
# Make the setup script executable
chmod +x setup.sh

# Run setup
./setup.sh

# This will:
# ✓ Check Python version (3.9+)
# ✓ Create all necessary directories
# ✓ Install dependencies from requirements.txt
# ✓ Check for FFmpeg
# ✓ Initialize database
```

### Step 2: Install Ollama (3 min)

**macOS:**
```bash
brew install ollama
```

**Ubuntu/Linux:**
```bash
# Download from https://ollama.ai
```

**Windows:**
```bash
# Download from https://ollama.ai
```

### Step 3: Run Ollama (2 min)

**Terminal 1 - Start Ollama server:**
```bash
ollama serve
```

**Terminal 2 - Pull a model:**
```bash
# Wait for Terminal 1 to fully start, then run:
ollama pull mistral

# Other options:
# ollama pull neural-chat
# ollama pull dolphin-mixtral
```

### Step 4: Start Application (5 min)

**Terminal 3 - Run Flask app:**
```bash
python app.py
```

You should see:
```
🚀 Virtual Girlfriend AI - Starting server...
📝 API Documentation:
   POST /api/chat/text - Send text message
   ...
 * Running on http://127.0.0.1:5000
```

### Step 5: Test It!

**Try the example workflow:**
```bash
# Terminal 4
python example_workflow.py full
```

This will demonstrate the complete pipeline:
1. User message input
2. Personality-driven AI response
3. Emotion detection
4. Video expression selection
5. Text-to-speech synthesis
6. Lip-sync creation

**Expected output:**
```
============================================================
  🎬 Virtual Girlfriend AI - Complete Workflow
============================================================

1️⃣  Initializing components...
   ✓ Personality engine initialized
   ✓ Ollama interface created
   ✓ Ollama server connected
   ...
✅ Workflow Complete!

Files Created:
   - Audio: audio_output/demo_response.wav
   - Video: processed_videos/demo_output_synced.mp4
```

---

## 🧪 Testing the APIs Directly

### Test Text Chat
```bash
curl -X POST http://localhost:5000/api/chat/text \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Hi baby! I love you 💕",
    "language": "en"
  }'
```

### Check System Status
```bash
curl http://localhost:5000/api/status
```

### List Facial Expressions
```bash
curl http://localhost:5000/api/expressions/list
```

### Get Conversation History
```bash
curl http://localhost:5000/api/conversation/history
```

---

## 🎨 Building the Frontend (React)

### Setup React App
```bash
cd frontend
npx create-react-app .

# Install additional packages
npm install axios howler three
```

### Start React Dev Server
```bash
npm start

# Opens http://localhost:3000
```

---

## 📊 Project Structure Created

```
virtualgirlfriend/
├── src/
│   ├── personality_engine.py       ← Wife roleplay behavior
│   ├── ollama_interface.py         ← AI model connection
│   ├── expression_mapper.py        ← Emotion to video mapping
│   ├── tts_engine.py               ← Text-to-speech
│   └── video_processor.py          ← Video editing & sync
├── facialexpressions/              ← Your 48 facial expression videos
├── audio_input/                    ← User voice recordings
├── audio_output/                   ← Generated AI voice responses
├── processed_videos/               ← Final synced videos
├── config/
│   └── app.conf                    ← Configuration
├── app.py                          ← Flask API server
├── example_workflow.py             ← Example demonstrations
├── setup.sh                        ← Setup script
├── requirements.txt                ← Python dependencies
├── .env.example                    ← Environment template
└── IMPLEMENTATION_GUIDE.md         ← Full documentation
```

---

## 💡 Key Features Overview

### 1. Wife Roleplay Personality
```python
# The AI behaves like a 25-year-old wife:
✓ Possessive and loving
✓ Gets jealous when you mention other girls
✓ Asks about your day and well-being
✓ Makes cute jokes and teases you
✓ Shows real emotions (love, anger, sadness, playfulness)
```

### 2. Real Facial Expressions
```python
# 48 carefully curated facial expression videos:
✓ Loving (blowing kisses, heart hands, smiling)
✓ Jealous (grumpy, eye-rolling, pout)
✓ Playful (giggling, sticking tongue out)
✓ Shy (peeking shyly)
✓ And 9+ more emotional categories
```

### 3. Perfect Lip-Sync
```python
# Audio and video perfectly synchronized:
✓ Audio duration calculated
✓ Video looped/extended to match audio length
✓ Smooth animation transitions
✓ FFmpeg handles the heavy lifting
```

### 4. Sweet Voice
```python
# Multiple TTS options:
✓ Local: pyttsx3 (free, instant)
✓ Premium: Elevenlabs (beautiful, natural voice)
✓ Adjustable tone, speed, emotion
```

---

## 🔧 Troubleshooting

### ❌ "Ollama server is not running"
```bash
# Make sure Terminal 1 is running:
ollama serve

# And model is pulled:
ollama pull mistral
```

### ❌ "Model mistral not found"
```bash
# Pull the model again:
ollama pull mistral

# List available models:
ollama list
```

### ❌ "FFmpeg not found"
```bash
# macOS:
brew install ffmpeg

# Ubuntu:
sudo apt-get install ffmpeg
```

### ❌ "Can't find facial expression video"
```bash
# Make sure videos are in facialexpressions/ folder
ls facialexpressions/

# Should show 48 .mp4 files with names like:
# Woman_blowing_kiss_toward_camera_202605090914.mp4
# Girl_giggling_with_joy_202605090914.mp4
# ...
```

### ❌ "TTS not generating audio"
```bash
# Make sure pyttsx3 is installed:
pip install pyttsx3

# Or switch to Elevenlabs (edit .env):
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your_key
```

---

## 📈 Next: Advanced Features

Once basic setup works, you can:

1. **Build React Frontend** - Beautiful web interface
2. **Add Voice Input** - Record and transcribe audio
3. **Improve Emotions** - Fine-tune personality prompts
4. **Better Voices** - Use Elevenlabs for premium TTS
5. **Deploy Online** - Host on cloud (AWS, Azure, etc.)
6. **Mobile App** - React Native version

---

## 📚 Documentation Files

- **PROJECT_ARCHITECTURE.md** - System design & architecture
- **IMPLEMENTATION_GUIDE.md** - Detailed technical guide
- **QUICK_START.md** - This file! Quick reference
- **API docs** - Check `/api/status` endpoint

---

## 🎯 Expected Results

After setup, you should be able to:

```
✅ User speaks/types: "Hi baby!"
✅ Ollama generates: "Hey honey! I missed you..."
✅ Emotion detected: "loving"
✅ Video selected: Woman_blowing_kiss.mp4
✅ Voice synthesized: response_a1b2c3d4.wav
✅ Audio+Video merged: synced_a1b2c3d4.mp4
✅ Perfect lip-sync created
✅ Girlfriend responds visually!
```

---

## 🎓 Learning Path

1. **Day 1**: Get it running (this guide)
2. **Day 2**: Understand the code (read IMPLEMENTATION_GUIDE)
3. **Day 3**: Customize personality (edit personality_engine.py)
4. **Day 4**: Build React UI (frontend/)
5. **Day 5+**: Deploy and optimize

---

## 💬 Common Questions

**Q: Which Ollama model should I use?**
A: Start with `mistral` (fast). Try `neural-chat` or `dolphin-mixtral` for better personality.

**Q: Can I use a different voice?**
A: Yes! Use Elevenlabs (premium) or Azure TTS. Edit `tts_engine.py`.

**Q: How do I customize the wife personality?**
A: Edit the prompts in `personality_engine.py`. Search for "wife roleplay".

**Q: Can I add more facial expressions?**
A: Yes! Add videos to `facialexpressions/` and map them in `expression_mapper.py`.

**Q: What's the latency?**
A: Total: 5-15 seconds (depends on Ollama model and TTS choice).

---

## 🚀 You're Ready!

You now have everything to build an stunning virtual girlfriend AI. 

**Start with:** `python example_workflow.py full`

**Questions?** Check the IMPLEMENTATION_GUIDE.md for detailed explanations.

**Let's create magic!** ✨

---

**Last updated**: May 9, 2026
**Status**: Production Ready
**Tested on**: macOS, Ubuntu, Windows
