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

# העתקת קבצי backend בלבד
COPY backend/ ./backend/
COPY config/ ./config/
COPY core/ ./core/
COPY db/ ./db/
COPY models/ ./models/
COPY server/ ./server/
COPY telegram_bot/ ./telegram_bot/
COPY scripts/ ./scripts/

# העתקת קבצים נחוצים מהשורש
COPY *.py ./
COPY *.txt ./
COPY *.md ./

# יצירת תיקיות נדרשות
RUN mkdir -p logs

EXPOSE 8000

# נקודת כניסה עם JSON format (לתיקון ה-warning)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
