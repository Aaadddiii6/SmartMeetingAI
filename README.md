# SmartMeetingAI - Reel Maker Module

Transform your meeting videos into engaging reels using AI-powered video processing.

## 🚀 Features

- **Video Upload**: Support for multiple video formats (MP4, AVI, MOV, MKV, WMV, FLV, WEBM)
- **AI-Powered Processing**: Automatic highlight detection and reel generation
- **Customizable Reels**: Choose duration (15s, 30s, 45s, 60s) and style
- **Real-time Progress**: Live status updates during processing
- **Download & Preview**: View and download generated reels
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

- **Backend**: Flask (Python)
- **Task Queue**: Celery + Redis
- **Video Processing**: Pictory API (AI-powered)
- **Storage**: Local file system (expandable to cloud)
- **Frontend**: HTML/CSS/JavaScript (Vanilla)

## 📁 Project Structure

```
/smartmeetingai/
├── app.py                 # Flask application & routes
├── celery_worker.py       # Background task processing
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .env                 # Environment variables (create this)
├── /static             # Static files (CSS, JS, reels)
│   ├── css/style.css
│   ├── js/app.js
│   └── reels/          # Generated reels storage
├── /templates          # HTML templates
│   └── index.html
├── /uploads            # Uploaded videos storage
├── /services           # Business logic services
│   ├── __init__.py
│   ├── file_manager.py # File operations & metadata
│   └── pictory_api.py  # Pictory API integration
└── tasks.json          # Task tracking data
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- Redis server
- Pictory API key (optional for testing)

### 1. Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd SmartMeetingAI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Pictory API (add when you get the key)
PICTORY_API_KEY=your-pictory-api-key
PICTORY_API_URL=https://api.pictory.ai

# Storage Configuration
STORAGE_BACKEND=local
```

### 3. Start Redis

```bash
# Windows (if using WSL or Docker)
redis-server

# macOS (using Homebrew)
brew services start redis

# Linux
sudo systemctl start redis
```

### 4. Run the Application

Open **three terminal windows** and run these commands:

**Terminal 1 - Flask Server:**

```bash
python app.py
```

**Terminal 2 - Celery Worker:**

```bash
celery -A celery_worker.celery worker --loglevel=info
```

**Terminal 3 - Celery Beat (optional, for scheduled tasks):**

```bash
celery -A celery_worker.celery beat --loglevel=info
```

### 5. Access the Application

Open your browser and go to: `http://localhost:5000`

## 🎯 Usage Guide

### 1. Upload Video

- Click "Choose Video File" or drag & drop
- Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM
- Maximum file size: 500MB

### 2. Configure Reel Settings

- **Duration**: 15, 30, 45, or 60 seconds
- **Style**: Professional, Casual, Energetic, Calm, Modern, Classic

### 3. Generate Reel

- Click "Generate Reel"
- Watch real-time progress updates
- Processing typically takes 2-5 minutes

### 4. Download & Share

- Preview the generated reel
- Download to your device
- Generate additional reels from the same video

## 🔧 API Endpoints

| Method | Endpoint            | Description               |
| ------ | ------------------- | ------------------------- |
| `GET`  | `/`                 | Homepage with upload form |
| `POST` | `/upload`           | Upload video file         |
| `POST` | `/generate-reel`    | Start reel generation     |
| `GET`  | `/status/<file_id>` | Check processing status   |
| `GET`  | `/video/<file_id>`  | Serve uploaded video      |
| `GET`  | `/reel/<file_id>`   | Serve generated reel      |
| `GET`  | `/tasks`            | List all tasks (debug)    |

## 🧪 Testing Without Pictory API

The application includes a **mock mode** that works without the Pictory API key:

- Upload any video file
- Processing will simulate with mock data
- Generated "reels" will be dummy files
- Perfect for testing the UI and workflow

## 🔄 Development Workflow

### Adding Real Pictory API Integration

When you get your Pictory API key:

1. Add the key to your `.env` file
2. The application will automatically switch from mock to real API
3. No code changes needed - it's already implemented!

### Customizing Styles and Durations

Edit `services/pictory_api.py`:

```python
def get_available_styles(self) -> list:
    return ["professional", "casual", "energetic", "calm", "modern", "classic"]

def get_duration_options(self) -> list:
    return [15, 30, 45, 60]
```

## 🚀 Deployment

### Local Development

- Use the setup instructions above
- Redis must be running
- All files stored locally

### Production Deployment

- Use a production WSGI server (Gunicorn)
- Set up Redis on a separate server
- Configure cloud storage (Supabase/Google Drive)
- Set `DEBUG=False` in environment

## 🐛 Troubleshooting

### Common Issues

**Redis Connection Error:**

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

**Celery Worker Not Starting:**

```bash
# Make sure you're in the project directory
# Check if Redis is accessible
celery -A celery_worker.celery inspect active
```

**File Upload Fails:**

- Check file size (max 500MB)
- Verify file format is supported
- Ensure `/uploads` directory exists

**Processing Stuck:**

- Check Celery worker logs
- Verify Redis connection
- Restart Celery worker if needed

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:

- Check the troubleshooting section
- Review the logs in terminal windows
- Create an issue in the repository

---

**Note**: This is a development version. The Pictory API integration will be fully functional once you receive your API key.
