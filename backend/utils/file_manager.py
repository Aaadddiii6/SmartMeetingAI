import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class FileManager:
    def __init__(self):
        self.tasks_file = 'tasks.json'
        self.files_file = 'files.json'
        self.load_tasks()
        self.load_files()
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r') as f:
                    self.tasks = json.load(f)
            else:
                self.tasks = {}
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = {}
    
    def load_files(self):
        """Load files metadata from JSON file"""
        try:
            if os.path.exists(self.files_file):
                with open(self.files_file, 'r') as f:
                    self.files = json.load(f)
            else:
                self.files = {}
        except Exception as e:
            print(f"Error loading files: {e}")
            self.files = {}
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def save_files(self):
        """Save files metadata to JSON file"""
        try:
            with open(self.files_file, 'w') as f:
                json.dump(self.files, f, indent=2)
        except Exception as e:
            print(f"Error saving files: {e}")
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file type is allowed"""
        allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        file_ext = os.path.splitext(filename)[1].lower()
        return file_ext in allowed_extensions
    
    def save_file_data(self, file_id: str, file_data: Dict):
        """Save file metadata"""
        self.files[file_id] = file_data
        self.save_files()
    
    def get_file_data(self, file_id: str) -> Optional[Dict]:
        """Get file metadata"""
        return self.files.get(file_id)
    
    def save_task_data(self, file_id: str, task_data: Dict):
        """Save task data for a file"""
        self.tasks[file_id] = task_data
        self.save_tasks()
    
    def get_task_data(self, file_id: str) -> Optional[Dict]:
        """Get task data for a file"""
        return self.tasks.get(file_id)
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def update_task_status(self, file_id: str, status: str, progress: int = 0, message: str = ""):
        """Update task status"""
        if file_id in self.tasks:
            self.tasks[file_id]['status'] = status
            self.tasks[file_id]['progress'] = progress
            self.tasks[file_id]['message'] = message
            self.tasks[file_id]['last_updated'] = datetime.now().isoformat()
            self.save_tasks()
    
    def get_video_info(self, file_path: str) -> Dict:
        """Get video file information (mock implementation for now)"""
        try:
            file_size = os.path.getsize(file_path)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            # Mock video info - in real implementation, you'd use ffprobe or similar
            video_info = {
                'file_size_mb': file_size_mb,
                'duration': '00:05:30',  # Mock duration
                'resolution': '1920x1080',  # Mock resolution
                'format': os.path.splitext(file_path)[1][1:].upper(),
                'upload_time': datetime.now().isoformat()
            }
            
            return video_info
            
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {
                'file_size_mb': 0,
                'duration': '00:00:00',
                'resolution': 'Unknown',
                'format': 'Unknown',
                'upload_time': datetime.now().isoformat()
            }
    
    def cleanup_old_files(self, days_old: int = 7):
        """Clean up old files and tasks"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        files_to_delete = []
        for file_id, task_data in self.tasks.items():
            upload_time = datetime.fromisoformat(task_data.get('upload_time', '1970-01-01'))
            if upload_time.timestamp() < cutoff_date:
                files_to_delete.append(file_id)
        
        for file_id in files_to_delete:
            # Delete file
            file_path = self.tasks[file_id].get('file_path')
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
            
            # Delete reel if exists
            reel_path = self.tasks[file_id].get('reel_path')
            if reel_path and os.path.exists(reel_path):
                try:
                    os.remove(reel_path)
                except Exception as e:
                    print(f"Error deleting reel {reel_path}: {e}")
            
            # Remove from tasks
            del self.tasks[file_id]
        
        self.save_tasks()
        return len(files_to_delete)
    
    def get_file_stats(self) -> Dict:
        """Get file storage statistics"""
        total_files = len(self.tasks)
        total_size_mb = sum(task.get('video_info', {}).get('file_size_mb', 0) for task in self.tasks.values())
        
        status_counts = {}
        for task in self.tasks.values():
            status = task.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size_mb, 2),
            'status_counts': status_counts
        } 