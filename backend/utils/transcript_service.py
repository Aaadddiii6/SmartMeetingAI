"""
Transcript service utility
Handles transcript generation from video files using AssemblyAI
"""
import os
import time
from typing import Dict
from .assemblyai_service import AssemblyAIService

class TranscriptService:
    def __init__(self):
        self.assemblyai_service = AssemblyAIService()
    
    def generate_transcript(self, video_path: str) -> Dict:
        """
        Generate transcript from video file using AssemblyAI
        
        Input:
            video_path (str): Path to the video file
            
        Output:
            Dict: Transcript data including text, timestamps, and metadata
        """
        try:
            if not os.path.exists(video_path):
                return {
                    'success': False,
                    'error': f'Video file not found: {video_path}'
                }
            
            # Generate transcript using AssemblyAI service
            transcript_result = self.assemblyai_service.transcribe_video(video_path)
            
            if transcript_result.get('success'):
                return {
                    'success': True,
                    'transcript': transcript_result.get('transcript', ''),
                    'audio_duration': transcript_result.get('audio_duration', 0),
                    'confidence': transcript_result.get('confidence', 0),
                    'words': transcript_result.get('words', []),
                    'generated_at': time.time()
                }
            else:
                return {
                    'success': False,
                    'error': transcript_result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_meeting_info(self, transcript: str) -> Dict:
        """
        Extract meeting information from transcript
        
        Input:
            transcript (str): Raw transcript text
            
        Output:
            Dict: Extracted meeting information including participants, topics, etc.
        """
        try:
            info = {
                'participants': [],
                'topics': [],
                'duration': 0,
                'meeting_type': 'general',
                'key_points': []
            }
            
            if not transcript:
                return info
            
            # Extract participants (simple heuristic)
            lines = transcript.split('.')
            for line in lines:
                line = line.strip().lower()
                if any(word in line for word in ['i am', 'my name is', 'this is']):
                    # Extract name after these phrases
                    words = line.split()
                    for i, word in enumerate(words):
                        if word in ['am', 'is'] and i + 1 < len(words):
                            name = words[i + 1].title()
                            if name not in info['participants']:
                                info['participants'].append(name)
            
            # Extract topics
            topic_keywords = ['discuss', 'review', 'plan', 'update', 'present', 'meeting']
            for line in lines:
                line = line.strip().lower()
                if any(keyword in line for keyword in topic_keywords):
                    info['topics'].append(line.capitalize())
            
            # Determine meeting type
            if any(word in transcript.lower() for word in ['quarterly', 'quarter']):
                info['meeting_type'] = 'quarterly_review'
            elif any(word in transcript.lower() for word in ['strategy', 'strategic']):
                info['meeting_type'] = 'strategic_planning'
            elif any(word in transcript.lower() for word in ['performance', 'review']):
                info['meeting_type'] = 'performance_review'
            elif any(word in transcript.lower() for word in ['project', 'planning']):
                info['meeting_type'] = 'project_planning'
            
            # Extract key points (simple approach)
            sentences = transcript.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and any(word in sentence.lower() for word in ['important', 'key', 'critical', 'decision']):
                    info['key_points'].append(sentence)
            
            return info
            
        except Exception as e:
            print(f"Error extracting meeting info: {e}")
            return {
                'participants': [],
                'topics': [],
                'duration': 0,
                'meeting_type': 'general',
                'key_points': []
            } 