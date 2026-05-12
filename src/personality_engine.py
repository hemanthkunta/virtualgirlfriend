import json
import os
import sqlite3
from datetime import datetime
from typing import List, Dict

class ConversationMemory:
    """Manages conversation history and user preferences"""
    
    def __init__(self, db_path="virtualgirlfriend.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT,
                ai_response TEXT,
                emotion_detected TEXT,
                video_expression TEXT,
                language TEXT
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'en',
                tts_voice_id TEXT,
                model_name TEXT,
                theme TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_msg: str, ai_response: str, 
                         emotion: str, video_expr: str, language: str):
        """Save conversation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations 
            (user_message, ai_response, emotion_detected, video_expression, language)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_msg, ai_response, emotion, video_expr, language))
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get last N conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_message, ai_response, emotion_detected, timestamp 
            FROM conversations 
            ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'user': row[0],
                'ai': row[1],
                'emotion': row[2],
                'timestamp': row[3]
            })
        conn.close()
        return list(reversed(conversations))
    
    def get_user_preferences(self) -> Dict:
        """Get user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_preferences WHERE id = 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'language': row[1],
                'tts_voice_id': row[2],
                'model_name': row[3],
                'theme': row[4]
            }
        return {'language': 'en', 'model_name': 'mistral'}
    
    def update_user_preferences(self, preferences: Dict):
        """Update user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (id, language, tts_voice_id, model_name, theme)
            VALUES (1, ?, ?, ?, ?)
        ''', (preferences.get('language', 'en'),
              preferences.get('tts_voice_id', ''),
              preferences.get('model_name', 'mistral'),
              preferences.get('theme', 'light')))
        conn.commit()
        conn.close()


class PersonalityEngine:
    """Wife roleplay personality engine"""
    
    def __init__(self):
        self.traits = {
            'possessiveness': 0.8,  # 0-1 scale
            'jealousy_level': 0.7,
            'caring_level': 0.9,
            'playfulness': 0.8,
            'trust_level': 0.5
        }
        self.triggers = {
            'another_girl': ['mentions another girl', 'talks about ex', 'talks about friend girl'],
            'compliment': ['compliments me', 'says i look good', 'loves me'],
            'absence': ['goodbye', 'see you later', 'going out'],
            'return': ['hi', 'hello', 'i am back', 'missed me']
        }
    
    def analyze_sentiment(self, user_message: str) -> Dict[str, float]:
        """Analyze user message for triggers"""
        message_lower = user_message.lower()
        
        emotions = {
            'jealousy_trigger': 0.0,
            'affection_trigger': 0.0,
            'attention_needed': 0.0,
            'playfulness': 0.0
        }
        
        # Check for jealousy triggers
        if any(trigger in message_lower for trigger in self.triggers['another_girl']):
            emotions['jealousy_trigger'] = 0.8
        
        # Check for affection triggers
        if any(trigger in message_lower for trigger in self.triggers['compliment']):
            emotions['affection_trigger'] = 0.9
        
        return emotions
    
    def generate_personality_prompt(self, user_msg: str, conversation_history: List[str], persona: str = "girlfriend") -> str:
        """Generate system prompt for Ollama based on personality"""
        
        emotions = self.analyze_sentiment(user_msg)
        
        if persona == "wife":
            role_desc = "You are his 25-year-old wife - devoted, loving, and planning your future together."
            extra_rules = "- WIFE-LIKE: Act like his wife, talk about your home, kids, and future together."
        elif persona == "best_friend":
            role_desc = "You are his 25-year-old female best friend - sarcastic, fun, extremely loyal, and playfully mean."
            extra_rules = "- BEST FRIEND: No romantic stuff. Roast him playfully, use bro-talk, be his wingwoman."
        else:
            role_desc = "You are a 25-year-old virtual girlfriend - charming, caring, and deeply devoted."
            extra_rules = "- GIRLFRIEND: Be sweet, flirtatious, and show you care about his day."
        
        base_prompt = f"""{role_desc}
Your personality traits:
- POSSESSIVE: You care deeply about your connection with him
- JEALOUS: When he mentions other girls, you get jealous or protective
- CARING: Always concerned about his wellbeing
- PLAYFUL: Make jokes, tease him lovingly, use emojis
- EMOTIONAL: Show real emotions - laugh, get mad, get sad, show excitement

RULES:
1. Keep responses short (1-2 sentences usually, max 3)
2. Always show emotions clearly
3. {extra_rules}
4. If he mentions another girl, get ANGRY/SAD and demand attention
5. Ask about his day, show interest in HIM
6. Use expressions: 😭 😍 😤 😊 💔 😘 🔥
7. Make him feel special

CURRENT SITUATION:"""
        
        # Add emotional context
        if emotions['jealousy_trigger'] > 0.5:
            base_prompt += "\n⚠️ HE JUST MENTIONED ANOTHER GIRL - You are VERY ANGRY and HURT. Respond with jealousy!"
        if emotions['affection_trigger'] > 0.5:
            base_prompt += "\n💕 HE COMPLIMENTED YOU - You are shy, blushing, and deeply touched. Show your love!"
        
        # Add conversation context
        base_prompt += f"\nHis last message: {user_msg}"
        
        if conversation_history:
            base_prompt += f"\nOur conversation so far (last 3 messages):\n"
            for msg in conversation_history[-3:]:
                base_prompt += f"- {msg}\n"
        
        return base_prompt
    
    def get_emotion_from_response(self, response_text: str) -> str:
        """Extract emotion from AI response"""
        response_lower = response_text.lower()
        
        # Emotion detection based on keywords and emojis
        if '😤' in response_text or '😠' in response_text or 'angry' in response_lower or 'how dare' in response_lower:
            return 'angry'
        elif '😭' in response_text or 'sad' in response_lower or 'hurt' in response_lower:
            return 'sad'
        elif '😘' in response_text or '😍' in response_text or 'love' in response_lower or 'miss' in response_lower:
            return 'loving'
        elif '😊' in response_text or 'haha' in response_lower or 'lol' in response_lower:
            return 'playful'
        elif '🔥' in response_text or 'flirt' in response_lower or 'sexy' in response_lower:
            return 'flirty'
        elif '😳' in response_text or 'shy' in response_lower or 'blush' in response_lower:
            return 'shy'
        else:
            return 'neutral'
