import requests
import json
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

class OllamaInterface:
    """Interface to communicate with Ollama models"""
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model_name: str = "mistral"):
        """
        Initialize Ollama interface
        
        Args:
            base_url: Ollama server URL (default: localhost:11434)
            model_name: Model to use (mistral, neural-chat, dolphin-mixtral, etc.)
        """
        self.base_url = base_url
        self.model_name = model_name
        self.generate_endpoint = f"{base_url}/api/generate"
    
    def check_connection(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_available_models(self) -> List[str]:
        """List all available models on Ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []
    
    def generate_response(self, prompt: str, system_prompt: str = None,
                         temperature: float = 0.7, 
                         top_p: float = 0.9,
                         max_tokens: int = 150) -> str:
        """
        Generate response from Ollama model
        
        Args:
            prompt: User input/query
            system_prompt: System instructions (personality/role)
            temperature: Creativity level (0-1, higher = more creative)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum response length
            
        Returns:
            Generated response text
        """
        if not self.check_connection():
            raise Exception("Ollama server is not running. Start it with: ollama serve")
        
        # Combine system and user prompts
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nResponse:"
        else:
            full_prompt = prompt
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            }
            
            response = requests.post(self.generate_endpoint, json=payload, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                raise Exception(f"Ollama error: {response.status_code}")
        
        except requests.exceptions.Timeout:
            raise Exception("Request to Ollama timed out. Try increasing timeout or using shorter prompt.")
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    def generate_response_stream(self, prompt: str, system_prompt: str = None,
                                temperature: float = 0.7):
        """
        Generate response with streaming (real-time token generation)
        
        Yields tokens as they are generated
        """
        if not self.check_connection():
            raise Exception("Ollama server is not running")
        
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nResponse:"
        else:
            full_prompt = prompt
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": True,
            "temperature": temperature,
        }
        
        try:
            response = requests.post(self.generate_endpoint, json=payload, 
                                   stream=True, timeout=60)
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']
        
        except Exception as e:
            raise Exception(f"Error in streaming: {str(e)}")


class ConversationManager:
    """Manages multi-turn conversations with context"""
    
    def __init__(self, ollama: OllamaInterface):
        self.ollama = ollama
        self.conversation_history: List[Dict[str, str]] = []
        self.context_limit = 5  # Keep last 5 exchanges
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            'role': role,
            'content': content
        })
        
        # Keep only recent messages for context
        if len(self.conversation_history) > self.context_limit * 2:
            self.conversation_history = self.conversation_history[-self.context_limit * 2:]
    
    def get_context_string(self) -> str:
        """Get recent conversation context as string"""
        context_lines = []
        for msg in self.conversation_history[-4:]:  # Last 2 exchanges
            role = "You" if msg['role'] == 'assistant' else "Him"
            context_lines.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_lines)
    
    def generate_response(self, user_message: str, system_prompt: str,
                         temperature: float = 0.7) -> str:
        """
        Generate AI response with conversation context
        """
        # Add user message to history
        self.add_message('user', user_message)
        
        # Get context string for better coherence
        context = self.get_context_string()
        
        # Create enhanced prompt with context
        enhanced_prompt = f"{system_prompt}\n\nPrevious conversation:\n{context}"
        
        # Generate response
        response = self.ollama.generate_response(
            prompt=user_message,
            system_prompt=enhanced_prompt,
            temperature=temperature,
            max_tokens=200
        )
        
        # Add assistant response to history
        self.add_message('assistant', response)
        
        return response
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


# Recommended Ollama models for this use case
RECOMMENDED_MODELS = {
    'mistral': {
        'name': 'mistral',
        'description': 'Fast, balanced, good for roleplay',
        'recommended': True,
        'parameters': {'temperature': 0.8, 'top_p': 0.95}
    },
    'neural-chat': {
        'name': 'neural-chat',
        'description': 'Good conversational AI, great for character roleplay',
        'recommended': True,
        'parameters': {'temperature': 0.7, 'top_p': 0.9}
    },
    'dolphin-mixtral': {
        'name': 'dolphin-mixtral',
        'description': 'More powerful, better personality',
        'recommended': True,
        'parameters': {'temperature': 0.75, 'top_p': 0.92}
    },
    'zephyr': {
        'name': 'zephyr',
        'description': 'Lightweight, good personality',
        'recommended': False,
        'parameters': {'temperature': 0.8, 'top_p': 0.9}
    },
    'orca-mini': {
        'name': 'orca-mini',
        'description': 'Smaller, faster but less capable',
        'recommended': False,
        'parameters': {'temperature': 0.7, 'top_p': 0.85}
    }
}

def get_model_recommendation() -> Dict:
    """Get recommended model configuration for virtual girlfriend"""
    return RECOMMENDED_MODELS['mistral']  # or 'neural-chat' or 'dolphin-mixtral'
