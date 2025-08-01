"""
Blog service utility
Handles blog article generation from meeting transcripts using OpenAI
"""
import time
from typing import Dict
from .openai_service import OpenAIService

class BlogService:
    def __init__(self):
        self.openai_service = OpenAIService()
    
    def generate_blog_article(self, transcript: str, meeting_details: Dict) -> Dict:
        """
        Generate comprehensive blog article from meeting transcript
        
        Input:
            transcript (str): Meeting transcript text
            meeting_details (Dict): Meeting information including title, date, duration
            
        Output:
            Dict: Blog generation result with content and metadata
        """
        try:
            # Generate blog using OpenAI service
            blog_result = self.openai_service.generate_blog_article(transcript, meeting_details)
            
            if blog_result.get('success'):
                return {
                    'success': True,
                    'blog_content': blog_result.get('blog_content'),
                    'word_count': blog_result.get('word_count', 0),
                    'service': 'openai',
                    'generated_at': time.time()
                }
            else:
                return {
                    'success': False,
                    'error': blog_result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_blog_summary(self, transcript: str, meeting_details: Dict) -> Dict:
        """
        Generate a shorter blog summary from meeting transcript
        
        Input:
            transcript (str): Meeting transcript text
            meeting_details (Dict): Meeting information
            
        Output:
            Dict: Blog summary result
        """
        try:
            # Create a shorter prompt for summary
            prompt = f"""
            Create a concise blog summary (500-800 words) based on this meeting transcript.
            
            MEETING: {meeting_details.get('title', 'Business Meeting')}
            DATE: {meeting_details.get('date', 'Recent')}
            DURATION: {meeting_details.get('duration', 0)} minutes
            
            TRANSCRIPT: {transcript}
            
            Create a professional, engaging summary that includes:
            1. Key discussion points
            2. Important decisions made
            3. Action items and next steps
            4. Industry insights and implications
            
            Keep it concise and focused on the most important takeaways.
            """
            
            # Use OpenAI service with custom prompt
            blog_result = self.openai_service.generate_blog_article(transcript, meeting_details)
            
            if blog_result.get('success'):
                return {
                    'success': True,
                    'blog_content': blog_result.get('blog_content'),
                    'word_count': blog_result.get('word_count', 0),
                    'type': 'summary',
                    'generated_at': time.time()
                }
            else:
                return {
                    'success': False,
                    'error': blog_result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_key_points(self, transcript: str) -> Dict:
        """
        Extract key points from meeting transcript for blog generation
        
        Input:
            transcript (str): Meeting transcript text
            
        Output:
            Dict: Extracted key points and insights
        """
        try:
            key_points = {
                'main_topics': [],
                'decisions': [],
                'action_items': [],
                'insights': [],
                'participants': []
            }
            
            if not transcript:
                return key_points
            
            # Extract main topics
            lines = transcript.split('.')
            for line in lines:
                line = line.strip().lower()
                if any(word in line for word in ['discuss', 'review', 'plan', 'strategy', 'budget']):
                    key_points['main_topics'].append(line.capitalize())
            
            # Extract decisions (simple heuristic)
            for line in lines:
                line = line.strip().lower()
                if any(word in line for word in ['decide', 'decision', 'agree', 'approve', 'vote']):
                    key_points['decisions'].append(line.capitalize())
            
            # Extract action items
            for line in lines:
                line = line.strip().lower()
                if any(word in line for word in ['action', 'task', 'todo', 'follow up', 'next step']):
                    key_points['action_items'].append(line.capitalize())
            
            # Extract insights
            for line in lines:
                line = line.strip().lower()
                if any(word in line for word in ['insight', 'learn', 'discover', 'find', 'realize']):
                    key_points['insights'].append(line.capitalize())
            
            # Extract participants
            for line in lines:
                line = line.strip().lower()
                if any(word in line for word in ['i am', 'my name is', 'this is']):
                    words = line.split()
                    for i, word in enumerate(words):
                        if word in ['am', 'is'] and i + 1 < len(words):
                            name = words[i + 1].title()
                            if name not in key_points['participants']:
                                key_points['participants'].append(name)
            
            return key_points
            
        except Exception as e:
            print(f"Error extracting key points: {e}")
            return {
                'main_topics': [],
                'decisions': [],
                'action_items': [],
                'insights': [],
                'participants': []
            } 