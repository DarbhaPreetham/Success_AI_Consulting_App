#!/usr/bin/env python3
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
from dotenv import load_dotenv

async def fix_cursor_url():
    """Update Cursor AI to redirect to correct cursor.com"""
    load_dotenv()
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'ai_tools_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Update Cursor AI URL
        result = await db.ai_tools.update_many(
            {"name": "Cursor AI"},
            {
                "$set": {
                    "url": "https://cursor.com",
                    "description": "AI-powered coding assistant for faster development with intelligent code completion and real-time collaboration"
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Successfully updated {result.modified_count} Cursor AI tool(s) to redirect to cursor.com")
        else:
            print("ℹ️  No Cursor AI tools found to update")
        
        # Verify the update
        cursor_tools = await db.ai_tools.find({"name": "Cursor AI"}).to_list(10)
        print(f"\n📋 Cursor AI tools now:")
        for tool in cursor_tools:
            print(f"   ✅ {tool['name']}: {tool['url']}")
            
    except Exception as e:
        print(f"❌ Error updating tool: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_cursor_url())