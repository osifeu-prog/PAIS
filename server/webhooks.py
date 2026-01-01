from fastapi import APIRouter, Request, HTTPException, Header
import hashlib
import hmac
import json
from typing import Optional
import logging

from server.main import app
from core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature"""
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

@router.post("/railway")
async def railway_webhook(
    request: Request,
    x_railway_signature: Optional[str] = Header(None)
):
    """Handle Railway webhooks for deployments"""
    try:
        payload = await request.body()
        
        # Verify signature if provided
        if x_railway_signature:
            # In production, use your Railway webhook secret
            if not verify_webhook_signature(payload, x_railway_signature, "your_railway_secret"):
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        data = await request.json()
        
        # Log deployment event
        logger.info(f"Railway webhook received: {data.get('type', 'unknown')}")
        
        # Handle different event types
        event_type = data.get("type")
        
        if event_type == "deployment.succeeded":
            deployment_id = data.get("deployment", {}).get("id")
            logger.info(f"Deployment {deployment_id} succeeded")
            
            # You could trigger data sync or other post-deployment tasks here
            async with app.state.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO activity_log 
                    (user_id, activity_type, metadata)
                    VALUES (0, 'deployment_succeeded', $1)
                """, json.dumps({"deployment_id": deployment_id}))
        
        elif event_type == "deployment.failed":
            logger.error(f"Deployment failed: {data}")
            
        return {"status": "received", "event": event_type}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/main-system")
async def main_system_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None)
):
    """Handle webhooks from main system"""
    try:
        payload = await request.body()
        
        # Verify signature
        webhook_secret = settings.WEBHOOK_SECRET
        if not verify_webhook_signature(payload, x_signature, webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        data = await request.json()
        event_type = data.get("event")
        
        logger.info(f"Main system webhook: {event_type}")
        
        async with app.state.db_pool.acquire() as conn:
            if event_type == "user.created":
                # Sync user from main system
                user_data = data.get("data", {})
                
                await conn.execute("""
                    INSERT INTO users 
                    (main_system_id, username, email, phone, user_level)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (main_system_id) DO UPDATE 
                    SET username = EXCLUDED.username,
                        email = EXCLUDED.email,
                        phone = EXCLUDED.phone,
                        updated_at = CURRENT_TIMESTAMP
                """, user_data.get("id"), user_data.get("username"),
                   user_data.get("email"), user_data.get("phone"),
                   user_data.get("level", "beginner"))
                
                # Create wallet if doesn't exist
                user_id = await conn.fetchval("""
                    SELECT id FROM users WHERE main_system_id = $1
                """, user_data.get("id"))
                
                wallet_exists = await conn.fetchval("""
                    SELECT 1 FROM wallets WHERE user_id = $1
                """, user_id)
                
                if not wallet_exists:
                    initial_balance = settings.POINTS["initial_balance"]
                    await conn.execute("""
                        INSERT INTO wallets (user_id, points_balance)
                        VALUES ($1, $2)
                    """, user_id, initial_balance)
            
            elif event_type == "points.transfer":
                # Handle points transfer from main system
                transfer_data = data.get("data", {})
                from_user_id = await conn.fetchval("""
                    SELECT id FROM users WHERE main_system_id = $1
                """, transfer_data.get("from_user_id"))
                
                to_user_id = await conn.fetchval("""
                    SELECT id FROM users WHERE main_system_id = $1
                """, transfer_data.get("to_user_id"))
                
                amount = transfer_data.get("amount")
                description = transfer_data.get("description", "")
                
                if from_user_id and to_user_id and amount:
                    # Use ledger engine for transfer
                    from core.ledger_engine import LedgerEngine
                    ledger = LedgerEngine(app.state.db_pool)
                    
                    success = await ledger.transfer_points(
                        from_user_id, to_user_id, amount, description
                    )
                    
                    if not success:
                        logger.error(f"Failed to process points transfer: {transfer_data}")
            
            elif event_type == "system.sync":
                # Trigger data sync
                from core.data_sync import DataSync
                sync_engine = DataSync(app.state.db_pool)
                
                results = await sync_engine.fetch_lottery_results()
                await sync_engine.sync_results_to_db(results)
                await sync_engine.update_user_predictions()
                
                logger.info(f"Data sync completed: {len(results)} results")
            
            # Log webhook event
            await conn.execute("""
                INSERT INTO activity_log 
                (user_id, activity_type, metadata)
                VALUES (0, 'webhook_received', $1)
            """, json.dumps({"event": event_type, "data": data}))
        
        return {"status": "processed", "event": event_type}
        
    except Exception as e:
        logger.error(f"Error processing main system webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/telegram")
async def telegram_webhook(request: Request):
    """Handle Telegram bot webhook"""
    try:
        data = await request.json()
        update = data.get("message") or data.get("callback_query")
        
        if not update:
            return {"status": "ignored"}
        
        # Process Telegram update (simplified - actual processing in bot.py)
        logger.info(f"Telegram webhook received: {update}")
        
        # You could forward to your bot processor here
        # In production, use a message queue or direct processing
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        return {"status": "error", "detail": str(e)}
