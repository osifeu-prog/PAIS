FROM python:3.11-slim

WORKDIR /app

# העתקת כל הקבצים
COPY . .

# התקנת תלות מערכת
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# התקנת תלות פייתון
RUN pip install --no-cache-dir -r requirements.txt

# יצירת תיקיות נדרשות
RUN mkdir -p logs

EXPOSE 8000

# נקודת כניסה ברורה
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
