#!/usr/bin/env python3
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
from dotenv import load_dotenv

async def complete_database_cleanup():
    """Clean up all duplicates and fix URLs"""
    load_dotenv()
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'ai_tools_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        print("🧹 Starting complete database cleanup...")
        
        # Step 1: Remove ALL tools except the original 5 base tools
        base_tools = ["Cursor AI", "ChatGPT", "DALL-E 3", "GitHub Copilot", "Midjourney"]
        
        # Get all tools
        all_tools = await db.ai_tools.find({}).to_list(100)
        print(f"Found {len(all_tools)} total tools")
        
        # Remove all non-base tools
        result = await db.ai_tools.delete_many({
            "name": {"$nin": base_tools}
        })
        print(f"✅ Removed {result.deleted_count} duplicate/extra tools")
        
        # Step 2: Update Cursor AI to correct URL
        cursor_update = await db.ai_tools.update_one(
            {"name": "Cursor AI"},
            {
                "$set": {
                    "url": "https://cursor.com",
                    "description": "AI-powered coding assistant for faster development with intelligent code completion and real-time collaboration"
                }
            }
        )
        
        if cursor_update.modified_count > 0:
            print("✅ Updated Cursor AI URL to cursor.com")
        
        # Step 3: Add back the corrected new tools (one of each)
        new_tools = [
            {
                "name": "Google Gemini",
                "description": "Google's most capable AI model with advanced reasoning, coding, and multimodal capabilities",
                "category": "General AI",
                "platforms": ["Web", "API", "Mobile"],
                "features": ["Advanced reasoning", "Code generation", "Multimodal AI", "Image analysis"],
                "pricing": "Free tier available - $20/month for advanced features",
                "url": "https://gemini.google.com",
                "rating": 4.7,
                "review_count": 800,
                "tags": ["google", "ai", "multimodal", "reasoning"]
            },
            {
                "name": "Grok AI", 
                "description": "Elon Musk's witty AI assistant with real-time information access and humor-infused responses",
                "category": "General AI",
                "platforms": ["Web", "Mobile"],
                "features": ["Real-time information", "Witty responses", "Current events", "Twitter integration"],
                "pricing": "Premium subscription - $8/month with X Premium",
                "url": "https://x.ai/grok",
                "rating": 4.3,
                "review_count": 500,
                "tags": ["twitter", "real-time", "humor", "elon musk"]
            },
            {
                "name": "Claude AI",
                "description": "Anthropic's advanced AI assistant known for safety, helpfulness, and detailed analytical responses",
                "category": "General AI",
                "platforms": ["Web", "API"],
                "features": ["200K context window", "Safe AI responses", "Document analysis", "Code assistance"],
                "pricing": "Free tier - $20/month for Claude Pro",
                "url": "https://claude.ai",
                "rating": 4.6,
                "review_count": 1200,
                "tags": ["anthropic", "safety", "analysis", "large context"]
            },
            {
                "name": "Perplexity AI",
                "description": "AI-powered answer engine that provides accurate, sourced answers with real-time web search capabilities",
                "category": "Search & Research", 
                "platforms": ["Web", "Mobile", "API"],
                "features": ["Real-time search", "Source citations", "Academic research", "Pro search"],
                "pricing": "Free tier - $20/month for Pro features",
                "url": "https://perplexity.ai",
                "rating": 4.5,
                "review_count": 600,
                "tags": ["search", "research", "citations", "real-time"]
            },
            {
                "name": "Meta AI",
                "description": "Meta's AI assistant integrated across Facebook, Instagram, and WhatsApp with image generation",
                "category": "General AI",
                "platforms": ["Web", "Mobile", "Social Media"],
                "features": ["Social media integration", "Image generation", "Multi-platform", "Creative tools"],
                "pricing": "Free with Meta platforms",
                "url": "https://www.meta.ai",
                "rating": 4.2,
                "review_count": 300,
                "tags": ["meta", "facebook", "instagram", "social media"]
            },
            {
                "name": "Canva AI",
                "description": "AI-powered design platform with text-to-image generation, background removal, and intelligent design suggestions",
                "category": "Design & Creative",
                "platforms": ["Web", "Mobile", "Desktop"],
                "features": ["AI image generation", "Magic eraser", "Background removal", "Design templates"],
                "pricing": "Free tier - $15/month for Pro features", 
                "url": "https://canva.com",
                "rating": 4.4,
                "review_count": 2000,
                "tags": ["design", "graphics", "templates", "ai generation"]
            },
            {
                "name": "Lovable",
                "description": "AI-powered full-stack development platform that builds complete React applications from simple prompts",
                "category": "Development",
                "platforms": ["Web"],
                "features": ["Full-stack generation", "React applications", "Database integration", "Instant deployment"],
                "pricing": "Free tier available - Premium plans from $20/month",
                "url": "https://lovable.dev",
                "rating": 4.6,
                "review_count": 150,
                "tags": ["development", "full-stack", "react", "lovable"]
            },
            {
                "name": "Bolt.new",
                "description": "AI-powered web development platform that creates, edits, and deploys full-stack applications instantly",
                "category": "Development", 
                "platforms": ["Web"],
                "features": ["Instant web apps", "Full-stack development", "Real-time editing", "One-click deployment"],
                "pricing": "Usage-based pricing - Free tier available",
                "url": "https://bolt.new",
                "rating": 4.5,
                "review_count": 200,
                "tags": ["web development", "instant", "deployment", "full-stack"]
            },
            {
                "name": "Emergent AI",
                "description": "Advanced AI agent platform for building complete applications with intelligent automation",
                "category": "Development",
                "platforms": ["Web"],
                "features": ["AI agents", "Multi-agent systems", "Application building", "Automation"],
                "pricing": "Subscription tiers - Free tier available",
                "url": "https://app.emergent.sh",
                "rating": 4.7,
                "review_count": 100,
                "tags": ["ai agents", "automation", "platform", "emergent"]
            }
        ]
        
        # Insert each new tool
        for tool in new_tools:
            # Check if it already exists
            existing = await db.ai_tools.find_one({"name": tool["name"]})
            if not existing:
                # Add missing fields
                import uuid
                from datetime import datetime
                tool["id"] = str(uuid.uuid4())
                tool["created_at"] = datetime.utcnow()
                
                await db.ai_tools.insert_one(tool)
                print(f"✅ Added {tool['name']}")
            else:
                print(f"ℹ️  {tool['name']} already exists")
        
        # Final verification
        final_tools = await db.ai_tools.find({}).to_list(100)
        print(f"\n📊 Final status: {len(final_tools)} unique tools")
        
        # Show all tools with their URLs
        print("\n📋 Final tool list:")
        for tool in sorted(final_tools, key=lambda x: x['name']):
            print(f"   ✅ {tool['name']}: {tool['url']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(complete_database_cleanup())