#!/usr/bin/env python3
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
from dotenv import load_dotenv

async def fix_loveable_redirect():
    """Update Loveable AI tool to redirect to correct lovable.dev"""
    load_dotenv()
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')  
    db_name = os.environ.get('DB_NAME', 'ai_tools_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Find the specific tool by ID
        tool_id = "92587bdb-b1b0-4ce9-9852-06d05bb5eb59"
        
        # Update the tool to redirect to lovable.dev
        update_result = await db.ai_tools.update_one(
            {"id": tool_id},
            {
                "$set": {
                    "name": "Lovable",
                    "url": "https://lovable.dev",
                    "description": "AI-powered full-stack development platform that builds complete applications from simple prompts with modern React frameworks",
                    "pricing": "Free tier available - Premium plans from $20/month"
                }
            }
        )
        
        if update_result.modified_count > 0:
            print(f"✅ Successfully updated Loveable AI to redirect to lovable.dev!")
            print(f"   - Tool ID: {tool_id}")
            print(f"   - New URL: https://lovable.dev")
            print(f"   - New Name: Lovable")
        else:
            print(f"❌ Tool with ID {tool_id} not found in local database")
            
        # Also try updating by name and old URL as backup
        backup_result = await db.ai_tools.update_many(
            {
                "$or": [
                    {"name": "Loveable AI"},
                    {"url": "https://loveable.ai"}
                ]
            },
            {
                "$set": {
                    "name": "Lovable",
                    "url": "https://lovable.dev",
                    "description": "AI-powered full-stack development platform that builds complete applications from simple prompts with modern React frameworks",
                    "pricing": "Free tier available - Premium plans from $20/month"
                }
            }
        )
        
        if backup_result.modified_count > 0:
            print(f"✅ Backup update successful: {backup_result.modified_count} tools updated")
        
        # Verify the changes
        verification_tools = await db.ai_tools.find({"url": "https://lovable.dev"}).to_list(10)
        print(f"\n📋 Tools now redirecting to lovable.dev: {len(verification_tools)}")
        for tool in verification_tools:
            print(f"   ✅ {tool['name']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_loveable_redirect())