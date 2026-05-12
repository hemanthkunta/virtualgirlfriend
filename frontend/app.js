const API_BASE = 'http://localhost:5000/api';

// DOM Elements
const statusIndicator = document.getElementById('connection-status');
const statusText = document.getElementById('system-status-text');
const chatHistory = document.getElementById('chat-history');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const recordBtn = document.getElementById('record-btn');
const typingIndicator = document.getElementById('typing-indicator');
const mainVideo = document.getElementById('main-video');
const secondaryVideo = document.getElementById('secondary-video');
const emotionDisplay = document.getElementById('emotion-display');
const responseAudio = document.getElementById('response-audio');

const settingsBtn = document.getElementById('settings-btn');
const settingsModal = document.getElementById('settings-modal');
const closeSettingsBtn = document.getElementById('close-settings-btn');
const languageSelect = document.getElementById('language-select');
const clearChatBtn = document.getElementById('clear-chat-btn');
const handsFreeBtn = document.getElementById('hands-free-btn');

// State
let isRecording = false;
let mediaRecorder;
let audioChunks = [];
let isVideoPlaying = false;
let videoQueue = [];
let currentLanguage = 'en';
let isBackendReady = false;

// Hands-Free State
let handsFreeMode = false;
let speechRecognition = null;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    speechRecognition = new SpeechRec();
    speechRecognition.continuous = false;
    speechRecognition.interimResults = false;
    
    speechRecognition.onstart = () => {
        recordBtn.classList.add('recording');
        mainVideo.src = `${API_BASE}/expression/Girl_tilting_head_thoughtfully_202605090914.mp4`;
        mainVideo.loop = true;
        mainVideo.muted = true;
        mainVideo.play().catch(e => console.log(e));
    };
    
    speechRecognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        if (text.trim()) {
            messageInput.value = text;
            handleSendText();
        }
    };
    
    speechRecognition.onend = () => {
        recordBtn.classList.remove('recording');
    };
    
    speechRecognition.onerror = (event) => {
        console.log("Speech recognition error:", event.error);
        if (handsFreeMode && !isVideoPlaying && event.error !== 'aborted') {
            setTimeout(() => { if (handsFreeMode && !isVideoPlaying) speechRecognition.start(); }, 1000);
        }
    };
}

// Initialize
async function init() {
    checkBackendStatus();
    loadConversationHistory();
    
    // Set an idle video so the model is visible immediately
    mainVideo.src = `${API_BASE}/expression/Virtual_girl_smiling_warmly_202605090914.mp4`;
    mainVideo.muted = true; // Required for browser autoplay without user interaction
    mainVideo.play().catch(e => console.log("Autoplay prevented:", e));
    
    // Event Listeners
    sendBtn.addEventListener('click', handleSendText);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendText();
    });
    
    // Hands Free Toggle
    if (handsFreeBtn) {
        handsFreeBtn.addEventListener('click', toggleHandsFree);
    }
    
    // Audio recording events
    recordBtn.addEventListener('mousedown', startRecording);
    recordBtn.addEventListener('mouseup', stopRecording);
    recordBtn.addEventListener('mouseleave', stopRecording);
    
    // Touch support for mobile recording
    recordBtn.addEventListener('touchstart', (e) => { e.preventDefault(); startRecording(); });
    recordBtn.addEventListener('touchend', (e) => { e.preventDefault(); stopRecording(); });
    
    // Settings events
    settingsBtn.addEventListener('click', () => settingsModal.classList.remove('hidden'));
    closeSettingsBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));
    languageSelect.addEventListener('change', (e) => setLanguage(e.target.value));
    
    clearChatBtn.addEventListener('click', clearConversation);
}

// Hands Free Functions
function toggleHandsFree() {
    if (!speechRecognition) {
        appendSystemMessage("Hands-free mode is not supported by your browser (use Chrome/Safari).");
        return;
    }
    
    handsFreeMode = !handsFreeMode;
    if (handsFreeMode) {
        handsFreeBtn.style.color = 'var(--status-online)';
        appendSystemMessage("Hands-Free Mode Enabled! Say Hello.");
        
        // Start listening
        if (!isVideoPlaying) {
            speechRecognition.start();
        }
        
        // Generate an initial greeting from the AI to start the flow
        triggerGreeting();
    } else {
        handsFreeBtn.style.color = '';
        appendSystemMessage("Hands-Free Mode Disabled.");
        speechRecognition.stop();
    }
}

async function triggerGreeting() {
    // Send a hidden prompt to the backend
    try {
        const response = await fetch(`${API_BASE}/chat/text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_message: "Hi! Let's start the conversation. Please greet me warmly in one short sentence and wait for my reply.",
                language: currentLanguage,
                persona: document.getElementById('persona-select').value
            })
        });
        const data = await response.json();
        if (data.success) {
            handleAIResponse(data);
        }
    } catch (e) {
        console.error("Failed to trigger greeting", e);
    }
}

// API Calls
async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        if (data.status === 'ready') {
            statusIndicator.className = 'status-indicator online';
            statusText.textContent = 'Online & Ready';
            isBackendReady = true;
            if (data.user_session && data.user_session.language) {
                currentLanguage = data.user_session.language;
                languageSelect.value = currentLanguage;
            }
        } else {
            statusIndicator.className = 'status-indicator busy';
            statusText.textContent = 'Ollama Offline';
            isBackendReady = false;
            appendSystemMessage("Warning: AI Model is offline. Start Ollama serve.");
        }
    } catch (error) {
        console.error("Backend connection failed:", error);
        statusIndicator.className = 'status-indicator';
        statusText.textContent = 'Disconnected';
        isBackendReady = false;
    }
}

async function setLanguage(lang) {
    try {
        await fetch(`${API_BASE}/set-language`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ language: lang })
        });
        currentLanguage = lang;
        appendSystemMessage(`Language changed to ${languageSelect.options[languageSelect.selectedIndex].text}`);
    } catch (error) {
        console.error("Failed to set language", error);
    }
}

async function loadConversationHistory() {
    try {
        const response = await fetch(`${API_BASE}/conversation/history?limit=20`);
        const data = await response.json();
        
        if (data.success && data.history.length > 0) {
            // Clear current chat except the first system message
            chatHistory.innerHTML = '<div class="message system-message"><p>Connected. Say hi! 💕</p></div>';
            
            // The history comes back from newest to oldest in array, or oldest to newest depending on backend implementation.
            // Assuming the backend returns list with oldest first (standard). If reversed, we'd reverse it.
            data.history.forEach(msg => {
                if(msg.user) appendMessage(msg.user, 'user-message', false);
                if(msg.ai) appendMessage(msg.ai, 'ai-message', false);
            });
            scrollToBottom();
        }
    } catch (error) {
        console.error("Failed to load history", error);
    }
}

async function clearConversation() {
    try {
        await fetch(`${API_BASE}/conversation/clear`, { method: 'POST' });
        chatHistory.innerHTML = '<div class="message system-message"><p>Conversation cleared.</p></div>';
        appendSystemMessage("Started a new conversation.");
    } catch (error) {
        console.error("Failed to clear", error);
    }
}

// Chat Handlers
async function handleSendText() {
    if (!isBackendReady) {
        appendSystemMessage("Backend is not ready. Please wait.");
        return;
    }
    
    const text = messageInput.value.trim();
    if (!text) return;
    
    // Clear input
    messageInput.value = '';
    
    // Show user message
    appendMessage(text, 'user-message');
    
    // Show typing indicator
    showTyping();
    
    // Set video to thinking expression
    mainVideo.src = `${API_BASE}/expression/Woman_thinking_in_bedroom_202605090914.mp4`;
    mainVideo.loop = true;
    mainVideo.muted = true;
    mainVideo.play().catch(e => console.log(e));
    
    try {
        const response = await fetch(`${API_BASE}/chat/text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_message: text,
                language: currentLanguage,
                persona: document.getElementById('persona-select').value
            })
        });
        
        const data = await response.json();
        hideTyping();
        
        if (data.success) {
            handleAIResponse(data);
        } else {
            appendSystemMessage("Error: " + (data.error || "Failed to get response"));
        }
    } catch (error) {
        hideTyping();
        appendSystemMessage("Network error occurred.");
        console.error(error);
    }
}

async function handleAIResponse(data) {
    // Append text message
    appendMessage(data.ai_response, 'ai-message');
    
    // Play video segments sequentially
    if (data.segments && data.segments.length > 0) {
        await playSegmentsSequentially(data.segments);
    } else if (data.video_expression && data.audio_file) {
        // Fallback for older API format
        await playSingleSegment(data.video_expression, data.audio_file, data.emotion);
    }
}

async function playSegmentsSequentially(segments) {
    for (let i = 0; i < segments.length; i++) {
        const seg = segments[i];
        await playSingleSegment(seg.video_expression, seg.audio_file, seg.emotion, `Syncing part ${i + 1} of ${segments.length}...`);
    }
    
    // After all segments finish, loop the last video without audio to act as idle
    mainVideo.loop = true;
}

async function playSingleSegment(videoFile, audioFile, emotion, syncMessage = "Syncing video...") {
    // Show emotion overlay briefly
    if (emotion) {
        emotionDisplay.textContent = emotion;
        emotionDisplay.classList.add('visible');
        setTimeout(() => emotionDisplay.classList.remove('visible'), 3000);
    }
    
    try {
        appendSystemMessage(syncMessage);
        const syncResponse = await fetch(`${API_BASE}/video/sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                video_file: videoFile,
                audio_file: audioFile
            })
        });
        
        const syncData = await syncResponse.json();
        
        // Remove sync message
        chatHistory.removeChild(chatHistory.lastChild);

        if (syncData.success && syncData.output_video) {
            await playVideoAndWait(syncData.output_video);
        }
    } catch (error) {
        console.error("Sync failed:", error);
    }
}

function playVideoAndWait(videoFilename) {
    return new Promise((resolve) => {
        const videoUrl = `${API_BASE}/video/${videoFilename}`;
        mainVideo.src = videoUrl;
        mainVideo.loop = false; // We want to know when it ends
        mainVideo.muted = false; // Unmute so we can hear her speak
        
        mainVideo.oncanplay = () => {
            isVideoPlaying = true;
            if (speechRecognition && handsFreeMode) speechRecognition.abort(); // Pause listening while speaking
            
            mainVideo.play();
            mainVideo.classList.add('active-video');
            mainVideo.classList.remove('hidden-video');
        };
        
        mainVideo.onended = () => {
            isVideoPlaying = false;
            // Return to idle animation
            mainVideo.src = `${API_BASE}/expression/Virtual_girl_smiling_warmly_202605090914.mp4`;
            mainVideo.loop = true;
            mainVideo.muted = true; // Mute idle video
            mainVideo.play().catch(e => console.log(e));
            
            if (handsFreeMode && speechRecognition) {
                setTimeout(() => { speechRecognition.start(); }, 500); // Resume listening
            }
            resolve();
        };
        
        mainVideo.onerror = () => {
            resolve(); // Skip on error
        };
    });
}

// Audio Recording
async function startRecording() {
    if (!isBackendReady || isRecording) return;
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunks.push(e.data);
        };
        
        mediaRecorder.onstop = sendAudioToServer;
        
        mediaRecorder.start();
        isRecording = true;
        recordBtn.classList.add('recording');
        
        // Change expression to show she is listening
        mainVideo.src = `${API_BASE}/expression/Girl_tilting_head_thoughtfully_202605090914.mp4`;
        mainVideo.loop = true;
        mainVideo.muted = true;
        mainVideo.play().catch(e => console.log(e));
        
    } catch (err) {
        console.error("Microphone access denied or error:", err);
        appendSystemMessage("Could not access microphone.");
    }
}

function stopRecording() {
    if (!isRecording || !mediaRecorder) return;
    
    mediaRecorder.stop();
    isRecording = false;
    recordBtn.classList.remove('recording');
    
    // Stop all tracks to release mic
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
}

async function sendAudioToServer() {
    if (audioChunks.length === 0) return;
    
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    formData.append('language', currentLanguage);
    formData.append('persona', document.getElementById('persona-select').value);
    
    showTyping();
    appendSystemMessage("Processing audio...");
    
    // Set video to thinking expression
    mainVideo.src = `${API_BASE}/expression/Woman_thinking_in_bedroom_202605090914.mp4`;
    mainVideo.loop = true;
    mainVideo.muted = true;
    mainVideo.play().catch(e => console.log(e));
    
    try {
        const response = await fetch(`${API_BASE}/chat/audio`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        hideTyping();
        
        if (data.success) {
            // Remove the "Processing audio..." message
            chatHistory.removeChild(chatHistory.lastChild);
            
            // Show transcribed text as user message
            if (data.transcribed_text) {
                appendMessage(`🎤 ${data.transcribed_text}`, 'user-message');
            }
            
            handleAIResponse(data);
        } else {
            appendSystemMessage("Audio processing failed: " + (data.error || "Unknown error"));
        }
    } catch (error) {
        hideTyping();
        appendSystemMessage("Failed to upload audio.");
        console.error(error);
    }
}

// UI Helpers
function appendMessage(text, className, smoothScroll = true) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${className}`;
    msgDiv.textContent = text;
    chatHistory.appendChild(msgDiv);
    
    if (smoothScroll) {
        scrollToBottom();
    }
}

function appendSystemMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message system-message';
    msgDiv.innerHTML = `<p>${text}</p>`;
    chatHistory.appendChild(msgDiv);
    scrollToBottom();
}

function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function showTyping() {
    typingIndicator.classList.remove('hidden');
    scrollToBottom();
}

function hideTyping() {
    typingIndicator.classList.add('hidden');
}

// Media Playback Logic
// Replaced by playVideoAndWait and playSegmentsSequentially

// Start
document.addEventListener('DOMContentLoaded', init);
