import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionEngine:
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = "models/prediction_model.pkl"
        self.load_or_train_model()
    
    def load_or_train_model(self):
        """Load existing model or train new one"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info("Loaded existing prediction model")
            except:
                logger.warning("Could not load model, will train new one")
                self.train_model()
        else:
            self.train_model()
    
    async def get_historical_data(self, lottery_type: str = "lotto", limit: int = 1000):
        """Get historical lottery data for analysis"""
        async with self.db_pool.acquire() as conn:
            results = await conn.fetch("""
                SELECT winning_numbers, draw_date, prize_pool
                FROM lottery_results 
                WHERE lottery_type = $1
                ORDER BY draw_date DESC
                LIMIT $2
            """, lottery_type, limit)
            
            return results
    
    def analyze_frequency(self, results: List) -> Dict:
        """Analyze number frequency from historical data"""
        all_numbers = []
        
        for result in results:
            numbers = json.loads(result["winning_numbers"])
            all_numbers.extend(numbers)
        
        # Calculate frequency
        unique, counts = np.unique(all_numbers, return_counts=True)
        frequency_dict = dict(zip(unique, counts))
        
        # Sort by frequency (hot numbers)
        hot_numbers = sorted(frequency_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Cold numbers (least frequent)
        cold_numbers = sorted(frequency_dict.items(), key=lambda x: x[1])[:10]
        
        # Calculate probabilities
        total_draws = len(results)
        probabilities = {num: count/total_draws for num, count in frequency_dict.items()}
        
        return {
            "hot_numbers": [num for num, _ in hot_numbers],
            "cold_numbers": [num for num, _ in cold_numbers],
            "probabilities": probabilities,
            "total_analyzed": total_draws
        }
    
    def train_model(self):
        """Train machine learning model for predictions"""
        # This is a simplified example - in production, you'd use more features
        logger.info("Training new prediction model...")
        
        # Create dummy data for example
        # In reality, you'd use actual historical data with features
        X = np.random.rand(100, 10)  # 100 samples, 10 features
        y = np.random.randint(1, 50, 100)  # Target numbers 1-49
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # Save model
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info("Model trained and saved")
    
    async def generate_predictions(self, user_id: int, lottery_type: str = "lotto", 
                                  count: int = 6) -> List[int]:
        """Generate lottery number predictions for a user"""
        
        # Get user's prediction history
        async with self.db_pool.acquire() as conn:
            user_history = await conn.fetch("""
                SELECT prediction_numbers, accuracy, is_correct
                FROM predictions 
                WHERE user_id = $1 AND lottery_type = $2
                ORDER BY created_at DESC
                LIMIT 100
            """, user_id, lottery_type)
        
        # Get historical data
        historical_data = await self.get_historical_data(lottery_type)
        analysis = self.analyze_frequency(historical_data)
        
        # Strategy 1: Use hot numbers
        hot_prediction = analysis["hot_numbers"][:count]
        
        # Strategy 2: Balanced approach (mix of hot and random)
        balanced_prediction = []
        hot_count = count // 2
        balanced_prediction.extend(analysis["hot_numbers"][:hot_count])
        
        # Add some random but less cold numbers
        available_numbers = list(range(1, 50))
        cold_set = set(analysis["cold_numbers"])
        available_numbers = [n for n in available_numbers if n not in cold_set]
        
        remaining = count - hot_count
        if available_numbers and len(available_numbers) >= remaining:
            random_numbers = np.random.choice(available_numbers, remaining, replace=False)
            balanced_prediction.extend(random_numbers.tolist())
        
        # Strategy 3: Personal pattern (if user has history)
        personal_prediction = None
        if user_history:
            # Analyze user's successful patterns
            successful = [h for h in user_history if h["is_correct"]]
            if successful:
                # Extract numbers from successful predictions
                personal_numbers = []
                for pred in successful:
                    numbers = json.loads(pred["prediction_numbers"])
                    personal_numbers.extend(numbers)
                
                # Get most common numbers in user's successful predictions
                if personal_numbers:
                    unique, counts = np.unique(personal_numbers, return_counts=True)
                    user_best = [num for num, _ in 
                                sorted(zip(unique, counts), key=lambda x: x[1], reverse=True)]
                    personal_prediction = user_best[:count]
        
        # Return the best prediction based on strategy
        if personal_prediction and len(personal_prediction) >= count:
            return sorted(personal_prediction[:count])
        elif len(balanced_prediction) >= count:
            return sorted(balanced_prediction[:count])
        else:
            return sorted(hot_prediction[:count])
    
    def calculate_probability(self, numbers: List[int], lottery_type: str = "lotto") -> float:
        """Calculate the probability of winning with given numbers"""
        # Simplified probability calculation
        total_numbers = 49  # For standard lotto
        numbers_to_choose = 6
        
        # Basic combinatorial probability
        from math import comb
        total_combinations = comb(total_numbers, numbers_to_choose)
        probability = 1 / total_combinations
        
        # Adjust based on number patterns (simplified)
        # In reality, you'd use more sophisticated analysis
        return probability * 100  # Return as percentage
