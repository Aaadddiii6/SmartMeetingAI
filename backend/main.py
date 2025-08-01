"""
Main Flask application
Handles all API route definitions with clean RESTful approach
"""
import os
import uuid
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

# Import configuration and utilities
from config import Config
from utils.file_manager import FileManager
from utils.video_processor import VideoProcessor
from utils.transcript_service import TranscriptService
from utils.poster_service import PosterService
from utils.blog_service import BlogService
from utils.reel_service import ReelService

# Initialize Flask app
app = Flask(__name__, 
           template_folder='../frontend',
           static_folder='../frontend/static')
app.config.from_object(Config)

# Initialize services
file_manager = FileManager()
video_processor = VideoProcessor()
transcript_service = TranscriptService()
poster_service = PosterService()
blog_service = BlogService()
reel_service = ReelService()

# Ensure upload directory exists
UPLOAD_FOLDER = Path(Config.UPLOAD_FOLDER)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# API Routes

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """
    Upload video file
    Input: Multipart form data with 'video' file
    Output: JSON with file_id and status
    """
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'message': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not file_manager.allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Generate unique file ID and save file
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_path = UPLOAD_FOLDER / f"{file_id}_{filename}"
        file.save(file_path)
        
        # Get video info and create task entry
        video_info = file_manager.get_video_info(str(file_path))
        task_data = {
            'filename': filename,
            'file_path': str(file_path),
            'status': 'uploaded',
            'created_at': datetime.now().isoformat(),
            'video_info': video_info,
            'reels': []
        }
        
        file_manager.save_task_data(file_id, task_data)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'message': 'Video uploaded successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500

@app.route('/api/generate-reels', methods=['POST'])
def generate_reels():
    """
    Generate reels from uploaded video
    Input: JSON with file_id and configs array
    Output: JSON with status and message
    """
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        configs = data.get('configs', [])
        
        if not file_id:
            return jsonify({'success': False, 'message': 'File ID required'}), 400
        
        task_data = file_manager.get_task_data(file_id)
        if not task_data:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        # Update task status and start processing
        task_data['status'] = 'processing'
        task_data['configs'] = configs
        task_data['reels'] = []
        file_manager.save_task_data(file_id, task_data)
        
        # Start background thread for reel generation
        thread = threading.Thread(target=video_processor.process_video_thread, args=(file_id, configs))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Reel generation started'
        })
        
    except Exception as e:
        app.logger.error(f"Generation error: {str(e)}")
        return jsonify({'success': False, 'message': f'Generation failed: {str(e)}'}), 500

@app.route('/api/status/<task_id>')
def check_status(task_id):
    """
    Check the status of a processing task
    Input: task_id in URL path
    Output: JSON with current status and progress
    """
    try:
        task_info = file_manager.get_task_data(task_id)
        
        if not task_info:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        # Check with external service if still processing
        if task_info.get('status') == 'processing':
            project_id = task_info.get('project_id')
            if project_id:
                status_result = reel_service.check_status(project_id)
                
                if status_result.get('success') and status_result.get('status') == 'completed':
                    task_info.update({
                        'status': 'completed',
                        'video_url': status_result.get('video_url'),
                        'thumbnail_url': status_result.get('thumbnail_url'),
                        'completed_at': status_result.get('completed_at')
                    })
                    file_manager.save_task_data(task_id, task_info)
                    
                    return jsonify({
                        'success': True,
                        'status': 'completed',
                        'video_url': status_result.get('video_url'),
                        'thumbnail_url': status_result.get('thumbnail_url')
                    })
                
                elif status_result.get('success') and status_result.get('status') == 'failed':
                    task_info.update({
                        'status': 'failed',
                        'error': status_result.get('error', 'Unknown error')
                    })
                    file_manager.save_task_data(task_id, task_info)
                    
                    return jsonify({
                        'success': False,
                        'status': 'failed',
                        'error': status_result.get('error', 'Unknown error')
                    })
        
        return jsonify({
            'success': True,
            'status': task_info.get('status'),
            'video_url': task_info.get('video_url'),
            'thumbnail_url': task_info.get('thumbnail_url'),
            'error': task_info.get('error')
        })
        
    except Exception as e:
        print(f"Status check error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-transcript', methods=['POST'])
def generate_transcript():
    """
    Generate transcript from uploaded video
    Input: JSON with file_id
    Output: JSON with transcript data
    """
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        
        if not file_id:
            return jsonify({'success': False, 'message': 'File ID required'}), 400
        
        task_data = file_manager.get_task_data(file_id)
        if not task_data:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        video_path = task_data.get('file_path')
        if not video_path or not os.path.exists(video_path):
            return jsonify({'success': False, 'message': 'Video file not found'}), 404
        
        # Generate transcript using service
        transcript_result = transcript_service.generate_transcript(video_path)
        
        if transcript_result.get('success'):
            task_data['transcript'] = transcript_result
            file_manager.save_task_data(file_id, task_data)
            
            return jsonify({
                'success': True,
                'transcript': transcript_result,
                'message': 'Transcript generated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Transcript generation failed: {transcript_result.get("error", "Unknown error")}'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Transcript generation error: {str(e)}")
        return jsonify({'success': False, 'message': f'Transcript generation failed: {str(e)}'}), 500

@app.route('/api/generate-poster', methods=['POST'])
def generate_poster():
    """
    Generate poster from meeting transcript
    Input: JSON with file_id
    Output: JSON with poster image data
    """
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        
        if not file_id:
            return jsonify({'success': False, 'message': 'File ID required'}), 400
        
        task_data = file_manager.get_task_data(file_id)
        if not task_data:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        transcript_data = task_data.get('transcript')
        if not transcript_data:
            return jsonify({'success': False, 'message': 'Transcript not found. Generate transcript first.'}), 400
        
        # Prepare meeting details
        meeting_details = {
            'title': task_data.get('filename', 'Business Meeting'),
            'date': task_data.get('created_at', 'Recent'),
            'duration': transcript_data.get('audio_duration', 0)
        }
        
        # Generate poster using service
        poster_result = poster_service.generate_poster_image(
            transcript_data.get('transcript', ''),
            meeting_details
        )
        
        if poster_result.get('success'):
            task_data['poster'] = poster_result
            file_manager.save_task_data(file_id, task_data)
            
            return jsonify({
                'success': True,
                'poster': poster_result,
                'message': 'Poster generated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Poster generation failed: {poster_result.get("error", "Unknown error")}'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Poster generation error: {str(e)}")
        return jsonify({'success': False, 'message': f'Poster generation failed: {str(e)}'}), 500

@app.route('/api/generate-blog', methods=['POST'])
def generate_blog():
    """
    Generate blog article from meeting transcript
    Input: JSON with file_id
    Output: JSON with blog content
    """
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        
        if not file_id:
            return jsonify({'success': False, 'message': 'File ID required'}), 400
        
        task_data = file_manager.get_task_data(file_id)
        if not task_data:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        transcript_data = task_data.get('transcript')
        if not transcript_data:
            return jsonify({'success': False, 'message': 'Transcript not found. Generate transcript first.'}), 400
        
        # Prepare meeting details
        meeting_details = {
            'title': task_data.get('filename', 'Business Meeting'),
            'date': task_data.get('created_at', 'Recent'),
            'duration': transcript_data.get('audio_duration', 0)
        }
        
        # Generate blog using service
        blog_result = blog_service.generate_blog_article(
            transcript_data.get('transcript', ''),
            meeting_details
        )
        
        if blog_result.get('success'):
            task_data['blog'] = blog_result
            file_manager.save_task_data(file_id, task_data)
            
            return jsonify({
                'success': True,
                'blog': blog_result,
                'message': 'Blog article generated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Blog generation failed: {blog_result.get("error", "Unknown error")}'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Blog generation error: {str(e)}")
        return jsonify({'success': False, 'message': f'Blog generation failed: {str(e)}'}), 500

@app.route('/api/download/<file_id>/<reel_id>')
def download_reel(file_id, reel_id):
    """
    Download generated reel
    Input: file_id and reel_id in URL path
    Output: File download
    """
    try:
        task_data = file_manager.get_task_data(file_id)
        if not task_data:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        reel = next((r for r in task_data.get('reels', []) if r.get('id') == reel_id), None)
        
        if not reel:
            return jsonify({'success': False, 'message': 'Reel not found'}), 404
        
        reel_path = Path(reel.get('file_path', ''))
        if not reel_path.exists():
            return jsonify({'success': False, 'message': 'Reel file not found'}), 404
        
        return send_from_directory(
            reel_path.parent,
            reel_path.name,
            as_attachment=True,
            download_name=f"reel_{reel_id}.mp4"
        )
        
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return jsonify({'success': False, 'message': f'Download failed: {str(e)}'}), 500

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """
    Handle external service webhook callbacks
    Input: JSON webhook data
    Output: JSON confirmation
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        project_id = data.get('projectId')
        status = data.get('status')
        
        if not project_id:
            return jsonify({'success': False, 'error': 'No project ID'}), 400
        
        # Update task status based on webhook
        if status == 'completed':
            outputs = data.get('outputs', [])
            if outputs:
                output = outputs[0]
                video_url = output.get('videoUrl')
                thumbnail_url = output.get('thumbnailUrl')
                
                task_info = file_manager.get_task_data(project_id)
                if task_info:
                    task_info.update({
                        'status': 'completed',
                        'video_url': video_url,
                        'thumbnail_url': thumbnail_url,
                        'completed_at': datetime.now().isoformat()
                    })
                    file_manager.save_task_data(project_id, task_info)
        
        elif status == 'failed':
            error = data.get('error', 'Unknown error')
            task_info = file_manager.get_task_data(project_id)
            if task_info:
                task_info.update({
                    'status': 'failed',
                    'error': error
                })
                file_manager.save_task_data(project_id, task_info)
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Static file serving routes
@app.route('/static/reels/<path:filename>')
def serve_reel(filename):
    """Serve reel files"""
    return send_from_directory('static/reels', filename)

@app.route('/static/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    """Serve thumbnail files"""
    return send_from_directory('static/thumbnails', filename)

@app.route('/static/posters/<path:filename>')
def serve_poster(filename):
    """Serve poster files"""
    return send_from_directory('static/posters', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 