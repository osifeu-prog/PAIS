# ========================
# Dockerfile אוניברסלי ל-FastAPI
# ========================
FROM python:3.11-slim

WORKDIR /app

# 1. עדכן והתקן תלותיות מערכת
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 2. העתק והתקן תלותיות פייתון
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. העתק את כל קוד המקור
#    .dockerignore ימנע קבצים לא נחוצים
COPY . .

# 4. הפוך את backend לתיקיית עבודה
WORKDIR /app/backend

# 5. הרץ את האפליקציה
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
