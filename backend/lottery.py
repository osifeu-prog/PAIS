# Lottery Integration Module
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
import random
from collections import Counter

router = APIRouter(prefix="/api/v1/lottery", tags=["lottery"])

# נתוני לוטו לדוגמה
LOTTERY_DATA = [
    {"date": "2024-01-15", "numbers": [12, 24, 36, 48, 55], "special": 7},
    {"date": "2024-01-08", "numbers": [5, 17, 29, 42, 51], "special": 3},
    {"date": "2024-01-01", "numbers": [8, 19, 33, 47, 59], "special": 1}
]

class LotteryService:
    def __init__(self):
        self.history = LOTTERY_DATA
    
    def get_draws(self, count: int = 5):
        return self.history[:count]
    
    def analyze(self):
        all_numbers = []
        for draw in self.history:
            all_numbers.extend(draw["numbers"])
        
        freq = Counter(all_numbers)
        hot = [num for num, _ in freq.most_common(5)]
        cold = [num for num, _ in freq.most_common()[-5:]]
        
        return {
            "hot_numbers": hot,
            "cold_numbers": cold,
            "frequency": dict(freq)
        }
    
    def generate_prediction(self):
        analysis = self.analyze()
        prediction = random.sample(range(1, 61), 5)
        return {
            "numbers": sorted(prediction),
            "confidence": round(random.uniform(0.6, 0.9), 2),
            "timestamp": datetime.now().isoformat()
        }

service = LotteryService()

@router.get("/health")
async def health():
    return {
        "status": "active",
        "service": "lottery",
        "version": "1.0.0"
    }

@router.get("/draws")
async def get_draws(count: int = 3):
    return {"draws": service.get_draws(count), "total": len(service.history)}

@router.get("/analysis")
async def get_analysis():
    return {"analysis": service.analyze()}

@router.get("/prediction")
async def get_prediction():
    return {"prediction": service.generate_prediction()}

@router.post("/simulate")
async def simulate_bet(numbers: List[int], bet: float = 10):
    if len(numbers) != 5:
        raise HTTPException(400, "Need 5 numbers")
    
    winning = random.sample(range(1, 61), 5)
    matches = len(set(numbers) & set(winning))
    
    prize = 0
    if matches == 5:
        prize = bet * 1000
    elif matches == 4:
        prize = bet * 100
    elif matches == 3:
        prize = bet * 10
    
    return {
        "user_numbers": numbers,
        "winning_numbers": winning,
        "matches": matches,
        "bet": bet,
        "prize": prize,
        "won": prize > 0
    }
