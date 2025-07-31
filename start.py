#!/usr/bin/env python3
"""
SmartMeetingAI Startup Script
This script helps you start the application with proper checks.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'python-dotenv', 
        'requests', 'werkzeug'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                import dotenv
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def check_directories():
    """Check if required directories exist"""
    directories = ['uploads', 'static/reels', 'static/thumbnails']
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"❌ Directory missing: {directory}")
            return False
    
    print("✅ All directories exist")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'static/reels', 'static/thumbnails']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path('.env')
    if not env_file.exists():
        env_content = """# Flask Configuration
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True

# Pictory API (add when you get the key)
PICTORY_API_KEY=
PICTORY_API_URL=https://api.pictory.ai

# Storage Configuration
STORAGE_BACKEND=local
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file exists")

def start_application():
    """Start the application"""
    print("\n🚀 Starting SmartMeetingAI...")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_dependencies():
        return False
    
    if not check_directories():
        return False
    
    create_directories()
    create_env_file()
    
    print("\n📋 Setup complete! Now you can run the application:")
    print("\nTerminal - Flask Server:")
    print("  python app.py")
    print("\nThen open: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    print("🧠 SmartMeetingAI - Reel Maker Module")
    print("=" * 40)
    
    if start_application():
        print("\n✅ Ready to start! Follow the instructions above.")
    else:
        print("\n❌ Setup failed. Please fix the issues above.")
        sys.exit(1) 