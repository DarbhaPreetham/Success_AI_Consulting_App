#!/usr/bin/env python3
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio

async def remove_loveable_ai():
    """Remove the old Loveable AI entry, keeping only Lovable"""
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'ai_tools_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Remove the old "Loveable AI" tool
        result = await db.ai_tools.delete_many({"name": "Loveable AI"})
        
        if result.deleted_count > 0:
            print(f"✅ Successfully removed {result.deleted_count} 'Loveable AI' entries")
        else:
            print("ℹ️  No 'Loveable AI' entries found to remove")
            
        # Show remaining tools with "Lovable" in name
        remaining_tools = await db.ai_tools.find({"name": {"$regex": "Lovable", "$options": "i"}}).to_list(10)
        print(f"📋 Remaining Lovable-related tools:")
        for tool in remaining_tools:
            print(f"   - {tool['name']}: {tool['url']}")
            
    except Exception as e:
        print(f"❌ Error removing tool: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(remove_loveable_ai())