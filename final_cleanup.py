#!/usr/bin/env python3
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio

async def remove_wrong_loveable():
    """Remove the Loveable AI with wrong URL"""
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'ai_tools_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Remove the tool with wrong URL
        result = await db.ai_tools.delete_many({
            "name": "Loveable AI",
            "url": "https://loveable.ai"
        })
        
        if result.deleted_count > 0:
            print(f"✅ Successfully removed {result.deleted_count} 'Loveable AI' entries with wrong URL")
        else:
            print("ℹ️  No matching entries found to remove")
            
        # Verify what's left
        remaining_love_tools = await db.ai_tools.find({
            "name": {"$regex": "love", "$options": "i"}
        }).to_list(10)
        
        print(f"\n📋 Remaining love-related tools:")
        for tool in remaining_love_tools:
            print(f"   ✅ {tool['name']}: {tool['url']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(remove_wrong_loveable())