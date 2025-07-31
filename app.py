#!/usr/bin/env python3
"""
SmartMeetingAI Flask Application
Main application for video upload and reel generation
"""

import os
import json
import uuid
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from config import Config
from services.file_manager import FileManager
from services.quickreel_api import QuickReelAPI
from services.assemblyai_service import AssemblyAIService
from services.openai_service import OpenAIService

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
file_manager = FileManager()
quickreel_api = QuickReelAPI()
assemblyai_service = AssemblyAIService()
openai_service = OpenAIService()

# Ensure upload directory exists
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)

def process_video_thread(file_id: str, configs: list):
    """Background thread to process video and generate reels"""
    try:
        # Get task data
        task_data = file_manager.get_task_data(file_id)
        if not task_data:
            print(f"Task data not found for file_id: {file_id}")
            return
        
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
                
                # Generate reel using QuickReel API
                reel_result = quickreel_api.create_reel(
                    video_url=f"http://localhost:5000/uploads/{task_data.get('filename', 'video.mp4')}",
                    duration=config.get('duration', 30),
                    caption=config.get('caption', ''),
                    platforms=config.get('platforms', ['instagram']),
                    webhook_url="http://localhost:5000/webhook"  # You'll need to implement this endpoint
                )
                
                if not reel_result.get('success'):
                    raise Exception(f"Reel generation failed: {reel_result.get('error', 'Unknown error')}")
                
                # Store project_id for status checking
                project_id = reel_result.get('project_id')
                if project_id:
                    task_data['project_id'] = project_id
                    file_manager.save_task_data(file_id, task_data)
                
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
        file_manager.save_task_data(file_id, task_data)
        
        # Update final status
        file_manager.update_task_status(file_id, 'completed', 100, 'All reels generated successfully!')
        
        print(f"Task completed for file_id: {file_id}")
        print(f"Generated {len(reels)} reels")
        
    except Exception as e:
        # Update status to error
        file_manager.update_task_status(file_id, 'error', 0, f'Error: {str(e)}')
        print(f"Error processing video: {str(e)}")

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload"""
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'message': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not file_manager.allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_path = UPLOAD_FOLDER / f"{file_id}_{filename}"
        
        # Save file
        file.save(file_path)
        
        # Get video info
        video_info = file_manager.get_video_info(str(file_path))
        
        # Create task entry
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

@app.route('/generate-reels', methods=['POST'])
def generate_reels():
    """Generate reels from uploaded video"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        configs = data.get('configs', [])
        
        if not file_id:
            return jsonify({'success': False, 'message': 'File ID required'}), 400
        
        task_data = file_manager.get_task_data(file_id)
        if not task_data:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        
        # Update task status
        task_data['status'] = 'processing'
        task_data['configs'] = configs
        task_data['reels'] = []
        file_manager.save_task_data(file_id, task_data)
        
        # Start background thread
        thread = threading.Thread(target=process_video_thread, args=(file_id, configs))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Reel generation started'
        })
        
    except Exception as e:
        app.logger.error(f"Generation error: {str(e)}")
        return jsonify({'success': False, 'message': f'Generation failed: {str(e)}'}), 500

@app.route('/status/<task_id>')
def check_status(task_id):
    """Check the status of a reel generation task"""
    try:
        # Get task info from file manager
        task_info = file_manager.get_task_data(task_id)
        
        if not task_info:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        # If task is still processing, check with QuickReel API
        if task_info.get('status') == 'processing':
            project_id = task_info.get('project_id')
            if project_id:
                status_result = quickreel_api.check_status(project_id)
                
                if status_result.get('success') and status_result.get('status') == 'completed':
                    # Update task with completed data
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
        
        # Return current task status
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

@app.route('/download/<file_id>/<reel_id>')
def download_reel(file_id, reel_id):
    """Download generated reel"""
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

@app.route('/static/reels/<path:filename>')
def serve_reel(filename):
    """Serve reel files"""
    return send_from_directory('static/reels', filename)

@app.route('/static/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    """Serve thumbnail files"""
    return send_from_directory('static/thumbnails', filename)

@app.route('/generate-transcript', methods=['POST'])
def generate_transcript():
    """Generate transcript from uploaded video"""
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
        
        # Generate transcript
        transcript_result = assemblyai_service.transcribe_video(video_path)
        
        if transcript_result.get('success'):
            # Save transcript to task data
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

@app.route('/generate-poster', methods=['POST'])
def generate_poster():
    """Generate poster from meeting transcript"""
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
        
        # Generate poster
        poster_result = openai_service.generate_poster_image(
            transcript_data.get('transcript', ''),
            meeting_details
        )
        
        if poster_result.get('success'):
            # Save poster data to task
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

@app.route('/generate-blog', methods=['POST'])
def generate_blog():
    """Generate blog article from meeting transcript"""
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
        
        # Generate blog article
        blog_result = openai_service.generate_blog_article(
            transcript_data.get('transcript', ''),
            meeting_details
        )
        
        if blog_result.get('success'):
            # Save blog data to task
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

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle QuickReel webhook callbacks"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        project_id = data.get('projectId')
        status = data.get('status')
        
        if not project_id:
            return jsonify({'success': False, 'error': 'No project ID'}), 400
        
        # Update task status in file manager
        if status == 'completed':
            outputs = data.get('outputs', [])
            if outputs:
                output = outputs[0]
                video_url = output.get('videoUrl')
                thumbnail_url = output.get('thumbnailUrl')
                
                # Update task with completed data
                task_info = file_manager.get_task_data(project_id)
                if task_info:
                    task_info.update({
                        'status': 'completed',
                        'video_url': video_url,
                        'thumbnail_url': thumbnail_url,
                        'completed_at': time.time()
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

@app.route('/static/posters/<path:filename>')
def serve_poster(filename):
    """Serve poster files"""
    return send_from_directory('static/posters', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 