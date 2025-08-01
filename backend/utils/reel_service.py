"""
Reel service utility
Handles reel generation using QuickReel API
"""
import time
from typing import Dict, List
from .quickreel_api import QuickReelAPI

class ReelService:
    def __init__(self):
        self.quickreel_api = QuickReelAPI()
    
    def create_reel(self, video_url: str, duration: int = 30, caption: str = '', 
                   platforms: List[str] = None, webhook_url: str = None) -> Dict:
        """
        Create a reel from video using QuickReel API
        
        Input:
            video_url (str): URL to the video file
            duration (int): Duration of the reel in seconds
            caption (str): Caption text for the reel
            platforms (List[str]): Target platforms (e.g., ['instagram', 'tiktok'])
            webhook_url (str): Webhook URL for status updates
            
        Output:
            Dict: Reel creation result with project_id and status
        """
        try:
            if platforms is None:
                platforms = ['instagram']
            
            # Create reel using QuickReel API
            reel_result = self.quickreel_api.create_reel(
                video_url=video_url,
                duration=duration,
                caption=caption,
                platforms=platforms,
                webhook_url=webhook_url
            )
            
            if reel_result.get('success'):
                return {
                    'success': True,
                    'project_id': reel_result.get('project_id'),
                    'video_url': reel_result.get('video_url'),
                    'thumbnail_url': reel_result.get('thumbnail_url'),
                    'status': 'processing',
                    'created_at': time.time()
                }
            else:
                return {
                    'success': False,
                    'error': reel_result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_status(self, project_id: str) -> Dict:
        """
        Check the status of a reel generation project
        
        Input:
            project_id (str): QuickReel project ID
            
        Output:
            Dict: Project status and results
        """
        try:
            status_result = self.quickreel_api.check_status(project_id)
            
            if status_result.get('success'):
                return {
                    'success': True,
                    'status': status_result.get('status'),
                    'video_url': status_result.get('video_url'),
                    'thumbnail_url': status_result.get('thumbnail_url'),
                    'completed_at': status_result.get('completed_at'),
                    'error': status_result.get('error')
                }
            else:
                return {
                    'success': False,
                    'error': status_result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_reel_configurations(self) -> Dict:
        """
        Get available reel configuration options
        
        Output:
            Dict: Available configurations for reel generation
        """
        return {
            'durations': [15, 30, 60, 90],
            'platforms': ['instagram', 'tiktok', 'youtube', 'facebook'],
            'styles': ['professional', 'casual', 'creative', 'minimal'],
            'aspect_ratios': {
                'instagram': '9:16',
                'tiktok': '9:16',
                'youtube': '16:9',
                'facebook': '16:9'
            }
        }
    
    def validate_reel_config(self, config: Dict) -> Dict:
        """
        Validate reel configuration parameters
        
        Input:
            config (Dict): Reel configuration to validate
            
        Output:
            Dict: Validation result with any errors
        """
        errors = []
        
        # Validate duration
        duration = config.get('duration', 30)
        if duration not in [15, 30, 60, 90]:
            errors.append(f"Invalid duration: {duration}. Must be 15, 30, 60, or 90 seconds.")
        
        # Validate platforms
        platforms = config.get('platforms', ['instagram'])
        valid_platforms = ['instagram', 'tiktok', 'youtube', 'facebook']
        for platform in platforms:
            if platform not in valid_platforms:
                errors.append(f"Invalid platform: {platform}. Must be one of {valid_platforms}")
        
        # Validate style
        style = config.get('style', 'professional')
        valid_styles = ['professional', 'casual', 'creative', 'minimal']
        if style not in valid_styles:
            errors.append(f"Invalid style: {style}. Must be one of {valid_styles}")
        
        # Validate caption length
        caption = config.get('caption', '')
        if len(caption) > 2200:  # Instagram caption limit
            errors.append(f"Caption too long: {len(caption)} characters. Max 2200 characters.")
        
        if errors:
            return {
                'valid': False,
                'errors': errors
            }
        else:
            return {
                'valid': True,
                'errors': []
            } 