import os
import time
import requests
from typing import Dict, Optional
from config import Config

class RunwayMLService:
    def __init__(self):
        self.api_key = Config.RUNWAYML_API_KEY
        self.base_url = Config.RUNWAYML_API_URL
        
    def generate_poster_image(self, transcript: str, meeting_details: Dict) -> Dict:
        """
        Generate a professional poster using RunwayML
        """
        if not self.api_key:
            return self._mock_generate_poster(transcript, meeting_details)
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create detailed prompt for RunwayML
            prompt = self._create_runwayml_prompt(transcript, meeting_details)
            
            data = {
                "model": "gen-3",  # RunwayML's latest model
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
                "num_frames": 1,
                "num_steps": 50,
                "guidance_scale": 7.5,
                "scheduler": "ddim"
            }
            
            response = requests.post(f"{self.base_url}/generations", headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            image_url = result['data'][0]['url']
            
            return {
                'success': True,
                'image_url': image_url,
                'prompt': prompt,
                'generated_at': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_runwayml_prompt(self, transcript: str, meeting_details: Dict) -> str:
        """
        Create a detailed prompt optimized for RunwayML's design capabilities
        """
        title = meeting_details.get('title', 'Business Meeting')
        date = meeting_details.get('date', 'Recent')
        duration = meeting_details.get('duration', 0)
        
        # Extract meeting details from transcript
        meeting_info = self._extract_meeting_info(transcript)
        
        prompt = f"""
        Create a clean, professional meeting poster with ONLY these essential elements:

        MEETING INFORMATION:
        - MEETING HOLDER: {meeting_info.get('holder', 'Business Team')}
        - AGENDA: {meeting_info.get('agenda', 'Business discussion and planning')}
        - DATE: {date}
        - TIME: {duration} minutes duration

        DESIGN REQUIREMENTS:
        - Clean, minimalist business flyer design (flat design, no 3D effects)
        - Professional corporate colors: blues, grays, whites
        - Large, clear typography for the meeting holder name
        - Simple layout with just the 4 essential elements
        - Clean background with subtle professional styling
        - NO extra text, NO icons, NO complex layouts
        - Focus only on: Holder, Agenda, Date, Time
        - NO room background, NO wall placement - just a flat flyer

        The poster should be simple and clean, showing only the meeting holder, agenda, date, and time in a professional business format.
        """
        
        return prompt.strip()
    
    def _extract_meeting_info(self, transcript: str) -> Dict:
        """
        Extract meeting information from transcript for poster generation
        """
        info = {
            'holder': 'Business Team',
            'agenda': 'Business discussion and planning',
            'topics': 'Strategic planning and team updates',
            'participants': 'Team members and stakeholders',
            'location': 'Conference Room / Virtual Meeting',
            'timing': 'To be scheduled'
        }
        
        # Extract meeting holder and topics from transcript
        if transcript:
            # Look for meeting holder (person leading the meeting)
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
    
    def _mock_generate_poster(self, transcript: str, meeting_details: Dict) -> Dict:
        """
        Mock poster generation for testing without API key
        """
        print(f"Mock RunwayML: Generating poster for meeting: {meeting_details.get('title', 'Business Meeting')}")
        time.sleep(2)  # Simulate processing time
        
        # Create a mock poster file
        poster_filename = f"runwayml_poster_{int(time.time())}.jpg"
        poster_path = os.path.join('static', 'posters', poster_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(poster_path), exist_ok=True)
        
        # Create a dummy poster file
        with open(poster_path, 'w') as f:
            f.write(f"Mock RunwayML poster for {meeting_details.get('title', 'Business Meeting')}")
        
        return {
            'success': True,
            'image_url': f'/static/posters/{poster_filename}',
            'prompt': self._create_runwayml_prompt(transcript, meeting_details),
            'generated_at': time.time()
        } 