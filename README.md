# SmartMeetingAI - Module (X) Routes

A comprehensive AI-powered meeting analysis and content generation platform that transforms meeting videos into reels, transcripts, posters, and blog articles.

## 🚀 Features

- **Video Upload & Processing**: Upload meeting videos and process them for content generation
- **AI-Powered Transcript Generation**: Convert speech to text using AssemblyAI
- **Smart Reel Creation**: Generate engaging social media reels using QuickReel API
- **Professional Poster Generation**: Create meeting posters using multiple AI services (OpenAI, Stability AI, RunwayML)
- **Blog Article Generation**: Transform meeting content into comprehensive blog articles
- **Multi-Platform Support**: Generate content optimized for Instagram, TikTok, YouTube, and Facebook

## 📁 Project Structure

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
├── API_DOCUMENTATION.md        # Comprehensive API documentation
└── .gitignore                  # Git ignore rules
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/module-2-routes.git
   cd module-2-routes
   ```

2. **Set up the backend**

   ```bash
   cd backend

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the `backend/` directory with your API keys:

   ```env
   # Flask Configuration
   SECRET_KEY=your_secret_key_here
   DEBUG=True

   # API Keys (get these from respective services)
   QUICKREEL_API_KEY=your_quickreel_api_key_here
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   RUNWAYML_API_KEY=your_runwayml_api_key_here
   STABILITYAI_API_KEY=your_stabilityai_api_key_here

   # Additional configuration
   UPLOAD_FOLDER=uploads
   MAX_CONTENT_LENGTH=524288000
   ```

4. **Run the application**

   ```bash
   # From the backend directory
   python main.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - The API will be available at `http://localhost:5000/api/`

## 🔑 Required API Keys

You'll need to obtain API keys from the following services:

### Essential APIs

- **AssemblyAI**: For transcript generation
- **OpenAI**: For blog and poster generation
- **QuickReel**: For reel generation

### Optional APIs (for enhanced features)

- **Stability AI**: For better poster generation (recommended over DALL-E)
- **RunwayML**: For alternative poster generation
- **Canva API**: For template-based poster generation

## 📚 API Documentation

For detailed API documentation, including all endpoints, input/output types, and examples, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## 🧪 Testing

### Running Tests

```bash
cd backend
python -m pytest tests/
```

### Test Coverage

```bash
python -m pytest --cov=utils tests/
```

## 🚀 Usage

### 1. Upload a Meeting Video

- Use the web interface or make a POST request to `/api/upload`
- Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM
- Maximum file size: 500MB

### 2. Generate Transcript

- Make a POST request to `/api/generate-transcript` with the file_id
- Get detailed transcript with timestamps and confidence scores

### 3. Generate Reels

- Make a POST request to `/api/generate-reels` with reel configurations
- Choose duration, platforms, and styling options
- Monitor progress with `/api/status/<task_id>`

### 4. Generate Posters

- Make a POST request to `/api/generate-poster`
- Automatically uses the best available AI service
- Supports multiple AI providers for optimal results

### 5. Generate Blog Articles

- Make a POST request to `/api/generate-blog`
- Creates comprehensive, professional blog articles
- Includes industry insights and strategic analysis

## 🔧 Development

### Adding New Features

1. Create new utility files in `backend/utils/`
2. Add corresponding API endpoints in `backend/main.py`
3. Write unit tests for new functionality
4. Update API documentation

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all functions
- Include input/output type documentation

### Testing Requirements

- All utility functions must have unit tests
- Test files should be placed in `backend/tests/`
- Maintain at least 80% code coverage

## 🏗️ Architecture

### Backend Architecture

- **Flask**: Web framework for API endpoints
- **Modular Design**: Clean separation of concerns with utility modules
- **Background Processing**: Threading for long-running tasks
- **File-based Storage**: JSON files for task data (can be upgraded to database)

### Service Integration

- **AssemblyAI**: Speech-to-text transcription
- **OpenAI**: Content generation and image creation
- **QuickReel**: Video reel generation
- **Multiple AI Services**: Fallback options for poster generation

## 🔒 Security

- API keys are stored in environment variables (never committed to Git)
- File upload validation and sanitization
- Input validation on all API endpoints
- Error messages don't expose sensitive information

## 📈 Performance

- Background processing for long-running tasks
- Threading for concurrent operations
- Efficient file handling and storage
- Graceful handling of API rate limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write unit tests for all new functionality
- Update API documentation for new endpoints
- Follow the existing code structure and patterns
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Check the [API Documentation](API_DOCUMENTATION.md)
- Review existing issues on GitHub
- Create a new issue with detailed information

## 🔮 Future Roadmap

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] Real-time WebSocket updates
- [ ] Mobile application
- [ ] Advanced analytics and reporting
- [ ] Integration with more AI services
- [ ] Cloud storage integration
- [ ] Advanced video processing features

---

**Note**: This project is designed for educational and professional use. Ensure you comply with all API service terms and conditions when using this application.
