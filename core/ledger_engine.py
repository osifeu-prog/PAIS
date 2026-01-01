import asyncpg
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
import json
import logging
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LedgerEngine:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    async def get_balance(self, user_id: int) -> Dict:
        """Get user's current balance"""
        async with self.db_pool.acquire() as conn:
            wallet = await conn.fetchrow("""
                SELECT * FROM wallets WHERE user_id = $1
            """, user_id)
            
            if not wallet:
                # Create wallet if doesn't exist
                wallet = await self.create_wallet(user_id)
            
            return dict(wallet)
    
    async def create_wallet(self, user_id: int) -> Dict:
        """Create a new wallet for user"""
        async with self.db_pool.acquire() as conn:
            initial_balance = Decimal(settings.POINTS["initial_balance"])
            
            wallet = await conn.fetchrow("""
                INSERT INTO wallets (user_id, points_balance)
                VALUES ($1, $2)
                RETURNING *
            """, user_id, initial_balance)
            
            # Record initial balance in ledger
            await conn.execute("""
                INSERT INTO ledger 
                (user_id, transaction_type, amount, balance_after, description)
                VALUES ($1, $2, $3, $4, $5)
            """, user_id, "initial_deposit", initial_balance, 
               initial_balance, "Initial points balance")
            
            return dict(wallet)
    
    async def add_transaction(self, user_id: int, 
                            transaction_type: str, 
                            amount: Decimal,
                            description: str = "",
                            reference_id: str = None) -> bool:
        """Add a transaction to ledger and update wallet"""
        try:
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    # Get current balance
                    current = await conn.fetchrow("""
                        SELECT points_balance FROM wallets WHERE user_id = $1
                    """, user_id)
                    
                    if not current:
                        logger.error(f"Wallet not found for user {user_id}")
                        return False
                    
                    current_balance = current["points_balance"]
                    new_balance = current_balance + amount
                    
                    # Update wallet
                    if amount > 0:
                        update_field = "total_earned = total_earned + $2"
                    else:
                        update_field = "total_spent = total_spent - $2"
                    
                    await conn.execute(f"""
                        UPDATE wallets 
                        SET points_balance = points_balance + $2,
                            {update_field}
                        WHERE user_id = $1
                    """, user_id, amount)
                    
                    # Record in ledger
                    await conn.execute("""
                        INSERT INTO ledger 
                        (user_id, transaction_type, amount, balance_after, 
                         description, reference_id)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """, user_id, transaction_type, amount, new_balance, 
                       description, reference_id)
                    
                    # Log activity
                    await conn.execute("""
                        INSERT INTO activity_log 
                        (user_id, activity_type, points_change, metadata)
                        VALUES ($1, $2, $3, $4)
                    """, user_id, transaction_type, amount,
                       json.dumps({"description": description}))
                    
                    logger.info(f"Transaction recorded: user={user_id}, "
                              f"type={transaction_type}, amount={amount}")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Error recording transaction: {e}")
            return False
    
    async def get_transaction_history(self, user_id: int, 
                                     limit: int = 50,
                                     offset: int = 0) -> List[Dict]:
        """Get user's transaction history"""
        async with self.db_pool.acquire() as conn:
            transactions = await conn.fetch("""
                SELECT * FROM ledger 
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """, user_id, limit, offset)
            
            return [dict(t) for t in transactions]
    
    async def validate_transaction(self, user_id: int, amount: Decimal) -> bool:
        """Validate if user has sufficient balance for transaction"""
        async with self.db_pool.acquire() as conn:
            wallet = await conn.fetchrow("""
                SELECT points_balance FROM wallets WHERE user_id = $1
            """, user_id)
            
            if not wallet:
                return False
            
            # Check if balance is sufficient (for negative amounts)
            if amount < 0 and abs(amount) > wallet["points_balance"]:
                return False
            
            return True
    
    async def transfer_points(self, from_user_id: int, 
                            to_user_id: int, 
                            amount: Decimal,
                            description: str = "") -> bool:
        """Transfer points between users"""
        if amount <= 0:
            return False
        
        try:
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    # Check sender's balance
                    sender_balance = await conn.fetchval("""
                        SELECT points_balance FROM wallets WHERE user_id = $1
                    """, from_user_id)
                    
                    if sender_balance < amount:
                        logger.error(f"Insufficient balance for transfer: "
                                   f"user={from_user_id}, balance={sender_balance}")
                        return False
                    
                    # Deduct from sender
                    await self.add_transaction(
                        from_user_id, "transfer_out", -amount,
                        f"Transfer to user {to_user_id}: {description}"
                    )
                    
                    # Add to receiver
                    await self.add_transaction(
                        to_user_id, "transfer_in", amount,
                        f"Transfer from user {from_user_id}: {description}"
                    )
                    
                    logger.info(f"Transfer completed: {from_user_id} -> "
                              f"{to_user_id}, amount={amount}")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Error in transfer: {e}")
            return False
    
    async def get_daily_summary(self, user_id: int, date: datetime = None) -> Dict:
        """Get daily transaction summary"""
        if date is None:
            date = datetime.now()
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        async with self.db_pool.acquire() as conn:
            summary = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as transaction_count,
                    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as total_expenses
                FROM ledger 
                WHERE user_id = $1 
                    AND created_at >= $2 
                    AND created_at <= $3
            """, user_id, start_date, end_date)
            
            return dict(summary) if summary else {
                "transaction_count": 0,
                "total_income": 0,
                "total_expenses": 0
            }
