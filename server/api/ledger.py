from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from server.main import get_current_user, app
from core.ledger_engine import LedgerEngine
from core.interest_calculator import InterestCalculator

router = APIRouter()

@router.get("/balance")
async def get_balance(current_user: dict = Depends(get_current_user)):
    """Get current balance"""
    engine = LedgerEngine(app.state.db_pool)
    balance = await engine.get_balance(current_user["id"])
    
    # Calculate projected balance with interest
    interest_calc = InterestCalculator(app.state.db_pool)
    apy = await interest_calc.calculate_apy()
    
    # Get today's interest projection
    today_interest = Decimal(str(balance["points_balance"])) * \
                     Decimal(str(0.001))  # Daily rate
    
    return {
        "balance": float(balance["points_balance"]),
        "total_earned": float(balance["total_earned"]),
        "total_spent": float(balance["total_spent"]),
        "interest_rate": {
            "daily": 0.001,
            "apy": float(apy)
        },
        "projected_interest_today": float(today_interest),
        "last_interest_calculation": balance["last_interest_calc"]
    }

@router.get("/transactions")
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    transaction_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get transaction history"""
    engine = LedgerEngine(app.state.db_pool)
    
    # Get all transactions
    transactions = await engine.get_transaction_history(
        current_user["id"], 
        limit=limit, 
        offset=(page-1)*limit
    )
    
    # Apply filters
    filtered = []
    for t in transactions:
        t_date = t["created_at"].date()
        
        # Filter by type
        if transaction_type and t["transaction_type"] != transaction_type:
            continue
        
        # Filter by date range
        if start_date and t_date < start_date:
            continue
        if end_date and t_date > end_date:
            continue
        
        filtered.append(t)
    
    # Get total count
    async with app.state.db_pool.acquire() as conn:
        total = await conn.fetchval("""
            SELECT COUNT(*) FROM ledger WHERE user_id = $1
        """, current_user["id"])
    
    return {
        "transactions": filtered,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.get("/daily-summary")
async def get_daily_summary(
    summary_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get daily transaction summary"""
    engine = LedgerEngine(app.state.db_pool)
    summary = await engine.get_daily_summary(current_user["id"], summary_date)
    
    return {
        "date": summary_date or date.today(),
        "summary": summary,
        "net_change": summary["total_income"] + summary["total_expenses"]
    }

@router.post("/transfer")
async def transfer_points(
    to_user_id: int,
    amount: float,
    description: str = "",
    current_user: dict = Depends(get_current_user)
):
    """Transfer points to another user"""
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be positive"
        )
    
    # Check if transferring to self
    if to_user_id == current_user["id"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer to yourself"
        )
    
    # Check if recipient exists
    async with app.state.db_pool.acquire() as conn:
        recipient = await conn.fetchrow("""
            SELECT id FROM users WHERE id = $1 AND is_active = true
        """, to_user_id)
        
        if not recipient:
            raise HTTPException(
                status_code=404,
                detail="Recipient not found"
            )
    
    engine = LedgerEngine(app.state.db_pool)
    amount_decimal = Decimal(str(amount))
    
    success = await engine.transfer_points(
        current_user["id"], to_user_id, amount_decimal, description
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Transfer failed. Check your balance."
        )
    
    return {
        "message": "Transfer successful",
        "from_user": current_user["id"],
        "to_user": to_user_id,
        "amount": amount,
        "description": description
    }

@router.get("/interest/history")
async def get_interest_history(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get interest earning history"""
    calculator = InterestCalculator(app.state.db_pool)
    history = await calculator.get_interest_history(current_user["id"], days)
    
    total_interest = sum(Decimal(str(h["interest_earned"])) for h in history)
    
    return {
        "history": history,
        "summary": {
            "period_days": days,
            "total_interest_earned": float(total_interest),
            "average_daily_interest": float(total_interest / days) if days > 0 else 0
        }
    }

@router.get("/interest/projection")
async def get_interest_projection(
    days_ahead: int = Query(365, ge=1, le=1825),  # Up to 5 years
    current_user: dict = Depends(get_current_user)
):
    """Get future balance projection with interest"""
    calculator = InterestCalculator(app.state.db_pool)
    projections = await calculator.project_future_balance(current_user["id"], days_ahead)
    
    if not projections:
        return {"message": "No projections available"}
    
    # Get key milestones
    milestones = [7, 30, 90, 180, 365]
    milestone_data = []
    
    for milestone in milestones:
        if milestone <= days_ahead:
            for proj in projections:
                if proj["day"] == milestone:
                    milestone_data.append(proj)
                    break
    
    return {
        "current_balance": projections[0]["projected_balance"] - projections[0]["interest_earned"],
        "projections": projections,
        "milestones": milestone_data,
        "final_projection": projections[-1] if projections else None
    }

@router.get("/stats")
async def get_ledger_stats(
    timeframe: str = "monthly",  # weekly, monthly, yearly
    current_user: dict = Depends(get_current_user)
):
    """Get ledger statistics"""
    time_conditions = {
        "weekly": "created_at >= CURRENT_DATE - INTERVAL '7 days'",
        "monthly": "created_at >= CURRENT_DATE - INTERVAL '30 days'",
        "yearly": "created_at >= CURRENT_DATE - INTERVAL '365 days'"
    }
    
    if timeframe not in time_conditions:
        raise HTTPException(status_code=400, detail="Invalid timeframe")
    
    condition = time_conditions[timeframe]
    
    async with app.state.db_pool.acquire() as conn:
        stats = await conn.fetchrow(f"""
            SELECT 
                COUNT(*) as transaction_count,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as total_expenses,
                AVG(CASE WHEN amount > 0 THEN amount END) as avg_income,
                AVG(CASE WHEN amount < 0 THEN amount END) as avg_expense,
                MIN(created_at) as first_transaction,
                MAX(created_at) as last_transaction
            FROM ledger 
            WHERE user_id = $1 AND {condition}
        """, current_user["id"])
        
        # Get transaction type breakdown
        breakdown = await conn.fetch(f"""
            SELECT 
                transaction_type,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM ledger 
            WHERE user_id = $1 AND {condition}
            GROUP BY transaction_type
            ORDER BY total_amount DESC
        """, current_user["id"])
        
        return {
            "timeframe": timeframe,
            "summary": dict(stats) if stats else {},
            "breakdown": [dict(row) for row in breakdown]
        }
