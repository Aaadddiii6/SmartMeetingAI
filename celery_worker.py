import os
import time
from celery import Celery
from config import Config
from services.file_manager import FileManager
from services.pictory_api import PictoryAPI

# Initialize Celery
celery = Celery('smartmeetingai')
celery.conf.update(
    broker_url=Config.CELERY_BROKER_URL,
    result_backend=Config.CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Initialize services
file_manager = FileManager()
pictory_api = PictoryAPI()

@celery.task(bind=True)
def process_video_task(self, file_id: str, configs: list):
    """
    Background task to process video and generate multiple reels
    """
    try:
        # Get task data
        task_data = file_manager.get_task_data(file_id)
        if not task_data:
            raise Exception(f"Task data not found for file_id: {file_id}")
        
        # Update status to processing
        file_manager.update_task_status(file_id, 'processing', 5, 'Starting video processing...')
        
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
                file_manager.update_task_status(
                    file_id, 
                    'processing', 
                    progress, 
                    f'Generating reel {i+1}/{total_configs}...'
                )
                
                # Generate reel using Pictory API
                reel_result = pictory_api.create_reel(
                    video_path=video_path,
                    duration=config.get('duration', 30),
                    style=config.get('style', 'professional'),
                    caption=config.get('caption', ''),
                    platforms=config.get('platforms', [])
                )
                
                if not reel_result.get('success'):
                    raise Exception(f"Reel generation failed: {reel_result.get('error', 'Unknown error')}")
                
                # Create reel data
                reel_data = {
                    'id': f"reel_{file_id}_{i+1}",
                    'duration': config.get('duration', 30),
                    'style': config.get('style', 'professional'),
                    'caption': config.get('caption', ''),
                    'platforms': config.get('platforms', []),
                    'url': reel_result.get('reel_url'),
                    'thumbnail': reel_result.get('thumbnail_url'),
                    'file_path': reel_result.get('reel_path'),
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
        file_manager.save_task_data(file_id, task_data)
        
        # Update final status
        file_manager.update_task_status(file_id, 'completed', 100, 'All reels generated successfully!')
        
        print(f"Task completed for file_id: {file_id}")
        print(f"Generated {len(reels)} reels")
        
        return {
            'success': True,
            'file_id': file_id,
            'reels': reels,
            'message': 'All reels generated successfully'
        }
        
    except Exception as e:
        # Update status to error
        file_manager.update_task_status(file_id, 'error', 0, f'Error: {str(e)}')
        
        # Re-raise the exception for Celery
        raise e

@celery.task
def cleanup_old_files_task(days_old: int = 7):
    """
    Background task to clean up old files
    """
    try:
        deleted_count = file_manager.cleanup_old_files(days_old)
        return {
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Cleaned up {deleted_count} old files'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Cleanup failed'
        }

@celery.task
def get_file_stats_task():
    """
    Background task to get file statistics
    """
    try:
        stats = file_manager.get_file_stats()
        return {
            'success': True,
            'stats': stats
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    celery.start() 