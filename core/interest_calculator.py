import asyncio
import asyncpg
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterestCalculator:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.daily_rate = Decimal(str(settings.INTEREST["daily_rate"]))
    
    async def calculate_daily_interest(self, calculation_date: datetime = None):
        """Calculate daily interest for all users"""
        if calculation_date is None:
            calculation_date = datetime.now().date()
        
        logger.info(f"Starting daily interest calculation for {calculation_date}")
        
        async with self.db_pool.acquire() as conn:
            # Get all active users with minimum balance
            min_balance = Decimal(str(settings.SCORING_RULES["interest_rules"]
                                    ["minimum_balance_for_interest"]))
            
            users = await conn.fetch("""
                SELECT w.*, u.is_active 
                FROM wallets w
                JOIN users u ON w.user_id = u.id
                WHERE w.points_balance >= $1 
                    AND u.is_active = true
                    AND (w.last_interest_calc IS NULL 
                         OR DATE(w.last_interest_calc) < $2)
            """, min_balance, calculation_date)
            
            total_interest = Decimal('0')
            users_processed = 0
            
            for user in users:
                interest_earned = await self.calculate_user_interest(user, calculation_date)
                
                if interest_earned > 0:
                    # Update wallet with interest
                    await conn.execute("""
                        UPDATE wallets 
                        SET points_balance = points_balance + $1,
                            last_interest_calc = $2
                        WHERE id = $3
                    """, interest_earned, calculation_date, user["id"])
                    
                    # Record interest in ledger
                    await conn.execute("""
                        INSERT INTO ledger 
                        (user_id, transaction_type, amount, description)
                        VALUES ($1, $2, $3, $4)
                    """, user["user_id"], "interest", interest_earned,
                       f"Daily interest at rate {self.daily_rate*100}%")
                    
                    # Record in interest history
                    await conn.execute("""
                        INSERT INTO interest_history 
                        (user_id, calculation_date, points_before, 
                         interest_earned, points_after)
                        VALUES ($1, $2, $3, $4, $5)
                    """, user["user_id"], calculation_date, 
                       user["points_balance"], interest_earned,
                       user["points_balance"] + interest_earned)
                    
                    total_interest += interest_earned
                    users_processed += 1
            
            logger.info(f"Interest calculation complete: "
                       f"users={users_processed}, total_interest={total_interest}")
            
            return {
                "date": calculation_date,
                "users_processed": users_processed,
                "total_interest_distributed": total_interest
            }
    
    async def calculate_user_interest(self, user: dict, calculation_date: datetime) -> Decimal:
        """Calculate interest for a specific user"""
        balance = Decimal(str(user["points_balance"]))
        
        # Check for maximum daily interest limit
        max_daily = Decimal(str(settings.SCORING_RULES["interest_rules"]
                              ["maximum_daily_interest"]))
        
        # Calculate interest
        interest = balance * self.daily_rate
        
        # Apply compounding if enabled
        if settings.SCORING_RULES["interest_rules"]["compounding"] == "daily":
            # For daily compounding, we use simple interest per day
            pass  # Already calculated as simple interest
        
        # Cap at maximum daily interest
        if interest > max_daily:
            interest = max_daily
        
        return interest.quantize(Decimal('0.0001'))
    
    async def get_interest_history(self, user_id: int, days: int = 30) -> list:
        """Get interest history for a user"""
        start_date = datetime.now().date() - timedelta(days=days)
        
        async with self.db_pool.acquire() as conn:
            history = await conn.fetch("""
                SELECT * FROM interest_history 
                WHERE user_id = $1 AND calculation_date >= $2
                ORDER BY calculation_date DESC
            """, user_id, start_date)
            
            return [dict(h) for h in history]
    
    async def calculate_compound_interest(self, principal: Decimal, 
                                         days: int,
                                         daily_rate: Decimal = None) -> Decimal:
        """Calculate compound interest for a given period"""
        if daily_rate is None:
            daily_rate = self.daily_rate
        
        # A = P(1 + r)^t
        # Where r is daily rate, t is number of days
        amount = principal * (1 + daily_rate) ** days
        
        return amount.quantize(Decimal('0.0001'))
    
    async def project_future_balance(self, user_id: int, 
                                    days_ahead: int = 365) -> list:
        """Project future balance with interest"""
        async with self.db_pool.acquire() as conn:
            wallet = await conn.fetchrow("""
                SELECT points_balance FROM wallets WHERE user_id = $1
            """, user_id)
            
            if not wallet:
                return []
            
            current_balance = Decimal(str(wallet["points_balance"]))
            projections = []
            
            for day in range(1, days_ahead + 1):
                future_balance = await self.calculate_compound_interest(
                    current_balance, day
                )
                
                projections.append({
                    "day": day,
                    "date": (datetime.now() + timedelta(days=day)).date(),
                    "projected_balance": future_balance,
                    "interest_earned": future_balance - current_balance
                })
            
            return projections
    
    async def calculate_apy(self) -> Decimal:
        """Calculate Annual Percentage Yield"""
        # APY = (1 + daily_rate)^365 - 1
        daily_rate = self.daily_rate
        apy = (1 + daily_rate) ** 365 - 1
        
        return (apy * 100).quantize(Decimal('0.01'))  # Return as percentage
