# שלב 1: בניית React Frontend
FROM node:18-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend-simple/package*.json ./
RUN npm ci --only=production
COPY frontend-simple/ ./
RUN npm run build

# שלב 2: הרצת Python Backend
FROM python:3.11-slim
WORKDIR /app

# התקנת תלותיות מערכת
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# העתקת requirements והתקנת Python packages
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת קוד backend
COPY backend/ .

# העתקת React build
COPY --from=frontend-builder /app/frontend/build ./static

# יצירת מסד נתונים
RUN python -c "
from database import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
