#!/usr/bin/env python3
import requests
import uuid

def add_correct_cursor():
    """Add correct Cursor AI tool via API"""
    try:
        # Get auth token
        unique_id = str(uuid.uuid4())[:8]
        auth_response = requests.post("https://successai.in/api/register", json={
            "email": f"cursor_fix_{unique_id}@successai.in",
            "username": f"cursor_fix_{unique_id}",
            "password": "AdminPass123!"
        })
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Add the CORRECT Cursor AI tool
            correct_cursor = {
                "name": "Cursor",
                "description": "AI-powered coding assistant for faster development with intelligent code completion, real-time collaboration, and advanced debugging support",
                "category": "Development",
                "platforms": ["Web", "Desktop"],
                "features": ["Code completion", "Real-time collaboration", "Debugging support", "Multi-language support", "AI pair programming"],
                "pricing": "Free tier available - $20/month for premium features",
                "url": "https://cursor.com",
                "tags": ["coding", "ai", "productivity", "development", "cursor"]
            }
            
            # Add the tool
            add_response = requests.post("https://successai.in/api/tools", json=correct_cursor, headers=headers)
            
            if add_response.status_code == 200:
                print("✅ Successfully added correct Cursor tool!")
                print(f"🌐 URL: https://cursor.com")
                
                # Verify current cursor tools
                tools_response = requests.get("https://successai.in/api/tools")
                if tools_response.status_code == 200:
                    tools = tools_response.json()
                    cursor_tools = [t for t in tools if 'cursor' in t['name'].lower()]
                    
                    print(f"\n📊 Current Cursor-related tools:")
                    for tool in cursor_tools:
                        status = "✅ CORRECT" if "cursor.com" in tool['url'] else "❌ OLD"
                        print(f"  {status} {tool['name']}: {tool['url']}")
                
                return True
            else:
                print(f"❌ Failed to add tool: {add_response.status_code} - {add_response.text}")
                return False
        else:
            print(f"❌ Auth failed: {auth_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    add_correct_cursor()