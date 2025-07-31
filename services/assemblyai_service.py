import os
import time
import requests
from typing import Dict, Optional
from config import Config

class AssemblyAIService:
    def __init__(self):
        self.api_key = Config.ASSEMBLYAI_API_KEY
        self.base_url = "https://api.assemblyai.com/v2"
        
    def transcribe_video(self, video_path: str) -> Dict:
        """
        Transcribe video using AssemblyAI
        """
        if not self.api_key:
            return self._mock_transcribe(video_path)
            
        try:
            # Upload the video file
            upload_url = f"{self.base_url}/upload"
            headers = {"authorization": self.api_key}
            
            with open(video_path, "rb") as f:
                response = requests.post(upload_url, headers=headers, data=f)
                response.raise_for_status()
                upload_url = response.json()["upload_url"]
            
            # Start transcription
            transcript_url = f"{self.base_url}/transcript"
            transcript_request = {
                "audio_url": upload_url,
                "speaker_labels": True,
                "auto_chapters": True,
                "entity_detection": True,
                "auto_highlights": True
            }
            
            response = requests.post(transcript_url, json=transcript_request, headers=headers)
            response.raise_for_status()
            transcript_id = response.json()["id"]
            
            # Poll for completion
            polling_url = f"{self.base_url}/transcript/{transcript_id}"
            while True:
                polling_response = requests.get(polling_url, headers=headers)
                polling_response.raise_for_status()
                transcript = polling_response.json()
                
                if transcript["status"] == "completed":
                    return {
                        'success': True,
                        'transcript': transcript.get('text', ''),
                        'chapters': transcript.get('chapters', []),
                        'highlights': transcript.get('auto_highlights_result', {}),
                        'speakers': transcript.get('utterances', []),
                        'entities': transcript.get('entities', []),
                        'confidence': transcript.get('confidence', 0),
                        'audio_duration': transcript.get('audio_duration', 0)
                    }
                elif transcript["status"] == "error":
                    return {
                        'success': False,
                        'error': transcript.get('error', 'Transcription failed')
                    }
                
                time.sleep(3)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _mock_transcribe(self, video_path: str) -> Dict:
        """
        Mock transcription for testing without API key
        """
        print(f"Mock: Transcribing video {video_path}")
        time.sleep(2)  # Simulate processing time
        
        return {
            'success': True,
            'transcript': "This is a mock transcript of the meeting. We discussed quarterly results and future plans. The team presented their findings and we made important decisions about the upcoming projects.",
            'chapters': [
                {
                    'summary': 'Quarterly Results Discussion',
                    'headline': 'Q4 Performance Review',
                    'gist': 'Team discussed quarterly performance metrics'
                },
                {
                    'summary': 'Future Planning',
                    'headline': 'Strategic Planning Session',
                    'gist': 'Planned upcoming projects and initiatives'
                }
            ],
            'highlights': {
                'results': [
                    {'text': 'quarterly results', 'rank': 0.95},
                    {'text': 'future plans', 'rank': 0.88},
                    {'text': 'important decisions', 'rank': 0.92}
                ]
            },
            'speakers': [
                {'speaker': 'A', 'text': 'Welcome everyone to our quarterly meeting.'},
                {'speaker': 'B', 'text': 'Let me present the quarterly results.'},
                {'speaker': 'A', 'text': 'Excellent work team, let\'s discuss future plans.'}
            ],
            'entities': [
                {'text': 'quarterly results', 'entity_type': 'topic'},
                {'text': 'future plans', 'entity_type': 'topic'},
                {'text': 'team', 'entity_type': 'organization'}
            ],
            'confidence': 0.95,
            'audio_duration': 1800  # 30 minutes in seconds
        } 