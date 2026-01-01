FROM python:3.11-slim

WORKDIR /app

# התקנת תלות מערכת
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# העתקת והתקנת תלותיות פייתון
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY config/ ./config/
COPY core/ ./core/
COPY db/ ./db/
COPY models/ ./models/
COPY server/ ./server/
COPY scripts/ ./scripts/
COPY telegram_bot/ ./telegram_bot/
# העתקת קבצי Python בודדים שנמצאים בנתיב השורש (אם יש)
COPY *.py ./

# יצירת תיקיות נדרשות
RUN mkdir -p logs

EXPOSE 8000

# הרצת האפליקציה
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
