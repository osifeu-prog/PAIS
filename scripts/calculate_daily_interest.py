#!/usr/bin/env python3
"""
Script to calculate daily interest for all users
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta
from decimal import Decimal

async def calculate_daily_interest():
    """Calculate and apply daily interest"""
    try:
        # Database connection
        conn = await asyncpg.connect(
            user='prediction_user',
            password='prediction_pass', 
            database='prediction_db',
            host='localhost'
        )
        
        print("💰 Starting daily interest calculation...")
        
        # Daily interest rate: 0.1%
        daily_rate = Decimal('0.001')
        
        # Get all active users with minimum balance
        users = await conn.fetch("""
            SELECT w.id, w.user_id, w.points_balance, u.username
            FROM wallets w
            JOIN users u ON w.user_id = u.id
            WHERE w.points_balance >= 100 
                AND u.is_active = true
                AND (w.last_interest_calc IS NULL 
                     OR DATE(w.last_interest_calc) < CURRENT_DATE)
        """)
        
        total_interest = Decimal('0')
        users_processed = 0
        
        for user in users:
            balance = Decimal(str(user['points_balance']))
            interest = balance * daily_rate
            
            # Cap at maximum 500 points per day
            max_daily = Decimal('500')
            if interest > max_daily:
                interest = max_daily
            
            if interest > 0:
                # Update wallet
                await conn.execute("""
                    UPDATE wallets 
                    SET points_balance = points_balance + $1,
                        last_interest_calc = CURRENT_TIMESTAMP
                    WHERE id = $2
                """, interest, user['id'])
                
                # Record in ledger
                await conn.execute("""
                    INSERT INTO ledger 
                    (user_id, transaction_type, amount, description)
                    VALUES ($1, $2, $3, $4)
                """, user['user_id'], 'interest', interest,
                   f'Daily interest at rate {daily_rate*100}%')
                
                total_interest += interest
                users_processed += 1
        
        print(f"✅ Interest calculation complete!")
        print(f"📊 Users processed: {users_processed}")
        print(f"💰 Total interest distributed: {total_interest}")
        
        # Close connection
        await conn.close()
        
    except Exception as e:
        print(f"❌ Interest calculation failed: {e}")

if __name__ == "__main__":
    asyncio.run(calculate_daily_interest())
