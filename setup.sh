#!/bin/bash

# Virtual Girlfriend AI - Setup Script
# This script sets up the entire project

echo "================================================"
echo "  🎬 Virtual Girlfriend AI - Setup Script"
echo "================================================"

# Check Python version
echo -e "\n1️⃣  Checking Python version..."
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+')
echo "   Python version: $python_version"

if (( $(echo "$python_version < 3.9" | bc -l) )); then
    echo "   ❌ Python 3.9+ required!"
    exit 1
fi

# Create directories
echo -e "\n2️⃣  Creating directories..."
mkdir -p src
mkdir -p config
mkdir -p frontend
mkdir -p audio_input
mkdir -p audio_output
mkdir -p processed_videos
echo "   ✓ Directories created"

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo -e "\n❌ requirements.txt not found!"
    echo "   Please create requirements.txt first"
    exit 1
fi

# Install Python dependencies
echo -e "\n3️⃣  Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "   ✓ Dependencies installed"
else
    echo "   ❌ Failed to install dependencies"
    exit 1
fi

# Check for FFmpeg
echo -e "\n4️⃣  Checking for FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "   ❌ FFmpeg not found!"
    echo "   Install with:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "      brew install ffmpeg"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "      sudo apt-get install ffmpeg"
    else
        echo "      Download from https://ffmpeg.org/download.html"
    fi
    exit 1
else
    ffmpeg_version=$(ffmpeg -version 2>/dev/null | head -n 1)
    echo "   ✓ $ffmpeg_version"
fi

# Check for Ollama
echo -e "\n5️⃣  Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "   ✓ Ollama found"
else
    echo "   ⚠️  Ollama not found!"
    echo "   Download from https://ollama.ai"
fi

# Setup .env
echo -e "\n6️⃣  Setting up .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   ✓ Created .env from template (edit with your values)"
else
    echo "   ✓ .env already exists"
fi

# Initialize database
echo -e "\n7️⃣  Initializing database..."
python << 'EOF'
from src.personality_engine import ConversationMemory
db = ConversationMemory()
print("   ✓ Database initialized")
EOF

# Summary
echo -e "\n================================================"
echo "  ✅ Setup Complete!"
echo "================================================"
echo -e "\nNext steps:"
echo "1. Edit .env with your configuration"
echo "2. Start Ollama server:"
echo "   ollama serve"
echo "3. Pull a model (in another terminal):"
echo "   ollama pull mistral"
echo "4. Run example workflow:"
echo "   python example_workflow.py full"
echo "5. Start the Flask app:"
echo "   python app.py"
echo "6. Open http://localhost:5000 in your browser"
echo ""
