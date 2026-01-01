#!/usr/bin/env python3
"""
Script to backup ledger data
"""
import asyncpg
import json
from datetime import datetime
import os

async def backup_ledger():
    """Backup ledger data to JSON file"""
    try:
        # Database connection
        conn = await asyncpg.connect(
            user='prediction_user',
            password='prediction_pass',
            database='prediction_db',
            host='localhost'
        )
        
        # Get all ledger data
        records = await conn.fetch("""
            SELECT * FROM ledger 
            ORDER BY created_at DESC
        """)
        
        # Convert to dictionary
        data = []
        for record in records:
            data.append(dict(record))
        
        # Create backup directory if not exists
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{backup_dir}/ledger_backup_{timestamp}.json"
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✅ Backup created: {filename}")
        print(f"📊 Records backed up: {len(data)}")
        
        # Close connection
        await conn.close()
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(backup_ledger())
