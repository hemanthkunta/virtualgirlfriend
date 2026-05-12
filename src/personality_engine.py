import json
import os
from datetime import datetime
from typing import List, Dict

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text, create_engine, desc, func, insert, select, update

class ConversationMemory:
    """Manages conversation history and user preferences"""
    
    def __init__(self, db_path="virtualgirlfriend.db", database_url: str = None):
        if database_url is None:
            database_url = os.getenv('DATABASE_URL')

        if not database_url:
            if db_path.startswith('sqlite:///') or db_path.startswith('postgresql'):
                database_url = db_path
            else:
                database_url = f"sqlite:///{db_path}"

        self.database_url = database_url
        self.engine = create_engine(self.database_url, future=True)
        self.metadata = MetaData()

        self.conversations = Table(
            'conversations',
            self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('timestamp', DateTime, server_default=func.current_timestamp(), nullable=False),
            Column('user_message', Text, nullable=False),
            Column('ai_response', Text, nullable=False),
            Column('emotion_detected', String(64), nullable=False),
            Column('video_expression', Text, nullable=False),
            Column('language', String(16), nullable=False),
        )

        self.user_preferences = Table(
            'user_preferences',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('language', String(16), default='en'),
            Column('tts_voice_id', Text),
            Column('model_name', Text),
            Column('theme', Text),
        )

        self.init_database()
    
    def init_database(self):
        """Initialize the database tables."""
        self.metadata.create_all(self.engine)
    
    def save_conversation(self, user_msg: str, ai_response: str, 
                         emotion: str, video_expr: str, language: str):
        """Save conversation to database"""
        statement = insert(self.conversations).values(
            user_message=user_msg,
            ai_response=ai_response,
            emotion_detected=emotion,
            video_expression=video_expr,
            language=language,
        )
        with self.engine.begin() as connection:
            connection.execute(statement)
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get last N conversations"""
        statement = (
            select(
                self.conversations.c.user_message,
                self.conversations.c.ai_response,
                self.conversations.c.emotion_detected,
                self.conversations.c.timestamp,
            )
            .order_by(desc(self.conversations.c.timestamp), desc(self.conversations.c.id))
            .limit(limit)
        )

        with self.engine.connect() as connection:
            rows = connection.execute(statement).mappings().all()

        conversations = []
        for row in rows:
            conversations.append({
                'user': row['user_message'],
                'ai': row['ai_response'],
                'emotion': row['emotion_detected'],
                'timestamp': row['timestamp'],
            })
        return list(reversed(conversations))
    
    def get_user_preferences(self) -> Dict:
        """Get user preferences"""
        statement = select(self.user_preferences).where(self.user_preferences.c.id == 1)

        with self.engine.connect() as connection:
            row = connection.execute(statement).mappings().first()

        if row:
            return {
                'language': row['language'],
                'tts_voice_id': row['tts_voice_id'],
                'model_name': row['model_name'],
                'theme': row['theme']
            }
        return {'language': 'en', 'model_name': 'mistral'}
    
    def update_user_preferences(self, preferences: Dict):
        """Update user preferences"""
        values = {
            'language': preferences.get('language', 'en'),
            'tts_voice_id': preferences.get('tts_voice_id', ''),
            'model_name': preferences.get('model_name', 'mistral'),
            'theme': preferences.get('theme', 'light'),
        }

        with self.engine.begin() as connection:
            existing = connection.execute(
                select(self.user_preferences.c.id).where(self.user_preferences.c.id == 1)
            ).first()

            if existing:
                connection.execute(
                    update(self.user_preferences)
                    .where(self.user_preferences.c.id == 1)
                    .values(id=1, **values)
                )
            else:
                connection.execute(insert(self.user_preferences).values(id=1, **values))


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
