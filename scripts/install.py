#!/usr/bin/env python3
"""
Installation script for Prediction Point System
"""
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
import yaml

def print_header():
    """Print installation header"""
    print("=" * 60)
    print("PREDICTION POINT SYSTEM - INSTALLATION")
    print("=" * 60)
    print()

def get_input(prompt, default=None, required=True):
    """Get user input with validation"""
    while True:
        if default:
            response = input(f"{prompt} [{default}]: ").strip()
            if not response:
                response = default
        else:
            response = input(f"{prompt}: ").strip()
        
        if not response and required:
            print("This field is required. Please try again.")
            continue
        
        return response

def create_project_structure(project_name):
    """Create project directory structure"""
    print(f"\n📁 Creating project structure for '{project_name}'...")
    
    # Define directory structure
    directories = [
        project_name,
        f"{project_name}/config",
        f"{project_name}/core",
        f"{project_name}/db",
        f"{project_name}/server",
        f"{project_name}/server/api",
        f"{project_name}/scripts",
        f"{project_name}/telegram_bot",
        f"{project_name}/frontend/src",
        f"{project_name}/frontend/public",
        f"{project_name}/logs",
        f"{project_name}/models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}")
    
    return project_name

def copy_config_files(project_path):
    """Copy configuration files"""
    print("\n⚙️  Creating configuration files...")
    
    config_files = [
        "settings.json",
        "scoring_rules.json", 
        "market_config.json"
    ]
    
    for config_file in config_files:
        # In a real installation, you would create these files
        # For now, we'll create placeholders
        config_path = Path(project_path) / "config" / config_file
        with open(config_path, 'w') as f:
            f.write(f'{{"note": "This is {config_file}. Edit with your settings."}}')
        print(f"  Created: config/{config_file}")
    
    return True

def create_docker_compose(project_path, webhook_url=None):
    """Create docker-compose.yml file"""
    print("\n🐳 Creating Docker configuration...")
    
    compose_content = f"""version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: prediction_db
      POSTGRES_USER: prediction_user
      POSTGRES_PASSWORD: prediction_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://prediction_user:prediction_pass@postgres:5432/prediction_db
      REDIS_URL: redis://redis:6379/0
      WEBHOOK_URL: "{webhook_url or 'https://your-webhook-url.com'}"
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs

  celery_worker:
    build: .
    command: celery -A server.celery_app worker --loglevel=info
    depends_on:
      - postgres
      - redis
      - api
    environment:
      DATABASE_URL: postgresql://prediction_user:prediction_pass@postgres:5432/prediction_db
      REDIS_URL: redis://redis:6379/0

  celery_beat:
    build: .
    command: celery -A server.celery_app beat --loglevel=info
    depends_on:
      - postgres
      - redis
      - api
    environment:
      DATABASE_URL: postgresql://prediction_user:prediction_pass@postgres:5432/prediction_db
      REDIS_URL: redis://redis:6379/0

  telegram_bot:
    build: .
    command: python telegram_bot/bot.py
    depends_on:
      - api
    environment:
      API_URL: http://api:8000
      TELEGRAM_BOT_TOKEN: ${{TELEGRAM_BOT_TOKEN:-your_bot_token_here}}
    volumes:
      - ./config:/app/config

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  postgres_data:
"""
    
    compose_path = Path(project_path) / "docker-compose.yml"
    with open(compose_path, 'w') as f:
        f.write(compose_content)
    
    print("  Created: docker-compose.yml")
    return True

def create_env_file(project_path, main_system_url=None):
    """Create .env file"""
    print("\n🔑 Creating environment file...")
    
    env_content = f"""# Database
DATABASE_URL=postgresql://prediction_user:prediction_pass@localhost:5432/prediction_db
REDIS_URL=redis://localhost:6379/0

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
SECRET_KEY=change-this-to-a-secret-key-in-production

# External Services
MAIN_SYSTEM_URL={main_system_url or 'https://your-main-system.com'}
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBHOOK_SECRET=your_webhook_secret_here

# Data Sources
PAIS_API_URL=https://api.pais.co.il/lottery/results
LOTTERY_API_URL=https://www.michlol.co.il/api/lottery
"""
    
    env_path = Path(project_path) / ".env"
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("  Created: .env")
    print("  ⚠️  Remember to update the secret keys in .env file!")
    return True

def create_requirements(project_path):
    """Create requirements.txt file"""
    print("\n📦 Creating Python requirements...")
    
    requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
celery==5.3.4
redis==5.0.1
requests==2.31.0
aiohttp==3.9.1
python-telegram-bot==20.6
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dateutil==2.8.2
pandas==2.1.4
numpy==1.26.2
scikit-learn==1.3.2
pyyaml==6.0.1
httpx==0.25.1
websockets==12.0
"""
    
    req_path = Path(project_path) / "requirements.txt"
    with open(req_path, 'w') as f:
        f.write(requirements)
    
    print("  Created: requirements.txt")
    return True

def create_readme(project_path, project_name):
    """Create README.md file"""
    print("\n📖 Creating README documentation...")
    
    readme_content = f"""# {project_name} - Prediction Point System

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for development)
- Node.js 18+ (for frontend development)

### Installation

1. **Clone and setup:**
```bash
cd {project_name}
python scripts/install.py
