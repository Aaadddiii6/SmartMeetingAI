# SmartMeetingAI API Documentation

## Project Structure

```
Module_(X)_Routes/
├── backend/
│   ├── .env                    # Environment variables (NEVER commit)
│   ├── db.py                   # Database connection handler
│   ├── main.py                 # Main Flask application with API routes
│   ├── requirements.txt        # Python dependencies
│   └── utils/                  # Business logic and helper functions
│       ├── file_manager.py     # File handling utilities
│       ├── video_processor.py  # Video processing logic
│       ├── transcript_service.py # Transcript generation
│       ├── poster_service.py   # Poster generation
│       ├── blog_service.py     # Blog article generation
│       ├── reel_service.py     # Reel generation
│       ├── openai_service.py   # OpenAI API integration
│       ├── assemblyai_service.py # AssemblyAI API integration
│       ├── quickreel_api.py    # QuickReel API integration
│       └── runwayml_service.py # RunwayML API integration
├── frontend/                   # Frontend files (HTML, CSS, JS)
└── .gitignore                  # Git ignore rules
```

## API Keys Required

### Required API Keys (add to backend/.env):

```env
# Flask Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=524288000
ALLOWED_EXTENSIONS=mp4,avi,mov,mkv,wmv,flv,webm

# API Keys
QUICKREEL_API_KEY=your_quickreel_api_key_here
QUICKREEL_API_URL=https://mango.quickreel.io/api/v2

# AssemblyAI for transcript generation
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# OpenAI for blog and poster generation
OPENAI_API_KEY=your_openai_api_key_here

# RunwayML for enhanced poster generation
RUNWAYML_API_KEY=your_runwayml_api_key_here
RUNWAYML_API_URL=https://api.runwayml.com/v1

# Stability AI for better poster generation
STABILITYAI_API_KEY=your_stabilityai_api_key_here

# Canva API for template-based poster generation
CANVA_API_KEY=your_canva_api_key_here
CANVA_API_URL=https://api.canva.com/v1

# Instagram API (for later)
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id_here
FACEBOOK_PAGE_ID=your_facebook_page_id_here

# Database Configuration (if needed later)
DATABASE_URL=your_database_url_here

# Storage Configuration
STORAGE_BACKEND=local

# Processing Configuration
MAX_VIDEO_DURATION=7200
THREAD_POOL_SIZE=4
```

## API Endpoints

### 1. Upload Video

**Endpoint:** `POST /api/upload`

**Input:**

- Content-Type: `multipart/form-data`
- Body: Form data with 'video' file

**Output:**

```json
{
  "success": true,
  "file_id": "uuid-string",
  "message": "Video uploaded successfully"
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Error description"
}
```

### 2. Generate Reels

**Endpoint:** `POST /api/generate-reels`

**Input:**

```json
{
  "file_id": "uuid-string",
  "configs": [
    {
      "duration": 30,
      "caption": "Meeting highlights",
      "platforms": ["instagram", "tiktok"],
      "style": "professional"
    }
  ]
}
```

**Output:**

```json
{
  "success": true,
  "message": "Reel generation started"
}
```

### 3. Check Status

**Endpoint:** `GET /api/status/<task_id>`

**Input:**

- URL Parameter: `task_id` (string)

**Output:**

```json
{
  "success": true,
  "status": "completed|processing|failed",
  "video_url": "https://example.com/video.mp4",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "error": null
}
```

### 4. Generate Transcript

**Endpoint:** `POST /api/generate-transcript`

**Input:**

```json
{
  "file_id": "uuid-string"
}
```

**Output:**

```json
{
  "success": true,
  "transcript": {
    "transcript": "Meeting transcript text...",
    "audio_duration": 1800,
    "confidence": 0.95,
    "words": [...],
    "generated_at": 1234567890
  },
  "message": "Transcript generated successfully"
}
```

### 5. Generate Poster

**Endpoint:** `POST /api/generate-poster`

**Input:**

```json
{
  "file_id": "uuid-string"
}
```

**Output:**

```json
{
  "success": true,
  "poster": {
    "image_url": "/static/posters/poster_123.png",
    "prompt": "Generated prompt text",
    "service": "openai|runwayml|stability",
    "generated_at": 1234567890
  },
  "message": "Poster generated successfully"
}
```

### 6. Generate Blog

**Endpoint:** `POST /api/generate-blog`

**Input:**

```json
{
  "file_id": "uuid-string"
}
```

**Output:**

```json
{
  "success": true,
  "blog": {
    "blog_content": "Generated blog article...",
    "word_count": 1500,
    "service": "openai",
    "generated_at": 1234567890
  },
  "message": "Blog article generated successfully"
}
```

### 7. Download Reel

**Endpoint:** `GET /api/download/<file_id>/<reel_id>`

**Input:**

- URL Parameters: `file_id` (string), `reel_id` (string)

**Output:**

- File download (video file)

### 8. Webhook

**Endpoint:** `POST /api/webhook`

**Input:**

```json
{
  "projectId": "project-uuid",
  "status": "completed|failed",
  "outputs": [
    {
      "videoUrl": "https://example.com/video.mp4",
      "thumbnailUrl": "https://example.com/thumbnail.jpg"
    }
  ],
  "error": "Error message if failed"
}
```

**Output:**

```json
{
  "success": true
}
```

## Utility Functions

### FileManager

**Location:** `backend/utils/file_manager.py`

**Key Methods:**

- `allowed_file(filename: str) -> bool`
- `get_video_info(file_path: str) -> Dict`
- `save_task_data(file_id: str, data: Dict) -> None`
- `get_task_data(file_id: str) -> Dict`
- `update_task_status(file_id: str, status: str, progress: int, message: str) -> None`

### VideoProcessor

**Location:** `backend/utils/video_processor.py`

**Key Methods:**

- `process_video_thread(file_id: str, configs: List[Dict]) -> None`
- `get_video_info(file_path: str) -> Dict`

### TranscriptService

**Location:** `backend/utils/transcript_service.py`

**Key Methods:**

- `generate_transcript(video_path: str) -> Dict`
- `extract_meeting_info(transcript: str) -> Dict`

### PosterService

**Location:** `backend/utils/poster_service.py`

**Key Methods:**

- `generate_poster_image(transcript: str, meeting_details: Dict) -> Dict`
- `generate_poster_with_service(transcript: str, meeting_details: Dict, service: str) -> Dict`
- `extract_meeting_info_for_poster(transcript: str) -> Dict`

### BlogService

**Location:** `backend/utils/blog_service.py`

**Key Methods:**

- `generate_blog_article(transcript: str, meeting_details: Dict) -> Dict`
- `generate_blog_summary(transcript: str, meeting_details: Dict) -> Dict`
- `extract_key_points(transcript: str) -> Dict`

### ReelService

**Location:** `backend/utils/reel_service.py`

**Key Methods:**

- `create_reel(video_url: str, duration: int, caption: str, platforms: List[str], webhook_url: str) -> Dict`
- `check_status(project_id: str) -> Dict`
- `get_reel_configurations() -> Dict`
- `validate_reel_config(config: Dict) -> Dict`

## Data Types

### Task Data Structure

```json
{
  "filename": "meeting_video.mp4",
  "file_path": "uploads/uuid_meeting_video.mp4",
  "status": "uploaded|processing|completed|failed",
  "created_at": "2024-01-01T12:00:00",
  "video_info": {
    "duration": 1800,
    "resolution": "1920x1080",
    "format": "mp4",
    "size": 52428800
  },
  "reels": [
    {
      "id": "reel_uuid_1",
      "duration": 30,
      "style": "professional",
      "caption": "Meeting highlights",
      "platforms": ["instagram"],
      "url": "https://example.com/video.mp4",
      "thumbnail": "https://example.com/thumbnail.jpg",
      "file_path": "https://example.com/video.mp4",
      "status": "completed",
      "progress": 100,
      "message": "Reel generated successfully"
    }
  ],
  "transcript": {
    "transcript": "Meeting transcript text...",
    "audio_duration": 1800,
    "confidence": 0.95,
    "words": [...],
    "generated_at": 1234567890
  },
  "poster": {
    "image_url": "/static/posters/poster_123.png",
    "prompt": "Generated prompt text",
    "service": "openai",
    "generated_at": 1234567890
  },
  "blog": {
    "blog_content": "Generated blog article...",
    "word_count": 1500,
    "service": "openai",
    "generated_at": 1234567890
  }
}
```

### Reel Configuration

```json
{
  "duration": 30,
  "caption": "Meeting highlights and key insights",
  "platforms": ["instagram", "tiktok"],
  "style": "professional"
}
```

### Meeting Details

```json
{
  "title": "Q4 Strategy Meeting",
  "date": "2024-01-01T12:00:00",
  "duration": 1800
}
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Descriptive error message",
  "error": "Technical error details (optional)"
}
```

Common HTTP Status Codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (file/task not found)
- `500`: Internal Server Error

## Testing

### Unit Tests

All utility functions should have unit tests. Test files should be placed in:

- `backend/tests/` directory
- Follow naming convention: `test_<module_name>.py`

### Running Tests

```bash
cd backend
python -m pytest tests/
```

### Test Coverage

```bash
python -m pytest --cov=utils tests/
```

## Deployment

### Development

```bash
cd backend
python main.py
```

### Production

```bash
cd backend
export FLASK_ENV=production
python main.py
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **File Uploads**: Validate file types and sizes
3. **Input Validation**: Validate all user inputs
4. **Error Messages**: Don't expose sensitive information in error messages
5. **Rate Limiting**: Implement rate limiting for API endpoints
6. **CORS**: Configure CORS properly for frontend integration

## Performance Considerations

1. **Background Processing**: Use threading for long-running tasks
2. **File Storage**: Consider cloud storage for production
3. **Caching**: Implement caching for frequently accessed data
4. **Database**: Use proper indexing for database queries
5. **API Limits**: Handle API rate limits gracefully

## Monitoring and Logging

1. **Application Logs**: Log all API requests and errors
2. **Performance Metrics**: Monitor response times and resource usage
3. **Error Tracking**: Implement error tracking and alerting
4. **Health Checks**: Implement health check endpoints

## Future Enhancements

1. **Database Integration**: Replace file-based storage with proper database
2. **User Authentication**: Add user authentication and authorization
3. **Real-time Updates**: Implement WebSocket for real-time status updates
4. **Advanced AI**: Integrate more AI services for enhanced features
5. **Mobile App**: Develop mobile application
6. **Analytics**: Add analytics and reporting features
