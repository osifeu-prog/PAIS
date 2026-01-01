# קובץ לבדיקות API - הרץ עם: python test_data.py
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_all_endpoints():
    print("🧪 מתחיל בדיקות API...")
    
    # 1. בדיקת health
    print("1. בדיקת health...")
    try:
        resp = requests.get("http://localhost:8000/health")
        print(f"   ✅ Health: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"   ❌ Health failed: {e}")
    
    # 2. קבלת משתמשים
    print("2. קבלת משתמשים...")
    try:
        resp = requests.get(f"{BASE_URL}/users")
        users = resp.json()
        print(f"   ✅ {len(users)} משתמשים נמצאו")
    except Exception as e:
        print(f"   ❌ Get users failed: {e}")
    
    # 3. יצירת משתמש חדש
    print("3. יצירת משתמש חדש...")
    try:
        user_data = {
            "username": f"test_user_{int(time.time())}",
            "email": f"test{int(time.time())}@example.com",
            "password": "test123"
        }
        resp = requests.post(f"{BASE_URL}/users", json=user_data)
        print(f"   ✅ משתמש נוצר: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Create user failed: {e}")
    
    # 4. קבלת סטטיסטיקות
    print("4. קבלת סטטיסטיקות...")
    try:
        resp = requests.get(f"{BASE_URL}/stats")
        stats = resp.json()
        print(f"   ✅ סטטיסטיקות: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"   ❌ Get stats failed: {e}")
    
    print("🎉 בדיקות הושלמו!")

if __name__ == "__main__":
    test_all_endpoints()
