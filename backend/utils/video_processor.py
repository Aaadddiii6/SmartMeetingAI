"""
Video processing utility
Handles video processing and reel generation logic
"""
import os
import time
import threading
from datetime import datetime
from typing import List, Dict
from .file_manager import FileManager
from .reel_service import ReelService

class VideoProcessor:
    def __init__(self):
        self.file_manager = FileManager()
        self.reel_service = ReelService()
    
    def process_video_thread(self, file_id: str, configs: List[Dict]) -> None:
        """
        Background thread to process video and generate reels
        
        Input:
            file_id (str): Unique identifier for the uploaded file
            configs (List[Dict]): List of reel configuration dictionaries
        
        Output:
            None (updates task data in file manager)
        """
        try:
            # Get task data
            task_data = self.file_manager.get_task_data(file_id)
            if not task_data:
                print(f"Task data not found for file_id: {file_id}")
                return
            
            # Update status to processing
            self.file_manager.update_task_status(file_id, 'processing', 5, 'Starting video processing...')
            
            # Check if video file exists
            video_path = task_data.get('file_path')
            if not video_path or not os.path.exists(video_path):
                raise Exception(f"Video file not found: {video_path}")
            
            # Initialize reels array
            reels = []
            total_configs = len(configs)
            
            for i, config in enumerate(configs):
                try:
                    # Update progress for each reel
                    progress = int((i / total_configs) * 80) + 10
                    self.file_manager.update_task_status(
                        file_id, 
                        'processing', 
                        progress, 
                        f'Generating reel {i+1}/{total_configs}...'
                    )
                    
                    # Generate reel using ReelService
                    reel_result = self.reel_service.create_reel(
                        video_url=f"http://localhost:5000/uploads/{task_data.get('filename', 'video.mp4')}",
                        duration=config.get('duration', 30),
                        caption=config.get('caption', ''),
                        platforms=config.get('platforms', ['instagram']),
                        webhook_url="http://localhost:5000/api/webhook"
                    )
                    
                    if not reel_result.get('success'):
                        raise Exception(f"Reel generation failed: {reel_result.get('error', 'Unknown error')}")
                    
                    # Store project_id for status checking
                    project_id = reel_result.get('project_id')
                    if project_id:
                        task_data['project_id'] = project_id
                        self.file_manager.save_task_data(file_id, task_data)
                    
                    # Create reel data
                    reel_data = {
                        'id': f"reel_{file_id}_{i+1}",
                        'duration': config.get('duration', 30),
                        'style': config.get('style', 'professional'),
                        'caption': config.get('caption', ''),
                        'platforms': config.get('platforms', []),
                        'url': reel_result.get('video_url'),
                        'thumbnail': reel_result.get('thumbnail_url'),
                        'file_path': reel_result.get('video_url'),
                        'status': 'completed',
                        'progress': 100,
                        'message': 'Reel generated successfully'
                    }
                    
                    reels.append(reel_data)
                    
                    # Simulate processing time
                    time.sleep(2)
                    
                except Exception as e:
                    # Add failed reel to list
                    reel_data = {
                        'id': f"reel_{file_id}_{i+1}",
                        'duration': config.get('duration', 30),
                        'style': config.get('style', 'professional'),
                        'caption': config.get('caption', ''),
                        'platforms': config.get('platforms', []),
                        'status': 'failed',
                        'progress': 0,
                        'message': f'Error: {str(e)}'
                    }
                    reels.append(reel_data)
            
            # Update task data with reels information
            task_data['reels'] = reels
            task_data['status'] = 'completed'
            task_data['completed_at'] = datetime.now().isoformat()
            
            # Save updated task data
            self.file_manager.save_task_data(file_id, task_data)
            
            # Update final status
            self.file_manager.update_task_status(file_id, 'completed', 100, 'All reels generated successfully!')
            
            print(f"Task completed for file_id: {file_id}")
            print(f"Generated {len(reels)} reels")
            
        except Exception as e:
            # Update status to error
            self.file_manager.update_task_status(file_id, 'error', 0, f'Error: {str(e)}')
            print(f"Error processing video: {str(e)}")
    
    def get_video_info(self, file_path: str) -> Dict:
        """
        Get video information from file
        
        Input:
            file_path (str): Path to the video file
            
        Output:
            Dict: Video information including duration, resolution, etc.
        """
        try:
            # This would typically use ffmpeg or similar to get video info
            # For now, return basic info
            return {
                'duration': 0,
                'resolution': 'Unknown',
                'format': 'Unknown',
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {
                'duration': 0,
                'resolution': 'Unknown',
                'format': 'Unknown',
                'size': 0
            } 