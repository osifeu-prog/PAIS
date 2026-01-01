from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date
import json


from core.prediction_engine import PredictionEngine

router = APIRouter()

@router.get("/lottery-types")
async def get_lottery_types(current_user: dict = Depends(get_current_user)):
    """Get available lottery types"""
    return {
        "lottery_types": [
            {"id": "lotto", "name": "Lotto", "numbers": 6, "range": "1-49"},
            {"id": "777", "name": "777", "numbers": 3, "range": "0-9"},
            {"id": "chance", "name": "Chance", "numbers": 4, "range": "0-9"}
        ]
    }

@router.post("/generate")
async def generate_prediction(
    lottery_type: str = "lotto",
    strategy: str = "balanced",
    current_user: dict = Depends(get_current_user)
):
    """Generate a new prediction"""
    async with app.state.db_pool.acquire() as conn:
        # Check daily limit
        today = date.today()
        today_predictions = await conn.fetchval("""
            SELECT COUNT(*) FROM predictions 
            WHERE user_id = $1 
                AND DATE(created_at) = $2
                AND lottery_type = $3
        """, current_user["id"], today, lottery_type)
        
        # Get scoring rules
        daily_limit = 10  # Default
        
        if today_predictions >= daily_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Daily prediction limit reached ({daily_limit})"
            )
        
        # Generate prediction
        engine = PredictionEngine(app.state.db_pool)
        numbers = await engine.generate_predictions(
            current_user["id"], lottery_type
        )
        
        # Calculate probability
        probability = engine.calculate_probability(numbers, lottery_type)
        
        # Save prediction
        prediction = await conn.fetchrow("""
            INSERT INTO predictions 
            (user_id, lottery_type, prediction_numbers, prediction_date)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """, current_user["id"], lottery_type, json.dumps(numbers), today)
        
        # Award points for making prediction
        scoring_rules = app.state.scoring_rules
        points = scoring_rules["actions"]["make_prediction"]["points"]
        
        await conn.execute("""
            UPDATE wallets 
            SET points_balance = points_balance + $1
            WHERE user_id = $2
        """, points, current_user["id"])
        
        # Log transaction
        await conn.execute("""
            INSERT INTO ledger 
            (user_id, transaction_type, amount, description)
            VALUES ($1, $2, $3, $4)
        """, current_user["id"], "prediction", points,
           f"Prediction generated for {lottery_type}")
        
        return {
            "prediction_id": prediction["id"],
            "lottery_type": lottery_type,
            "numbers": numbers,
            "probability": probability,
            "points_awarded": points,
            "daily_predictions_used": today_predictions + 1,
            "daily_predictions_left": daily_limit - (today_predictions + 1)
        }

@router.get("/history")
async def get_prediction_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get user's prediction history"""
    offset = (page - 1) * limit
    
    async with app.state.db_pool.acquire() as conn:
        predictions = await conn.fetch("""
            SELECT * FROM predictions 
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """, current_user["id"], limit, offset)
        
        total = await conn.fetchval("""
            SELECT COUNT(*) FROM predictions WHERE user_id = $1
        """, current_user["id"])
        
        # Parse JSON fields
        result = []
        for pred in predictions:
            pred_dict = dict(pred)
            pred_dict["prediction_numbers"] = json.loads(pred["prediction_numbers"])
            if pred["actual_numbers"]:
                pred_dict["actual_numbers"] = json.loads(pred["actual_numbers"])
            result.append(pred_dict)
        
        return {
            "predictions": result,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }

@router.get("/stats")
async def get_prediction_stats(current_user: dict = Depends(get_current_user)):
    """Get user's prediction statistics"""
    async with app.state.db_pool.acquire() as conn:
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_predictions,
                COUNT(CASE WHEN is_correct = true THEN 1 END) as correct_predictions,
                AVG(accuracy) as average_accuracy,
                SUM(points_awarded) as total_points_earned,
                MAX(accuracy) as best_accuracy,
                MIN(accuracy) as worst_accuracy
            FROM predictions 
            WHERE user_id = $1
        """, current_user["id"])
        
        if stats["total_predictions"] == 0:
            return {
                "message": "No predictions yet",
                "total_predictions": 0
            }
        
        success_rate = (stats["correct_predictions"] / stats["total_predictions"]) * 100
        
        return {
            "total_predictions": stats["total_predictions"],
            "correct_predictions": stats["correct_predictions"],
            "success_rate": round(success_rate, 2),
            "average_accuracy": round(float(stats["average_accuracy"] or 0), 2),
            "total_points_earned": float(stats["total_points_earned"] or 0),
            "best_accuracy": round(float(stats["best_accuracy"] or 0), 2),
            "worst_accuracy": round(float(stats["worst_accuracy"] or 0), 2)
        }

@router.get("/lottery-results")
async def get_lottery_results(
    lottery_type: str = "lotto",
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get recent lottery results"""
    async with app.state.db_pool.acquire() as conn:
        results = await conn.fetch("""
            SELECT * FROM lottery_results 
            WHERE lottery_type = $1
            ORDER BY draw_date DESC
            LIMIT $2
        """, lottery_type, limit)
        
        # Parse JSON fields
        formatted_results = []
        for result in results:
            result_dict = dict(result)
            result_dict["winning_numbers"] = json.loads(result["winning_numbers"])
            result_dict["bonus_numbers"] = json.loads(result["bonus_numbers"])
            formatted_results.append(result_dict)
        
        return formatted_results

@router.post("/analyze-numbers")
async def analyze_numbers(
    numbers: List[int],
    lottery_type: str = "lotto",
    current_user: dict = Depends(get_current_user)
):
    """Analyze given numbers"""
    if len(numbers) < 3 or len(numbers) > 10:
        raise HTTPException(
            status_code=400,
            detail="Please provide 3-10 numbers"
        )
    
    async with app.state.db_pool.acquire() as conn:
        # Get historical data for analysis
        engine = PredictionEngine(app.state.db_pool)
        historical_data = await engine.get_historical_data(lottery_type, 1000)
        analysis = engine.analyze_frequency(historical_data)
        
        # Calculate score for given numbers
        score = 0
        hot_count = 0
        cold_count = 0
        
        for num in numbers:
            if num in analysis["hot_numbers"]:
                score += 2
                hot_count += 1
            elif num in analysis["cold_numbers"]:
                score -= 1
                cold_count += 1
            else:
                score += 1
        
        # Calculate probability
        probability = engine.calculate_probability(numbers, lottery_type)
        
        # Get similar past results
        similar_results = []
        for result in historical_data[:20]:  # Last 20 results
            winning_numbers = json.loads(result["winning_numbers"])
            matches = len(set(numbers) & set(winning_numbers))
            if matches >= len(numbers) // 2:
                similar_results.append({
                    "date": result["draw_date"],
                    "numbers": winning_numbers,
                    "matches": matches
                })
        
        return {
            "numbers": numbers,
            "score": score,
            "hot_numbers_used": hot_count,
            "cold_numbers_used": cold_count,
            "probability_percentage": round(probability, 4),
            "analysis": {
                "hot_numbers": analysis["hot_numbers"][:10],
                "cold_numbers": analysis["cold_numbers"][:10]
            },
            "similar_past_results": similar_results[:5]
        }


