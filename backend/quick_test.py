# =========================================
# 🧪 סקריפט בדיקות מהירות - Prediction Point System
# =========================================

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(name, endpoint, method="GET", data=None):
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        
        print(f"✅ {name}: {response.status_code}")
        if response.status_code == 200:
            try:
                return response.json()
            except:
                return response.text
        return None
    except Exception as e:
        print(f"❌ {name}: {e}")
        return None

print("🧪 מתחיל בדיקות API...")
print("=" * 50)

# 1. Health Check
health = test_endpoint("Health Check", "/health")
if health:
    print(f"   Status: {health.get('status', 'N/A')}")

# 2. API Test
test = test_endpoint("API Test", "/api/v1/test")

# 3. Users
users = test_endpoint("Users", "/api/v1/users")
if users and isinstance(users, list):
    print(f"   מספר משתמשים: {len(users)}")

# 4. Stats
stats = test_endpoint("System Stats", "/api/v1/stats")
if stats:
    print(f"   משתמשים: {stats.get('users_count', 0)}")
    print(f"   תחזיות: {stats.get('predictions_count', 0)}")
    print(f"   עסקאות: {stats.get('transactions_count', 0)}")

# 5. יצירת משתמש לדוגמה
test_user = {
    "username": f"tester_{__import__('time').time():.0f}",
    "email": f"test_{__import__('time').time():.0f}@test.com",
    "password": "test123"
}
new_user = test_endpoint("Create User", "/api/v1/users", "POST", test_user)

print("=" * 50)
print("🎉 בדיקות הושלמו!")
print("")
print("🌐 כתובות חשובות:")
print("   React App: http://localhost:3000")
print("   API Docs:  http://localhost:8000/docs")
print("   API Root:  http://localhost:8000/")
