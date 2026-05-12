import json
import os
from typing import Dict, List, Tuple

class ExpressionMapper:
    """Maps AI emotions to appropriate facial expression videos"""
    
    def __init__(self):
        self.expression_map = self.load_expression_map()
    
    def load_expression_map(self) -> Dict[str, List[str]]:
        """
        Map emotions to facial expression videos from your collection
        """
        return {
            'loving': [
                'Woman_in_bedroom_with_smile_202605090914.mp4',
                'Woman_blowing_kiss_toward_camera_202605090914.mp4',
                'Woman_forming_heart_with_hands_202605090914.mp4',
                'Virtual_girl_smiling_warmly_202605090914.mp4',
                'Woman_with_empathetic_expression_202605090914.mp4',
            ],
            'caring': [
                'Woman_with_empathetic_expression_202605090914.mp4',
                'Woman_leaning_forward_intrigued_202605090914.mp4',
                'Woman_in_bedroom_with_smile_202605090914.mp4',
                'Virtual_girl_smiling_warmly_202605090914.mp4',
            ],
            'jealous': [
                'Woman_with_controlled_anger_202605090914.mp4',
                'Woman_rolling_eyes_at_camera_202605090914.mp4',
                'Girl_with_grumpy_expression_202605090913.mp4',
                'Girl_with_grumpy_pout_face_202605090913.mp4',
                'Woman_raising_eyebrow_skeptical_202605090914.mp4',
            ],
            'angry': [
                'Woman_with_controlled_anger_202605090914.mp4',
                'Woman_exhaling_in_frustration_202605090914.mp4',
                'Girl_with_grumpy_expression_202605090913.mp4',
                'Woman_rolling_eyes_at_camera_202605090914.mp4',
            ],
            'playful': [
                'Girl_giggling_with_joy_202605090914.mp4',
                'Girl_with_playful_shy_expression_202605090913.mp4',
                'Girl_sticking_tongue_out_202605090913.mp4',
                'Girl_making_silly_face_202605090913.mp4',
                'Woman_with_playful_smirk_202605090914.mp4',
                'Girl_with_raised_eyebrow_smirk_202605090913.mp4',
            ],
            'shy': [
                'Girl_peeking_shyly_through_hands_202605090913.mp4',
                'Girl_with_playful_shy_expression_202605090913.mp4',
                'Child_with_rosy_cheeks_smiling_202605090913.mp4',
                'Girl_with_puffed_cheeks_smiling_202605090913.mp4',
            ],
            'excited': [
                'Girl_gasping_in_excitement_shock_202605090913.mp4',
                'Girl_with_awe_expression_202605090913.mp4',
                'Woman_with_excited_grin_202605090914.mp4',
                'Girl_with_raised_eyebrow_smirk_202605090913.mp4',
            ],
            'sad': [
                'Girl_with_sad_eyes_looking_202605090913.mp4',
                'Girl_with_sad_eyes_pleading_202605090913.mp4',
                'Woman_crying_in_bedroom_202605090914.mp4',
                'Woman_with_sad_introspective_exp_202605090914.mp4',
                'Woman_looking_disappointed_in_be_202605090914.mp4',
            ],
            'flirty': [
                'Woman_with_flirty_smirk_202605090914.mp4',
                'Woman_puckering_lips_for_kiss_202605090914.mp4',
                'Woman_with_playful_smirk_202605090914.mp4',
                'Woman_blowing_kiss_toward_camera_202605090914.mp4',
                'Girl_with_guilty_grin_202605090913.mp4',
            ],
            'surprised': [
                'Girl_gasping_in_excitement_shock_202605090913.mp4',
                'Girl_with_awe_expression_202605090913.mp4',
                'Woman_in_bedroom_with_awe_202605090914.mp4',
                'Woman_reacting_surprised_in_bedroom_202605090914.mp4',
                'Girl_trying_not_to_laugh_202605090913.mp4',
            ],
            'thoughtful': [
                'Girl_tilting_head_thoughtfully_202605090914.mp4',
                'Woman_thinking_in_bedroom_202605090914.mp4',
                'Woman_staring_into_middle_distance_202605090914.mp4',
                'Woman_raising_eyebrow_skeptical_202605090914.mp4',
                'Sleepy_child_fighting_awake_202605090913.mp4',
            ],
            'default': [
                'Virtual_girl_smiling_warmly_202605090914.mp4',
                'Woman_in_bedroom_with_smile_202605090914.mp4',
            ]
        }
    
    def get_expression_for_emotion(self, emotion: str) -> str:
        """
        Get a video file for given emotion
        Returns the video filename from the facialexpressions folder
        """
        emotion_lower = emotion.lower().strip()
        
        if emotion_lower in self.expression_map:
            videos = self.expression_map[emotion_lower]
        else:
            videos = self.expression_map['default']
        
        import random
        # Return random video from the list for variety
        return random.choice(videos) if videos else random.choice(self.expression_map['default'])
    
    def get_multiple_expressions(self, emotion: str, count: int = 3) -> List[str]:
        """Get multiple video options for expression variety"""
        emotion_lower = emotion.lower().strip()
        
        if emotion_lower in self.expression_map:
            videos = self.expression_map[emotion_lower]
        else:
            videos = self.expression_map['default']
        
        return videos[:count]
    
    def get_video_path(self, video_filename: str, base_path: str = None) -> str:
        """Get full path to video file"""
        if base_path is None:
            base_path = os.path.join(os.path.dirname(__file__), '..', 'facialexpressions')
        
        return os.path.join(base_path, video_filename)
    
    def validate_video_exists(self, video_filename: str, base_path: str = None) -> bool:
        """Check if video file exists"""
        path = self.get_video_path(video_filename, base_path)
        return os.path.exists(path)
    
    def get_emotion_keywords(self) -> Dict[str, List[str]]:
        """
        Keywords that trigger each emotion
        Used for NLP-based emotion detection
        """
        return {
            'loving': ['love', 'miss', 'cute', 'beautiful', 'special', 'forever', 'yours'],
            'caring': ['care', 'worry', 'concerned', 'okay', 'health', 'sleep', 'eat'],
            'jealous': ['another girl', 'her', 'ex', 'friend girl', 'beautiful woman'],
            'angry': ['how dare', 'ridiculous', 'never', 'unacceptable', 'dare you'],
            'playful': ['haha', 'lol', 'funny', 'joke', 'tease', 'silly'],
            'shy': ['blush', 'shy', 'embarrassed', 'newbie'],
            'excited': ['amazing', 'awesome', 'wow', 'incredible', 'fantastic'],
            'sad': ['sorry', 'hurt', 'sad', 'pain', 'lonely', 'miss you'],
            'flirty': ['sexy', 'hot', 'flirt', 'kiss', 'seductive', 'charming'],
            'surprised': ['what', 'really', 'seriously', 'no way', 'unbelievable'],
        }
