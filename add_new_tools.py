#!/usr/bin/env python3
import requests
import uuid
from datetime import datetime

# Your API endpoint
API_URL = "https://successai.in/api"

def add_tool(tool_data):
    """Add a new tool to the database"""
    try:
        # First register a user to get auth token
        register_response = requests.post(f"{API_URL}/register", json={
            "email": f"admin_{uuid.uuid4().hex[:8]}@successai.in",
            "username": f"admin_{uuid.uuid4().hex[:8]}",
            "password": "AdminPass123!"
        })
        
        if register_response.status_code == 200:
            token = register_response.json()["access_token"]
            
            # Add the tool
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(f"{API_URL}/tools", json=tool_data, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ Successfully added {tool_data['name']}")
                return True
            else:
                print(f"❌ Failed to add {tool_data['name']}: {response.text}")
                return False
        else:
            print(f"❌ Authentication failed: {register_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error adding {tool_data['name']}: {e}")
        return False

# New AI Tools Data
new_tools = [
    {
        "name": "Google Gemini",
        "description": "Google's most capable AI model with advanced reasoning, coding, and multimodal capabilities including text, image, and video understanding",
        "category": "General AI",
        "platforms": ["Web", "API", "Mobile"],
        "features": ["Advanced reasoning", "Code generation", "Multimodal AI", "Image analysis", "Long context understanding"],
        "pricing": "Free tier available - $20/month for advanced features",
        "url": "https://gemini.google.com",
        "tags": ["google", "ai", "multimodal", "reasoning", "coding"]
    },
    {
        "name": "Grok AI",
        "description": "Elon Musk's witty and rebellious AI assistant with real-time information access and humor-infused responses",
        "category": "General AI",
        "platforms": ["Web", "Mobile"],
        "features": ["Real-time information", "Witty responses", "Current events", "Twitter integration", "Uncensored AI"],
        "pricing": "Premium subscription - $8/month with X Premium",
        "url": "https://x.ai/grok",
        "tags": ["elon musk", "twitter", "real-time", "humor", "uncensored"]
    },
    {
        "name": "Claude AI",
        "description": "Anthropic's advanced AI assistant known for safety, helpfulness, and detailed analytical responses with large context windows",
        "category": "General AI", 
        "platforms": ["Web", "API"],
        "features": ["200K context window", "Safe AI responses", "Document analysis", "Code assistance", "Research help"],
        "pricing": "Free tier - $20/month for Claude Pro",
        "url": "https://claude.ai",
        "tags": ["anthropic", "safety", "analysis", "large context", "research"]
    },
    {
        "name": "Perplexity AI",
        "description": "AI-powered answer engine that provides accurate, sourced answers with real-time web search and citation capabilities",
        "category": "Search & Research",
        "platforms": ["Web", "Mobile", "API"],
        "features": ["Real-time search", "Source citations", "Academic research", "Pro search", "Follow-up questions"],
        "pricing": "Free tier - $20/month for Pro features",
        "url": "https://perplexity.ai",
        "tags": ["search", "research", "citations", "real-time", "academic"]
    },
    {
        "name": "Meta AI",
        "description": "Meta's AI assistant integrated across Facebook, Instagram, and WhatsApp with image generation and smart assistance",
        "category": "General AI",
        "platforms": ["Web", "Mobile", "Social Media"],
        "features": ["Social media integration", "Image generation", "Real-time assistance", "Multi-platform", "Creative tools"],
        "pricing": "Free with Meta platforms",
        "url": "https://www.meta.ai",
        "tags": ["meta", "facebook", "instagram", "social media", "integration"]
    },
    {
        "name": "Canva AI",
        "description": "AI-powered design platform with text-to-image generation, background removal, and intelligent design suggestions",
        "category": "Design & Creative",
        "platforms": ["Web", "Mobile", "Desktop"],
        "features": ["AI image generation", "Magic eraser", "Background removal", "Design templates", "Brand kit"],
        "pricing": "Free tier - $15/month for Pro features",
        "url": "https://canva.com",
        "tags": ["design", "graphics", "templates", "ai generation", "creative"]
    },
    {
        "name": "Loveable AI",
        "description": "AI-powered full-stack development platform that builds complete applications from simple prompts with modern frameworks",
        "category": "Development",
        "platforms": ["Web"],
        "features": ["Full-stack generation", "React applications", "Database integration", "Modern frameworks", "Deployment ready"],
        "pricing": "Subscription-based - Contact for pricing",
        "url": "https://loveable.ai",
        "tags": ["development", "full-stack", "react", "ai generation", "deployment"]
    },
    {
        "name": "Bolt.new",
        "description": "AI-powered web development platform that creates, edits, and deploys full-stack applications instantly from natural language",
        "category": "Development",
        "platforms": ["Web"],
        "features": ["Instant web apps", "Full-stack development", "Real-time editing", "One-click deployment", "Modern tech stack"],
        "pricing": "Usage-based pricing - Free tier available",
        "url": "https://bolt.new",
        "tags": ["web development", "instant", "deployment", "full-stack", "modern"]
    },
    {
        "name": "Emergent AI",
        "description": "Advanced AI agent platform for building complete applications with intelligent automation and multi-agent collaboration",
        "category": "Development",
        "platforms": ["Web"],
        "features": ["AI agents", "Multi-agent systems", "Application building", "Automation", "Integration platform"],
        "pricing": "Subscription tiers - Free tier available",
        "url": "https://app.emergent.sh",
        "tags": ["ai agents", "automation", "multi-agent", "platform", "building"]
    }
]

def main():
    print("🚀 Adding new AI tools to SuccessAI.in...")
    print("=" * 60)
    
    success_count = 0
    total_count = len(new_tools)
    
    for tool in new_tools:
        if add_tool(tool):
            success_count += 1
    
    print("=" * 60)
    print(f"✅ Successfully added {success_count}/{total_count} tools!")
    print(f"🌐 Your updated application is live at: https://successai.in/tools")
    
if __name__ == "__main__":
    main()