FROM python:3.11-slim

WORKDIR /app

# התקנת תלות מערכת
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# העתקת דרישות ראשונות
COPY requirements.txt .

# התקנת תלות פייתון
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# העתקת שאר הקבצים
COPY . .

# יצירת תיקיות נדרשות
RUN mkdir -p logs

EXPOSE 8000

# הגדרת משתני סביבה ברירת מחדל
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# נקודת כניסה עם הרשאות והתחלה איטית
CMD ["sh", "-c", "echo '🚀 Starting PAIS API...' && \
     echo '📊 Environment variables:' && \
     echo 'PORT: $PORT' && \
     echo 'HOST: $HOST' && \
     echo '📁 Current directory:' && pwd && ls -la && \
     echo '🔧 Starting Uvicorn...' && \
     uvicorn backend.main:app --host \$HOST --port \$PORT --log-level debug"]
