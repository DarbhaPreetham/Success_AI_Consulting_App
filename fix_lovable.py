#!/usr/bin/env python3
import requests
import json
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
from datetime import datetime

async def fix_lovable_tool():
    """Fix the Loveable AI tool to be Lovable with correct URL"""
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'ai_tools_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Find and update the Loveable AI tool
        result = await db.ai_tools.update_one(
            {"name": "Loveable AI"},
            {
                "$set": {
                    "name": "Lovable",
                    "description": "AI-powered full-stack development platform that builds complete applications from simple prompts with modern frameworks",
                    "category": "Development", 
                    "platforms": ["Web"],
                    "features": ["Full-stack generation", "React applications", "Database integration", "Modern frameworks", "Deployment ready"],
                    "pricing": "Subscription-based - Free tier available",
                    "url": "https://lovable.dev",
                    "tags": ["development", "full-stack", "react", "ai generation", "deployment"]
                }
            }
        )
        
        if result.modified_count > 0:
            print("✅ Successfully updated Loveable AI to Lovable with correct URL!")
            print("🌐 New URL: https://lovable.dev")
        else:
            print("❌ Tool not found or no changes made")
            
    except Exception as e:
        print(f"❌ Error updating tool: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_lovable_tool())