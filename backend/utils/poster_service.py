"""
Poster service utility
Handles poster generation using multiple AI services (OpenAI, Stability AI, RunwayML)
"""
import os
import time
from typing import Dict
from .openai_service import OpenAIService
from .runwayml_service import RunwayMLService

class PosterService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.runwayml_service = RunwayMLService()
        # Note: Stability AI service would be added here when implemented
    
    def generate_poster_image(self, transcript: str, meeting_details: Dict) -> Dict:
        """
        Generate poster image from meeting transcript and details
        
        Input:
            transcript (str): Meeting transcript text
            meeting_details (Dict): Meeting information including title, date, duration
            
        Output:
            Dict: Poster generation result with image URL and metadata
        """
        try:
            # Try OpenAI DALL-E first (fallback)
            poster_result = self.openai_service.generate_poster_image(transcript, meeting_details)
            
            if poster_result.get('success'):
                return {
                    'success': True,
                    'image_url': poster_result.get('image_url'),
                    'prompt': poster_result.get('prompt'),
                    'service': 'openai',
                    'generated_at': time.time()
                }
            
            # If OpenAI fails, try RunwayML
            poster_result = self.runwayml_service.generate_poster_image(transcript, meeting_details)
            
            if poster_result.get('success'):
                return {
                    'success': True,
                    'image_url': poster_result.get('image_url'),
                    'prompt': poster_result.get('prompt'),
                    'service': 'runwayml',
                    'generated_at': time.time()
                }
            
            # If both fail, return error
            return {
                'success': False,
                'error': 'All poster generation services failed',
                'generated_at': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'generated_at': time.time()
            }
    
    def generate_poster_with_service(self, transcript: str, meeting_details: Dict, service: str = 'auto') -> Dict:
        """
        Generate poster using specific service
        
        Input:
            transcript (str): Meeting transcript text
            meeting_details (Dict): Meeting information
            service (str): Service to use ('openai', 'runwayml', 'stability', 'auto')
            
        Output:
            Dict: Poster generation result
        """
        try:
            if service == 'openai' or (service == 'auto' and self.openai_service.api_key):
                return self.openai_service.generate_poster_image(transcript, meeting_details)
            
            elif service == 'runwayml' or (service == 'auto' and self.runwayml_service.api_key):
                return self.runwayml_service.generate_poster_image(transcript, meeting_details)
            
            elif service == 'stability':
                # TODO: Implement Stability AI service
                return {
                    'success': False,
                    'error': 'Stability AI service not yet implemented'
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown or unavailable service: {service}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_meeting_info_for_poster(self, transcript: str) -> Dict:
        """
        Extract meeting information specifically for poster generation
        
        Input:
            transcript (str): Meeting transcript text
            
        Output:
            Dict: Meeting information optimized for poster generation
        """
        info = {
            'holder': 'Business Team',
            'agenda': 'Business discussion and planning',
            'topics': 'Strategic planning and team updates',
            'participants': 'Team members and stakeholders',
            'location': 'Conference Room / Virtual Meeting',
            'timing': 'To be scheduled'
        }
        
        if not transcript:
            return info
        
        # Extract meeting holder (person leading the meeting)
        transcript_lower = transcript.lower()
        
        # Common patterns for meeting holder identification
        holder_patterns = [
            'i am', 'my name is', 'this is', 'hello everyone, i\'m',
            'good morning, i\'m', 'good afternoon, i\'m', 'hi, i\'m',
            'welcome everyone, i\'m', 'thank you for joining, i\'m'
        ]
        
        for pattern in holder_patterns:
            if pattern in transcript_lower:
                # Extract the name after the pattern
                start_idx = transcript_lower.find(pattern) + len(pattern)
                end_idx = transcript_lower.find(' ', start_idx + 1)
                if end_idx > start_idx:
                    holder_name = transcript[start_idx:end_idx].strip()
                    if len(holder_name) > 2:  # Valid name length
                        info['holder'] = holder_name.title()
                        break
        
        # Look for common meeting phrases for agenda
        if 'quarterly' in transcript_lower:
            info['agenda'] = 'Quarterly review and planning'
        elif 'strategy' in transcript_lower:
            info['agenda'] = 'Strategic planning session'
        elif 'performance' in transcript_lower:
            info['agenda'] = 'Performance review and discussion'
        elif 'project' in transcript_lower:
            info['agenda'] = 'Project planning and updates'
        elif 'budget' in transcript_lower:
            info['agenda'] = 'Budget review and planning'
        elif 'team' in transcript_lower:
            info['agenda'] = 'Team meeting and updates'
        
        # Extract agenda items
        agenda_items = []
        lines = transcript.split('.')
        for line in lines:
            line = line.strip().lower()
            if any(word in line for word in ['discuss', 'review', 'plan', 'update', 'present']):
                agenda_items.append(line.capitalize())
        
        if agenda_items:
            info['agenda'] = '; '.join(agenda_items[:2])  # Take first 2 items
        
        return info 