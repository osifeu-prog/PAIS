from fastapi import APIRouter, Depends, HTTPException, Form, Body
from typing import Optional
import asyncpg
from datetime import datetime

from server.main import get_current_user, app
from core.ledger_engine import LedgerEngine

router = APIRouter()

@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    async with app.state.db_pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT u.*, w.points_balance, w.total_earned, w.total_spent,
                   w.last_interest_calc
            FROM users u
            LEFT JOIN wallets w ON u.id = w.user_id
            WHERE u.id = $1
        """, current_user["id"])
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user stats
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(DISTINCT p.id) as total_predictions,
                COUNT(DISTINCT CASE WHEN p.is_correct = true THEN p.id END) as correct_predictions,
                COUNT(DISTINCT b.id) as total_listings,
                COUNT(DISTINCT t.id) as total_transactions
            FROM users u
            LEFT JOIN predictions p ON u.id = p.user_id
            LEFT JOIN barter_listings b ON u.id = b.user_id
            LEFT JOIN barter_transactions t ON u.id = t.buyer_id OR u.id = t.seller_id
            WHERE u.id = $1
        """, current_user["id"])
        
        return {
            "user": dict(user),
            "stats": dict(stats) if stats else {}
        }

@router.put("/profile")
async def update_user_profile(
    email: Optional[str] = Body(None),
    phone: Optional[str] = Body(None),
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    async with app.state.db_pool.acquire() as conn:
        # Check if email is already taken
        if email:
            existing = await conn.fetchval("""
                SELECT 1 FROM users 
                WHERE email = $1 AND id != $2
            """, email, current_user["id"])
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
        
        # Build update query
        updates = []
        params = []
        param_count = 1
        
        if email:
            updates.append(f"email = ${param_count}")
            params.append(email)
            param_count += 1
        
        if phone:
            updates.append(f"phone = ${param_count}")
            params.append(phone)
            param_count += 1
        
        if not updates:
            raise HTTPException(
                status_code=400,
                detail="No fields to update"
            )
        
        # Add user ID as last parameter
        params.append(current_user["id"])
        
        query = f"""
            UPDATE users 
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_count}
            RETURNING *
        """
        
        updated_user = await conn.fetchrow(query, *params)
        
        return {"message": "Profile updated successfully", "user": dict(updated_user)}

@router.get("/leaderboard")
async def get_leaderboard(
    timeframe: str = "weekly",  # daily, weekly, monthly, all_time
    limit: int = 50
):
    """Get user leaderboard"""
    time_filters = {
        "daily": "DATE(created_at) = CURRENT_DATE",
        "weekly": "created_at >= CURRENT_DATE - INTERVAL '7 days'",
        "monthly": "created_at >= CURRENT_DATE - INTERVAL '30 days'",
        "all_time": "1=1"
    }
    
    if timeframe not in time_filters:
        raise HTTPException(status_code=400, detail="Invalid timeframe")
    
    time_filter = time_filters[timeframe]
    
    async with app.state.db_pool.acquire() as conn:
        leaderboard = await conn.fetch(f"""
            SELECT 
                u.id,
                u.username,
                u.user_level,
                w.points_balance,
                COUNT(DISTINCT p.id) as prediction_count,
                COUNT(DISTINCT CASE WHEN p.is_correct = true THEN p.id END) as correct_predictions,
                COALESCE(SUM(p.points_awarded), 0) as total_points_earned
            FROM users u
            LEFT JOIN wallets w ON u.id = w.user_id
            LEFT JOIN predictions p ON u.id = p.user_id AND {time_filter}
            WHERE u.is_active = true
            GROUP BY u.id, u.username, u.user_level, w.points_balance
            ORDER BY w.points_balance DESC
            LIMIT $1
        """, limit)
        
        return [
            {
                "rank": idx + 1,
                "user_id": row["id"],
                "username": row["username"],
                "level": row["user_level"],
                "points_balance": float(row["points_balance"]),
                "prediction_count": row["prediction_count"],
                "correct_predictions": row["correct_predictions"],
                "total_points_earned": float(row["total_points_earned"])
            }
            for idx, row in enumerate(leaderboard)
        ]

@router.post("/register-telegram")
async def register_telegram(
    telegram_id: int = Body(...),
    username: str = Body(...),
    main_system_id: Optional[str] = Body(None)
):
    """Register a new user via Telegram"""
    async with app.state.db_pool.acquire() as conn:
        # Check if Telegram ID already exists
        existing = await conn.fetchrow("""
            SELECT * FROM users WHERE telegram_id = $1
        """, telegram_id)
        
        if existing:
            # Update username if changed
            if existing["username"] != username:
                await conn.execute("""
                    UPDATE users SET username = $1 WHERE id = $2
                """, username, existing["id"])
            
            return {
                "message": "User already exists",
                "user_id": existing["id"],
                "is_new": False
            }
        
        # Create new user
        user = await conn.fetchrow("""
            INSERT INTO users 
            (telegram_id, username, main_system_id, user_level)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """, telegram_id, username, main_system_id, "beginner")
        
        # Create wallet for new user
        from core.config import settings
        initial_balance = settings.POINTS["initial_balance"]
        
        await conn.execute("""
            INSERT INTO wallets (user_id, points_balance)
            VALUES ($1, $2)
        """, user["id"], initial_balance)
        
        return {
            "message": "User registered successfully",
            "user_id": user["id"],
            "is_new": True,
            "initial_points": initial_balance
        }

@router.get("/activity")
async def get_user_activity(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user activity log"""
    offset = (page - 1) * limit
    
    async with app.state.db_pool.acquire() as conn:
        activities = await conn.fetch("""
            SELECT * FROM activity_log 
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """, current_user["id"], limit, offset)
        
        total = await conn.fetchval("""
            SELECT COUNT(*) FROM activity_log WHERE user_id = $1
        """, current_user["id"])
        
        return {
            "activities": [dict(a) for a in activities],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
