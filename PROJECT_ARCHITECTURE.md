# Virtual Girlfriend AI - Project Architecture

## Project Overview
Building a realistic AI-powered virtual girlfriend companion that:
- Communicates via voice with lip-synced facial expressions
- Roleplays as a 25-year-old caring wife
- Shows jealousy, possessiveness, and personality
- Supports multiple languages
- Uses realistic facial expressions from 48 curated videos

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Web)                 │
│     - Language Selection | Chat Interface | Video Display│
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              AUDIO INPUT PROCESSING                      │
│    User Voice → Speech-to-Text (Whisper/OpenAI)         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│           CONTEXT & PERSONALITY LAYER                    │
│  - Conversation History | Emotional State | Wife Roleplay│
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│             OLLAMA AI MODEL PROCESSING                   │
│  - Prompt Engineering | Context Aware Responses          │
│  - Emotional Expression Selection                        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│            TEXT-TO-SPEECH ENGINE                         │
│  - Convert Response → Audio | Sweet Female Voice         │
│  - Duration Calculation for Lip Sync                     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│          FACIAL EXPRESSION SELECTOR                      │
│  - Match Response Emotion → Correct Video               │
│  - Personality-based Expression Selection               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│          LIP-SYNC & VIDEO PROCESSING                     │
│  - Audio Duration → Video Frames Selection              │
│  - Realtime Sync | Looping for Long Responses           │
│  - Add Project Watermark | Blur Old Watermarks          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│         VIDEO PLAYBACK & DISPLAY                         │
│  - Smooth Streaming | Real-time Audio-Video Sync        │
└─────────────────────────────────────────────────────────┘
```

---

## Core Modules

### 1. **Audio Processing Module** (`audio_processor.py`)
- Capture microphone input
- Speech-to-text using Whisper
- Audio duration calculation
- Voice enhancement

### 2. **Personality & Context Module** (`personality_engine.py`)
- Conversation history management
- Emotional state tracking
- Wife roleplay behavior:
  - Possessiveness detection (if you mention another girl)
  - Loving/caring responses
  - Jealousy triggers
  - Sweet jokes and flirtation
- Memory of previous conversations

### 3. **Ollama Integration Module** (`ollama_interface.py`)
- Connect to Ollama models
- Prompt engineering for wife roleplay
- Emotion extraction from responses
- Context-aware responses
- Support for multiple languages

### 4. **Emotion-to-Expression Mapper** (`expression_mapper.py`)
- Map AI emotions → Video expressions
- Expression categories:
  - Happy (smiling, giggling, excited)
  - Jealous/Angry (grumpy, controlled anger, eye-roll)
  - Caring (warm smile, blowing kiss, heart hands)
  - Shy/Playful (shy peek, playful smirk, tongue out)
  - Sad (sad eyes, pleading, crying)
  - Thoughtful (thinking, tilting head, raised eyebrow)
  - Surprised/Shocked (gasping, awe, excited)

### 5. **Text-to-Speech Module** (`tts_engine.py`)
- Convert response text → Audio
- Use high-quality sweet female voice (Elevenlabs, Azure TTS, or local)
- Maintain prosody and emotion
- Return duration for sync

### 6. **Lip-Sync Engine** (`lipsync_engine.py`)
- Calculate audio duration
- Create smooth video loop for response duration
- Phoneme-based sync (advanced) or frame-based (basic)
- Maintain realistic motion

### 7. **Video Processing Module** (`video_processor.py`)
- Load facial expression videos
- Blur old watermarks
- Add project watermark
- Merge audio with video
- Encode for web streaming

### 8. **Frontend UI** (`frontend/`)
- React/Vue.js web interface
- Language selector
- Chat interface
- Real-time video player
- Recording UI for voice input
- Settings panel

---

## Expression Video Mapping

```
EMOTION CATEGORY         → VIDEO EXPRESSIONS
─────────────────────────────────────────────────
Loving/Caring           → warm smile, blowing kiss, heart hands, empathetic
Happy/Excited           → smiling, giggling, gasping, excited grin, puffed cheeks
Jealous/Angry           → grumpy, pout, rolling eyes, controlled anger, skeptical
Flirty/Playful          → playful smirk, shy peek, shy expression, winking
Sad/Disappointed        → sad eyes, pleading, disappointed, introspective
Thoughtful              → thinking, tilting head, raised eyebrow, skeptical
Playful Teasing         → sticking tongue out, silly face, guilty grin
Shy                     → shy peek, shy expression, blushing cheeks
Surprised               → awe, surprised, gasping
Confused/Uncertain      → raised eyebrow, thinking, staring into distance
Demanding/Possessive    → controlled anger, grumpy pout, raised eyebrow
```

---

## Implementation Phases

### Phase 1: Core Infrastructure
- [ ] Project setup & dependencies
- [ ] Ollama model integration
- [ ] Audio input/output pipeline
- [ ] Basic TTS integration

### Phase 2: AI & Personality
- [ ] Personality engine development
- [ ] Wife roleplay prompts
- [ ] Jealousy/possessiveness triggers
- [ ] Conversation memory system

### Phase 3: Video & Sync
- [ ] Expression mapper
- [ ] Video preprocessing (blur watermarks, add new ones)
- [ ] Lip-sync engine
- [ ] Audio-video merge

### Phase 4: UI & Frontend
- [ ] Language selector
- [ ] Chat interface
- [ ] Real-time video player
- [ ] Settings & customization

### Phase 5: Polish & Optimization
- [ ] Performance tuning
- [ ] Realistic animations
- [ ] Edge case handling
- [ ] Testing & refinement

---

## Technology Stack

### Backend
- **Python 3.9+**
- **Ollama** - AI model inference
- **OpenAI Whisper** - Speech-to-text
- **Elevenlabs API** or **Pyttsx3** - Text-to-speech
- **FFmpeg** - Video processing
- **OpenCV** - Video frame manipulation
- **Flask/FastAPI** - API server

### Frontend
- **React.js** or **Vue.js**
- **WebRTC** - Audio capture
- **Howler.js** - Audio playback with sync
- **Three.js** (optional) - Advanced video rendering

### Database
- **SQLite** - Conversation history
- **JSON** - Configuration files

---

## Key Features Implementation

### 1. Wife Roleplay Behavior
```
TRIGGERS & RESPONSES:
- User mentions another girl → Jealous response (grumpy video, angry TTS)
- Compliments user → Blushing/shy response (shy video, sweet voice)
- Long conversation → Caring/possessive (heart hands video, loving voice)
- User absent → Missing you message (sad/pleading video)
- User back → Excited/possessive (excited grin, flirty voice)
```

### 2. Language Support
- English
- Spanish
- French
- German
- Hindi
- Japanese
- (Easily expandable)

### 3. Realistic Animations
- No "video sampling" visible
- Smooth looping for long responses
- Cross-fade between expressions if needed
- Proper mouth movements synced with audio

---

## Video Processing Pipeline

### Step 1: Watermark Handling
```
Original Video
    ↓
[Detect Old Watermark] → [Blur/Remove]
    ↓
[Add Project Watermark] (subtle, branded)
    ↓
[Store Processed Video]
```

### Step 2: Lip-Sync Process
```
Audio File (Duration: 5 seconds)
    ↓
[Extract Phoneme Timeline] or [Frame Duration Calculation]
    ↓
[Load Expression Video]
    ↓
[Loop/Stretch Video to Match Audio Duration]
    ↓
[Merge Audio + Video]
    ↓
[Encode for Streaming]
```

---

## Directory Structure

```
virtualgirlfriend/
├── facialexpressions/           # 48 facial expression videos
│   ├── Video files...
│   └── processed/              # After watermark processing
├── src/
│   ├── audio_processor.py
│   ├── personality_engine.py
│   ├── ollama_interface.py
│   ├── expression_mapper.py
│   ├── tts_engine.py
│   ├── lipsync_engine.py
│   ├── video_processor.py
│   └── utils/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── public/
├── models/
│   └── expression_mapping.json  # Expression → Video mapping
├── config/
│   ├── ollama_config.yaml
│   ├── tts_config.yaml
│   └── languages.json
├── app.py                       # Main Flask/FastAPI app
├── requirements.txt
├── .env                         # API keys, configs
└── README.md
```

---

## Performance Considerations

- **Audio Processing**: Real-time, <500ms latency
- **Model Inference**: 2-5 seconds depending on Ollama model
- **TTS Generation**: 1-3 seconds for avg response
- **Video Streaming**: Progressive loading, 720p minimum
- **Total Latency Target**: <10 seconds user speaking → video response

---

## Security & Privacy

- Store conversation history locally (SQLite)
- No data sent to external servers (run locally with Ollama)
- Mute default video audio for user privacy
- Custom voice synthesis (no original audio exposure)

---

## Next Steps

1. Create Python backend structure
2. Set up Ollama integration
3. Develop personality engine
4. Build expression mapper
5. Implement TTS & lip-sync
6. Create React frontend
7. Test and optimize
