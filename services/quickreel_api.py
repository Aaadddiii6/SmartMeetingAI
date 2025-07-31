import os
import time
import requests
import json
from typing import Dict, Optional
from config import Config

class QuickReelAPI:
    def __init__(self):
        self.api_key = Config.QUICKREEL_API_KEY
        self.base_url = Config.QUICKREEL_API_URL
        
    def create_reel(self, video_url: str, duration: int, caption: str, platforms: list, webhook_url: str = None) -> Dict:
        """
        Create a reel using QuickReel API
        """
        if not self.api_key:
            return self._mock_create_reel(video_url, duration, caption, platforms)
            
        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Prepare clip settings based on duration
            duration_range = self._get_duration_range(duration)
            
            # Create prompt based on caption and platforms
            prompt = self._create_prompt(caption, platforms)
            
            # Prepare request data
            data = {
                "videoUrl": video_url,
                "webhookUrl": webhook_url or "https://your-callback-url.com",  # You'll need to set up a webhook endpoint
                "language": "english",
                "clipSettings": {
                    "reelsCount": 1,
                    "prompt": prompt,
                    "keywords": self._extract_keywords(caption),
                    "reelDuration": duration_range
                },
                "brollSettings": {
                    "type": "mixed",
                    "frequency": "medium"
                },
                "bgmSettings": {
                    "volume": 0.3,
                    "fadeIn": 0.5,
                    "fadeOut": 0.5
                },
                "subtitleStyles": {
                    "template": "productive",
                    "position": "bottom-center",
                    "fontSize": "m"
                },
                "additionalFeatures": {
                    "addBgm": True,
                    "addBroll": True,
                    "removeFillerWords": True,
                    "removeSilenceParts": True,
                    "addHook": True
                }
            }
            
            response = requests.post(f"{self.base_url}/clip", headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                'success': True,
                'project_id': result.get('projectId'),
                'status': 'processing',
                'created_at': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_status(self, project_id: str) -> Dict:
        """
        Check the status of a reel generation project
        """
        if not self.api_key:
            return self._mock_check_status(project_id)
            
        try:
            headers = {
                "x-api-key": self.api_key
            }
            
            response = requests.get(f"{self.base_url}/projects/{project_id}", headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('status') == 'completed':
                outputs = result.get('outputs', [])
                if outputs:
                    output = outputs[0]
                    return {
                        'success': True,
                        'status': 'completed',
                        'video_url': output.get('videoUrl'),
                        'thumbnail_url': output.get('thumbnailUrl'),
                        'completed_at': time.time()
                    }
            
            return {
                'success': True,
                'status': result.get('status', 'processing'),
                'error': result.get('error')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_duration_range(self, duration: int) -> str:
        """
        Convert duration to QuickReel format
        """
        if duration <= 30:
            return "10-30"
        elif duration <= 60:
            return "30-60"
        elif duration <= 90:
            return "60-90"
        elif duration <= 120:
            return "90-120"
        else:
            return "10-30"  # Default
    
    def _create_prompt(self, caption: str, platforms: list) -> str:
        """
        Create a prompt for reel generation
        """
        platform_text = ", ".join(platforms) if platforms else "social media"
        
        prompt = f"Create a viral {platform_text} video that captures attention and drives engagement. "
        prompt += f"Focus on the key message: {caption}. "
        prompt += "Make it engaging, fast-paced, and optimized for social media viewing. "
        prompt += "Include dynamic visuals, clear messaging, and compelling hooks to maximize viewer retention."
        
        return prompt
    
    def _extract_keywords(self, caption: str) -> list:
        """
        Extract keywords from caption for better AI processing
        """
        # Simple keyword extraction - you could make this more sophisticated
        common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        words = caption.lower().split()
        keywords = [word for word in words if word not in common_words and len(word) > 3]
        return keywords[:5]  # Return top 5 keywords
    
    def _mock_create_reel(self, video_url: str, duration: int, caption: str, platforms: list) -> Dict:
        """
        Mock reel creation for testing without API key
        """
        print(f"Mock QuickReel: Creating reel for {duration}s with caption: {caption}")
        time.sleep(1)  # Simulate processing time
        
        project_id = f"mock_project_{int(time.time())}"
        
        return {
            'success': True,
            'project_id': project_id,
            'status': 'processing',
            'created_at': time.time()
        }
    
    def _mock_check_status(self, project_id: str) -> Dict:
        """
        Mock status check for testing without API key
        """
        print(f"Mock QuickReel: Checking status for project {project_id}")
        time.sleep(1)  # Simulate processing time
        
        # Simulate completion after some time
        if 'mock_project_' in project_id:
            timestamp = int(project_id.split('_')[-1])
            if time.time() - timestamp > 5:  # Complete after 5 seconds
                return {
                    'success': True,
                    'status': 'completed',
                    'video_url': f'/static/reels/mock_reel_{timestamp}.mp4',
                    'thumbnail_url': f'/static/thumbnails/mock_thumbnail_{timestamp}.jpg',
                    'completed_at': time.time()
                }
        
        return {
            'success': True,
            'status': 'processing'
        } 