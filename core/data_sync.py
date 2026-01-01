import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncpg
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSync:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.pais_url = settings.DATA_SOURCES["pais"]
        self.lottery_api = settings.DATA_SOURCES["lottery_api"]
    
    async def fetch_lottery_results(self, days_back: int = 30) -> List[Dict]:
        """Fetch lottery results from external APIs"""
        results = []
        
        try:
            # Try main API first
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.pais_url}/last/{days_back}") as response:
                    if response.status == 200:
                        data = await response.json()
                        results.extend(self._parse_pais_results(data))
                    else:
                        logger.warning(f"Pais API failed: {response.status}")
                        
                # Fallback to secondary API
                async with session.get(self.lottery_api) as response:
                    if response.status == 200:
                        data = await response.json()
                        results.extend(self._parse_lottery_api_results(data))
                        
        except Exception as e:
            logger.error(f"Error fetching lottery results: {e}")
            
        return results
    
    def _parse_pais_results(self, data: Dict) -> List[Dict]:
        """Parse results from Pais API"""
        parsed_results = []
        
        for result in data.get("results", []):
            parsed_results.append({
                "lottery_type": result.get("type", "lotto"),
                "draw_date": datetime.strptime(result["date"], "%Y-%m-%d").date(),
                "winning_numbers": result["numbers"],
                "bonus_numbers": result.get("bonus", []),
                "prize_pool": result.get("prize", 0),
                "source": "pais"
            })
        
        return parsed_results
    
    def _parse_lottery_api_results(self, data: Dict) -> List[Dict]:
        """Parse results from lottery API"""
        parsed_results = []
        
        for result in data.get("draws", []):
            parsed_results.append({
                "lottery_type": result.get("game", "lotto"),
                "draw_date": datetime.strptime(result["date"], "%d/%m/%Y").date(),
                "winning_numbers": result["mainNumbers"],
                "bonus_numbers": result.get("extraNumbers", []),
                "prize_pool": result.get("jackpot", 0),
                "source": "lottery_api"
            })
        
        return parsed_results
    
    async def sync_results_to_db(self, results: List[Dict]):
        """Sync fetched results to database"""
        if not results:
            return
            
        async with self.db_pool.acquire() as conn:
            for result in results:
                # Check if result already exists
                exists = await conn.fetchval("""
                    SELECT 1 FROM lottery_results 
                    WHERE lottery_type = $1 AND draw_date = $2
                """, result["lottery_type"], result["draw_date"])
                
                if not exists:
                    await conn.execute("""
                        INSERT INTO lottery_results 
                        (lottery_type, draw_date, winning_numbers, bonus_numbers, prize_pool, source)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """, 
                    result["lottery_type"], result["draw_date"], 
                    json.dumps(result["winning_numbers"]),
                    json.dumps(result["bonus_numbers"]),
                    result["prize_pool"], result["source"])
                    
                    logger.info(f"Synced result for {result['draw_date']}")
    
    async def update_user_predictions(self):
        """Update user predictions with actual results"""
        async with self.db_pool.acquire() as conn:
            # Get predictions without results
            predictions = await conn.fetch("""
                SELECT p.*, lr.winning_numbers
                FROM predictions p
                LEFT JOIN lottery_results lr ON p.lottery_date = lr.draw_date 
                    AND p.lottery_type = lr.lottery_type
                WHERE p.actual_numbers IS NULL 
                    AND lr.winning_numbers IS NOT NULL
            """)
            
            for pred in predictions:
                predicted = pred["prediction_numbers"]
                actual = pred["winning_numbers"]
                
                # Calculate accuracy
                matches = len(set(predicted) & set(actual))
                total = len(actual)
                accuracy = (matches / total) * 100 if total > 0 else 0
                
                # Award points based on accuracy
                points = 0
                is_correct = accuracy >= 50  # Threshold for correct prediction
                
                if is_correct:
                    base_points = settings.POINTS["prediction_reward"]
                    multiplier = settings.POINTS["winning_multiplier"]
                    points = base_points * multiplier
                    
                    # Add accuracy bonus
                    if accuracy > 80:
                        points *= 1.5
                    elif accuracy > 60:
                        points *= 1.2
                
                # Update prediction
                await conn.execute("""
                    UPDATE predictions 
                    SET actual_numbers = $1, 
                        accuracy = $2, 
                        is_correct = $3,
                        points_awarded = $4
                    WHERE id = $5
                """, json.dumps(actual), accuracy, is_correct, points, pred["id"])
                
                # Update user's points if they earned any
                if points > 0:
                    await conn.execute("""
                        UPDATE wallets 
                        SET points_balance = points_balance + $1,
                            total_earned = total_earned + $1
                        WHERE user_id = $2
                    """, points, pred["user_id"])
                    
                    # Log the transaction
                    await conn.execute("""
                        INSERT INTO ledger 
                        (user_id, transaction_type, amount, description)
                        VALUES ($1, $2, $3, $4)
                    """, pred["user_id"], "prediction_reward", points, 
                       f"Prediction reward {accuracy:.1f}% accuracy")
