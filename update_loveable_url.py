#!/usr/bin/env python3
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
from dotenv import load_dotenv

async def update_loveable_to_correct_url():
    """Update Loveable AI to redirect to lovable.dev"""
    load_dotenv()
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'ai_tools_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Update the Loveable AI tool with correct URL and info
        result = await db.ai_tools.update_many(
            {"name": "Loveable AI"},
            {
                "$set": {
                    "name": "Lovable",
                    "description": "AI-powered full-stack development platform that builds complete applications from simple prompts with modern React frameworks",
                    "url": "https://lovable.dev",
                    "pricing": "Free tier available - Premium plans from $20/month",
                    "features": ["Full-stack generation", "React applications", "Database integration", "Modern frameworks", "Instant deployment"],
                    "tags": ["development", "full-stack", "react", "ai generation", "lovable"]
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Successfully updated {result.modified_count} Loveable AI tool(s) to redirect to lovable.dev")
        else:
            print("ℹ️  No Loveable AI tools found to update")
        
        # Verify the update
        updated_tools = await db.ai_tools.find({"url": "https://lovable.dev"}).to_list(10)
        print(f"\n📋 Tools now redirecting to lovable.dev:")
        for tool in updated_tools:
            print(f"   ✅ {tool['name']}: {tool['url']}")
            
        # Check if any old URLs remain
        old_urls = await db.ai_tools.find({"url": {"$regex": "loveable.ai"}}).to_list(10)
        if old_urls:
            print(f"\n⚠️  Still found {len(old_urls)} tools with old loveable.ai URL")
        else:
            print(f"\n✅ No more tools with old loveable.ai URL!")
            
    except Exception as e:
        print(f"❌ Error updating tool: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_loveable_to_correct_url())