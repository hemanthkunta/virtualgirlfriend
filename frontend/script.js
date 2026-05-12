const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const chatHistory = document.getElementById('chat-history');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const aiVideo = document.getElementById('ai-video');
const videoOverlay = document.getElementById('video-overlay');
const emotionBadge = document.getElementById('current-emotion');

// State
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];

// Initialize
async function init() {
    try {
        const response = await fetch(`${API_BASE_URL}/status`);
        const data = await response.json();
        
        if (data.status === 'ready') {
            document.querySelector('.status-indicator').classList.add('online');
            
            // Set an idle video if available
            aiVideo.src = `${API_BASE_URL}/expression/Virtual_girl_smiling_warmly_202605090914.mp4`; 
        }
    } catch (error) {
        console.error('Error connecting to backend:', error);
        addMessage('System', 'Could not connect to the backend server. Make sure it is running on port 5000.', 'ai');
    }
}

// Add message to chat UI
function addMessage(sender, text, type) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;
    
    msgDiv.appendChild(bubble);
    chatHistory.appendChild(msgDiv);
    
    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Send Text Message
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;
    
    // Clear input
    messageInput.value = '';
    
    // Add user message to UI
    addMessage('You', text, 'user');
    
    // Show loading
    videoOverlay.classList.remove('hidden');
    videoOverlay.querySelector('p').textContent = 'Thinking...';
    emotionBadge.textContent = 'Thinking...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat/text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_message: text, language: 'en' })
        });
        
        const data = await response.json();
        
        if (data.success) {
            handleAIResponse(data);
        } else {
            throw new Error(data.error || 'Failed to get response');
        }
    } catch (error) {
        console.error(error);
        videoOverlay.classList.add('hidden');
        addMessage('System', 'Error: ' + error.message, 'ai');
        emotionBadge.textContent = 'Error';
    }
}

// Handle the response from the backend
async function handleAIResponse(data) {
    // 1. Add AI text to chat
    addMessage('AI', data.ai_response, 'ai');
    
    // 2. Update Emotion Badge
    emotionBadge.textContent = data.emotion || 'Neutral';
    
    // 3. Trigger Video Sync (Now handled by Fal API in backend)
    videoOverlay.querySelector('p').textContent = 'Generating Video...';
    
    try {
        const syncResponse = await fetch(`${API_BASE_URL}/video/sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                video_file: data.video_expression,
                audio_file: data.audio_file
            })
        });
        
        const syncData = await syncResponse.json();
        
        if (syncData.success) {
            // Play the synced video
            aiVideo.src = `${API_BASE_URL}/video/${syncData.output_video}`;
            aiVideo.loop = false; // Only play once, then back to idle
            aiVideo.play();
            
            // Hide overlay
            videoOverlay.classList.add('hidden');
            
            // Listen for when video ends
            aiVideo.onended = () => {
                emotionBadge.textContent = 'Idle';
                // Ideally load idle video back
            };
        } else {
            throw new Error(syncData.error);
        }
    } catch (error) {
        console.error('Video Sync Error:', error);
        videoOverlay.classList.add('hidden');
        addMessage('System', 'Failed to generate lip-sync video.', 'ai');
        
        // Fallback: Just play the audio
        const audio = new Audio(`${API_BASE_URL}/audio/${data.audio_file}`);
        audio.play();
    }
}

// Voice Recording Logic
async function setupVoiceRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunks.push(e.data);
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            audioChunks = []; // reset
            
            await sendAudioMessage(audioBlob);
        };
    } catch (err) {
        console.error("Microphone access denied:", err);
        alert("Microphone access is required for voice chat.");
    }
}

async function sendAudioMessage(audioBlob) {
    videoOverlay.classList.remove('hidden');
    videoOverlay.querySelector('p').textContent = 'Transcribing...';
    
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('language', 'en');
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat/audio`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show what the user said
            addMessage('You', data.transcribed_text, 'user');
            // Handle the response
            handleAIResponse(data);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error(error);
        videoOverlay.classList.add('hidden');
        addMessage('System', 'Voice Error: ' + error.message, 'ai');
    }
}

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

voiceBtn.addEventListener('mousedown', () => {
    if (!mediaRecorder) {
        setupVoiceRecording().then(() => {
            startRecording();
        });
    } else {
        startRecording();
    }
});

voiceBtn.addEventListener('mouseup', stopRecording);
voiceBtn.addEventListener('mouseleave', () => {
    if (isRecording) stopRecording();
});

function startRecording() {
    if (mediaRecorder && mediaRecorder.state === 'inactive') {
        audioChunks = [];
        mediaRecorder.start();
        isRecording = true;
        voiceBtn.classList.add('recording');
        messageInput.placeholder = 'Listening...';
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        isRecording = false;
        voiceBtn.classList.remove('recording');
        messageInput.placeholder = 'Say something nice...';
    }
}

// Start
init();
