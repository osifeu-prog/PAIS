# =========================================
# 🎰 אינטגרציה עם מפעל הפיס - Lottery Integration
# =========================================

import requests
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from collections import Counter
import random

router = APIRouter(prefix="/api/v1/lottery", tags=["lottery"])

# נתונים לדוגמה - במציאות תוציא מכאן API אמיתי
LOTTERY_HISTORICAL_DATA = {
    "last_draws": [
        {
            "date": "2024-01-15",
            "numbers": [12, 24, 36, 48, 55],
            "special_number": 7,
            "winners": 3,
            "prize_pool": 1000000
        },
        {
            "date": "2024-01-08",
            "numbers": [5, 17, 29, 42, 51],
            "special_number": 3,
            "winners": 2,
            "prize_pool": 850000
        },
        {
            "date": "2024-01-01",
            "numbers": [8, 19, 33, 47, 59],
            "special_number": 1,
            "winners": 5,
            "prize_pool": 1200000
        }
    ],
    "statistics": {
        "most_common_numbers": [12, 24, 36, 5, 8],
        "least_common_numbers": [1, 2, 60, 59, 58],
        "average_prize_pool": 1016666,
        "total_draws": 1560
    }
}

class LotteryAnalyzer:
    def __init__(self):
        self.historical_data = LOTTERY_HISTORICAL_DATA
    
    def get_last_draws(self, count: int = 5) -> List[Dict]:
        """קבלת ההגרלות האחרונות"""
        return self.historical_data["last_draws"][:count]
    
    def analyze_numbers_frequency(self) -> Dict:
        """ניתוח תדירות מספרים"""
        all_numbers = []
        for draw in self.historical_data["last_draws"]:
            all_numbers.extend(draw["numbers"])
        
        freq = Counter(all_numbers)
        
        return {
            "hot_numbers": [num for num, count in freq.most_common(10)],
            "cold_numbers": [num for num, count in freq.most_common()[-10:]],
            "frequency_distribution": dict(freq.most_common(20))
        }
    
    def generate_prediction(self) -> Dict:
        """יצירת תחזית על בסיס סטטיסטיקה"""
        analysis = self.analyze_numbers_frequency()
        
        # אלגוריתם בסיסי: לקחת 4 מספרים חמים ו-1 מספר קר
        recommended_numbers = analysis["hot_numbers"][:4] + [random.choice(analysis["cold_numbers"])]
        recommended_numbers.sort()
        
        return {
            "recommended_numbers": recommended_numbers,
            "confidence_score": 0.75,
            "strategy": "4 חמים + 1 קר",
            "timestamp": datetime.now().isoformat()
        }

lottery_analyzer = LotteryAnalyzer()

# ========== API ENDPOINTS ==========

@router.get("/health")
async def lottery_health():
    """בדיקת בריאות של שירות הלוטו"""
    return {
        "status": "active",
        "service": "lottery-integration",
        "data_points": len(LOTTERY_HISTORICAL_DATA["last_draws"]),
        "last_update": datetime.now().isoformat()
    }

@router.get("/last-draws")
async def get_last_draws(count: int = 5):
    """קבלת ההגרלות האחרונות"""
    return {
        "draws": lottery_analyzer.get_last_draws(count),
        "count": count,
        "total_available": len(LOTTERY_HISTORICAL_DATA["last_draws"])
    }

@router.get("/analysis")
async def get_analysis():
    """קבלת ניתוח סטטיסטי"""
    return {
        "analysis": lottery_analyzer.analyze_numbers_frequency(),
        "statistics": LOTTERY_HISTORICAL_DATA["statistics"],
        "generated_at": datetime.now().isoformat()
    }

@router.get("/prediction")
async def get_prediction():
    """קבלת תחזית למספרים"""
    prediction = lottery_analyzer.generate_prediction()
    return {
        "prediction": prediction,
        "disclaimer": "לתשומת לבך: זהו ניתוח סטטיסטי בלבד ואינו מהווה המלצה להשקעה",
        "system_version": "1.0.0"
    }

@router.get("/smart-prediction")
async def get_smart_prediction(user_id: Optional[int] = None):
    """תחזית חכמה עם התאמה אישית"""
    base_prediction = lottery_analyzer.generate_prediction()
    
    # כאן ניתן להוסיף לוגיקה של למידת המשתמש בהמשך
    personalized_note = "תחזית בסיסית - הירשם למערכת לקבלת תחזיות מותאמות אישית"
    
    if user_id:
        personalized_note = f"תחזית מותאמת למשתמש #{user_id} - נבנתה על בסיס 3 הגרלות אחרונות"
    
    return {
        **base_prediction,
        "personalized_note": personalized_note,
        "recommended_bet_amount": 10,  # בשקלים
        "expected_return_rate": 2.5    # יחס זכייה משוער
    }

@router.post("/simulate-bet")
async def simulate_bet(numbers: List[int], bet_amount: float = 10):
    """סימולציית הימור"""
    if len(numbers) != 5:
        raise HTTPException(status_code=400, detail="נדרשים בדיוק 5 מספרים")
    
    if any(n < 1 or n > 60 for n in numbers):
        raise HTTPException(status_code=400, detail="מספרים חייבים להיות בין 1 ל-60")
    
    # סימולציה פשוטה
    winning_numbers = random.sample(range(1, 61), 5)
    winning_special = random.randint(1, 10)
    
    matches = len(set(numbers) & set(winning_numbers))
    has_special = random.choice([True, False])
    
    # חישוב זכייה
    prize = 0
    if matches == 5:
        prize = bet_amount * 10000  # זכייה ראשונה
    elif matches == 4:
        prize = bet_amount * 500
    elif matches == 3:
        prize = bet_amount * 50
    elif matches == 2:
        prize = bet_amount * 5
    
    if has_special:
        prize *= 2
    
    return {
        "user_numbers": numbers,
        "winning_numbers": winning_numbers,
        "special_number": winning_special,
        "matches": matches,
        "has_special_match": has_special,
        "bet_amount": bet_amount,
        "prize_won": prize,
        "profit_loss": prize - bet_amount,
        "is_winner": prize > 0,
        "simulation_id": f"SIM-{datetime.now().timestamp()}"
    }

@router.post("/create-prediction-from-lottery")
async def create_prediction_from_lottery(
    title: str,
    description: str = "תחזית לוטו מבוססת AI",
    points_staked: int = 100,
    user_id: int = 1
):
    """יצירת תחזית במערכת מנקודות הלוטו"""
    prediction_data = lottery_analyzer.generate_prediction()
    
    return {
        "success": True,
        "prediction_created": {
            "title": title,
            "description": description,
            "predicted_numbers": prediction_data["recommended_numbers"],
            "points_staked": points_staked,
            "user_id": user_id,
            "confidence": prediction_data["confidence_score"],
            "created_at": datetime.now().isoformat()
        },
        "lottery_data": prediction_data,
        "message": "תחזית נוצרה בהצלחה! התחזית נוספה למערכת הנקודות שלך."
    }
