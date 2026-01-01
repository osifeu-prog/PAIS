from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import json

from server.main import get_current_user, app
from core.ledger_engine import LedgerEngine
from core.config import settings

router = APIRouter()

@router.get("/listings")
async def get_market_listings(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get active market listings"""
    offset = (page - 1) * limit
    
    # Build filter conditions
    conditions = ["status = 'active'"]
    params = []
    param_count = 1
    
    if category:
        conditions.append(f"category = ${param_count}")
        params.append(category)
        param_count += 1
    
    if min_price:
        conditions.append(f"points_price >= ${param_count}")
        params.append(Decimal(str(min_price)))
        param_count += 1
    
    if max_price:
        conditions.append(f"points_price <= ${param_count}")
        params.append(Decimal(str(max_price)))
        param_count += 1
    
    if search:
        conditions.append(f"(title ILIKE ${param_count} OR description ILIKE ${param_count})")
        params.append(f"%{search}%")
        param_count += 1
    
    where_clause = " AND ".join(conditions)
    
    async with app.state.db_pool.acquire() as conn:
        listings = await conn.fetch(f"""
            SELECT 
                b.*,
                u.username as seller_username,
                u.user_level as seller_level
            FROM barter_listings b
            JOIN users u ON b.user_id = u.id
            WHERE {where_clause}
            ORDER BY 
                CASE WHEN is_featured = true THEN 0 ELSE 1 END,
                created_at DESC
            LIMIT ${param_count} OFFSET ${param_count + 1}
        """, *params, limit, offset)
        
        total = await conn.fetchval(f"""
            SELECT COUNT(*) FROM barter_listings 
            WHERE {where_clause}
        """, *params)
        
        # Increment view count (simplified)
        for listing in listings:
            await conn.execute("""
                UPDATE barter_listings 
                SET views = views + 1 
                WHERE id = $1
            """, listing["id"])
        
        return {
            "listings": [dict(l) for l in listings],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }

@router.post("/listings")
async def create_listing(
    title: str = Body(...),
    description: str = Body(...),
    category: str = Body(...),
    points_price: float = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create a new market listing"""
    # Validate category
    allowed_categories = settings.BARTER["allowed_categories"]
    if category not in allowed_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Category must be one of: {', '.join(allowed_categories)}"
        )
    
    # Validate price
    min_price = settings.BARTER["restrictions"]["min_price"]
    max_price = settings.BARTER["restrictions"]["max_price"]
    
    if points_price < min_price or points_price > max_price:
        raise HTTPException(
            status_code=400,
            detail=f"Price must be between {min_price} and {max_price} points"
        )
    
    # Check user's listing limit
    async with app.state.db_pool.acquire() as conn:
        user_listings = await conn.fetchval("""
            SELECT COUNT(*) FROM barter_listings 
            WHERE user_id = $1 AND status = 'active'
        """, current_user["id"])
        
        max_listings = settings.BARTER["max_listings_per_user"]
        if user_listings >= max_listings:
            raise HTTPException(
                status_code=400,
                detail=f"You can only have {max_listings} active listings"
            )
        
        # Check account age restriction
        account_age_days = settings.BARTER["restrictions"]["account_age_days"]
        if account_age_days > 0:
            user_age = await conn.fetchval("""
                SELECT DATE_PART('day', CURRENT_TIMESTAMP - created_at) 
                FROM users WHERE id = $1
            """, current_user["id"])
            
            if user_age < account_age_days:
                raise HTTPException(
                    status_code=400,
                    detail=f"Account must be at least {account_age_days} days old to list items"
                )
        
        # Create listing
        expires_at = datetime.now() + timedelta(
            days=settings.MARKET_CONFIG["marketplace"]["proposal_duration_days"]
        )
        
        listing = await conn.fetchrow("""
            INSERT INTO barter_listings 
            (user_id, title, description, category, points_price, expires_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """, current_user["id"], title, description, category, 
           Decimal(str(points_price)), expires_at)
        
        # Charge listing fee
        listing_fee = settings.MARKET_CONFIG["fees"]["listing_fee"]
        ledger = LedgerEngine(app.state.db_pool)
        
        await ledger.add_transaction(
            current_user["id"], "listing_fee", 
            Decimal(str(-listing_fee)),
            f"Listing fee for: {title}"
        )
        
        return {
            "message": "Listing created successfully",
            "listing": dict(listing),
            "fee_charged": listing_fee
        }

@router.post("/listings/{listing_id}/purchase")
async def purchase_listing(
    listing_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Purchase a listing"""
    async with app.state.db_pool.acquire() as conn:
        async with conn.transaction():
            # Get listing
            listing = await conn.fetchrow("""
                SELECT * FROM barter_listings 
                WHERE id = $1 AND status = 'active'
                FOR UPDATE
            """, listing_id)
            
            if not listing:
                raise HTTPException(
                    status_code=404,
                    detail="Listing not found or not active"
                )
            
            # Check if user is buying their own listing
            if listing["user_id"] == current_user["id"]:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot purchase your own listing"
                )
            
            # Check buyer's balance
            buyer_balance = await conn.fetchval("""
                SELECT points_balance FROM wallets WHERE user_id = $1
            """, current_user["id"])
            
            if buyer_balance < listing["points_price"]:
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient points balance"
                )
            
            # Calculate fees
            success_fee_percent = settings.MARKET_CONFIG["fees"]["success_fee_percent"]
            success_fee = listing["points_price"] * Decimal(str(success_fee_percent / 100))
            seller_receives = listing["points_price"] - success_fee
            
            # Create transaction record
            transaction = await conn.fetchrow("""
                INSERT INTO barter_transactions 
                (listing_id, buyer_id, seller_id, transaction_amount, fee_amount, status)
                VALUES ($1, $2, $3, $4, $5, 'pending')
                RETURNING *
            """, listing_id, current_user["id"], listing["user_id"],
               listing["points_price"], success_fee)
            
            # Update listing status
            await conn.execute("""
                UPDATE barter_listings 
                SET status = 'sold'
                WHERE id = $1
            """, listing_id)
            
            # Transfer points (via ledger)
            ledger = LedgerEngine(app.state.db_pool)
            
            # Deduct from buyer
            await ledger.add_transaction(
                current_user["id"], "market_purchase",
                -listing["points_price"],
                f"Purchase: {listing['title']}",
                reference_id=str(transaction["id"])
            )
            
            # Add to seller (minus fee)
            await ledger.add_transaction(
                listing["user_id"], "market_sale",
                seller_receives,
                f"Sale: {listing['title']}",
                reference_id=str(transaction["id"])
            )
            
            # Record fee collection
            await conn.execute("""
                INSERT INTO ledger 
                (user_id, transaction_type, amount, description, reference_id)
                VALUES (0, 'market_fee', $1, $2, $3)
            """, success_fee, f"Marketplace fee for transaction {transaction['id']}",
               str(transaction["id"]))
            
            return {
                "message": "Purchase successful",
                "transaction_id": transaction["id"],
                "amount_paid": float(listing["points_price"]),
                "fee_charged": float(success_fee),
                "seller_receives": float(seller_receives)
            }

@router.get("/my-listings")
async def get_my_listings(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get current user's listings"""
    async with app.state.db_pool.acquire() as conn:
        conditions = ["user_id = $1"]
        params = [current_user["id"]]
        
        if status:
            conditions.append("status = $2")
            params.append(status)
        
        where_clause = " AND ".join(conditions)
        
        listings = await conn.fetch(f"""
            SELECT * FROM barter_listings 
            WHERE {where_clause}
            ORDER BY created_at DESC
        """, *params)
        
        # Get stats
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_listings,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_listings,
                COUNT(CASE WHEN status = 'sold' THEN 1 END) as sold_listings,
                COALESCE(SUM(CASE WHEN status = 'sold' THEN points_price END), 0) as total_sales
            FROM barter_listings 
            WHERE user_id = $1
        """, current_user["id"])
        
        return {
            "listings": [dict(l) for l in listings],
            "stats": dict(stats) if stats else {}
        }

@router.get("/transactions")
async def get_market_transactions(
    role: str = "both",  # buyer, seller, both
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get user's marketplace transactions"""
    async with app.state.db_pool.acquire() as conn:
        conditions = []
        params = [current_user["id"]]
        
        if role == "buyer":
            conditions.append("buyer_id = $1")
        elif role == "seller":
            conditions.append("seller_id = $1")
        else:  # both
            conditions.append("(buyer_id = $1 OR seller_id = $1)")
        
        if status:
            conditions.append(f"status = ${len(params) + 1}")
            params.append(status)
        
        where_clause = " AND ".join(conditions)
        
        transactions = await conn.fetch(f"""
            SELECT 
                t.*,
                b.title as listing_title,
                b.category as listing_category,
                buyer.username as buyer_username,
                seller.username as seller_username
            FROM barter_transactions t
            JOIN barter_listings b ON t.listing_id = b.id
            JOIN users buyer ON t.buyer_id = buyer.id
            JOIN users seller ON t.seller_id = seller.id
            WHERE {where_clause}
            ORDER BY t.created_at DESC
        """, *params)
        
        # Calculate totals
        totals = await conn.fetchrow(f"""
            SELECT 
                COUNT(*) as total_transactions,
                COALESCE(SUM(transaction_amount), 0) as total_volume,
                COALESCE(SUM(fee_amount), 0) as total_fees
            FROM barter_transactions 
            WHERE {where_clause}
        """, *params)
        
        return {
            "transactions": [dict(t) for t in transactions],
            "totals": dict(totals) if totals else {}
        }

@router.post("/transactions/{transaction_id}/complete")
async def complete_transaction(
    transaction_id: int,
    rating: int = Body(..., ge=1, le=5),
    feedback: Optional[str] = Body(None),
    current_user: dict = Depends(get_current_user)
):
    """Complete a transaction and rate the other party"""
    async with app.state.db_pool.acquire() as conn:
        async with conn.transaction():
            # Get transaction
            transaction = await conn.fetchrow("""
                SELECT * FROM barter_transactions 
                WHERE id = $1 AND status = 'pending'
                FOR UPDATE
            """, transaction_id)
            
            if not transaction:
                raise HTTPException(
                    status_code=404,
                    detail="Transaction not found or not pending"
                )
            
            # Check if user is involved in transaction
            if (current_user["id"] != transaction["buyer_id"] and 
                current_user["id"] != transaction["seller_id"]):
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to complete this transaction"
                )
            
            # Determine which rating to update
            update_field = ""
            if current_user["id"] == transaction["buyer_id"]:
                update_field = "buyer_rating"
                other_party = transaction["seller_id"]
            else:
                update_field = "seller_rating"
                other_party = transaction["buyer_id"]
            
            # Check if already rated
            if transaction[update_field] is not None:
                raise HTTPException(
                    status_code=400,
                    detail="You have already rated this transaction"
                )
            
            # Update rating
            await conn.execute(f"""
                UPDATE barter_transactions 
                SET {update_field} = $1
                WHERE id = $2
            """, rating, transaction_id)
            
            # Check if both parties have rated
            updated = await conn.fetchrow("""
                SELECT buyer_rating, seller_rating 
                FROM barter_transactions WHERE id = $1
            """, transaction_id)
            
            # If both have rated, mark as completed
            if updated["buyer_rating"] is not None and updated["seller_rating"] is not None:
                await conn.execute("""
                    UPDATE barter_transactions 
                    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE id = $1
                """, transaction_id)
                
                # Award points to both parties for completing transaction
                scoring_rules = settings.SCORING_RULES
                if scoring_rules["actions"]["complete_barter"]["both_parties"]:
                    points = scoring_rules["actions"]["complete_barter"]["points"]
                    
                    # Award to buyer
                    await conn.execute("""
                        UPDATE wallets 
                        SET points_balance = points_balance + $1
                        WHERE user_id = $2
                    """, points, transaction["buyer_id"])
                    
                    # Award to seller
                    await conn.execute("""
                        UPDATE wallets 
                        SET points_balance = points_balance + $1
                        WHERE user_id = $2
                    """, points, transaction["seller_id"])
                    
                    # Log transactions
                    await conn.execute("""
                        INSERT INTO ledger 
                        (user_id, transaction_type, amount, description)
                        VALUES ($1, $2, $3, $4)
                    """, transaction["buyer_id"], "barter_completion", points,
                       "Completed marketplace transaction")
                    
                    await conn.execute("""
                        INSERT INTO ledger 
                        (user_id, transaction_type, amount, description)
                        VALUES ($1, $2, $3, $4)
                    """, transaction["seller_id"], "barter_completion", points,
                       "Completed marketplace transaction")
            
            return {
                "message": "Rating submitted successfully",
                "transaction_id": transaction_id,
                "rating": rating,
                "status": "completed" if updated["buyer_rating"] and updated["seller_rating"] else "pending_other_rating"
            }
