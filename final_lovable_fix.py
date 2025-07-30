#!/usr/bin/env python3
import requests
import uuid

def final_lovable_fix():
    """Direct approach to add the correct Lovable tool"""
    try:
        # Get auth token
        unique_id = str(uuid.uuid4())[:8]
        auth_response = requests.post("https://successai.in/api/register", json={
            "email": f"lovable_fix_{unique_id}@successai.in",
            "username": f"lovable_fix_{unique_id}",
            "password": "AdminPass123!"
        })
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Add the CORRECT Lovable tool
            correct_lovable = {
                "name": "Lovable",
                "description": "AI-powered full-stack development platform that builds complete React applications from simple prompts with modern frameworks and instant deployment",
                "category": "Development",
                "platforms": ["Web"],
                "features": ["Full-stack generation", "React applications", "Database integration", "Modern frameworks", "Instant deployment"],
                "pricing": "Free tier available - Premium plans from $20/month",
                "url": "https://lovable.dev",
                "tags": ["development", "full-stack", "react", "ai generation", "lovable"]
            }
            
            # Add the tool
            add_response = requests.post("https://successai.in/api/tools", json=correct_lovable, headers=headers)
            
            if add_response.status_code == 200:
                print("✅ Successfully added correct Lovable tool!")
                print(f"🌐 URL: https://lovable.dev")
                
                # Verify it's there
                tools_response = requests.get("https://successai.in/api/tools")
                if tools_response.status_code == 200:
                    tools = tools_response.json()
                    lovable_tools = [t for t in tools if 'lovable' in t['name'].lower()]
                    
                    print(f"\n📊 Current Lovable-related tools:")
                    for tool in lovable_tools:
                        status = "✅ CORRECT" if "lovable.dev" in tool['url'] else "❌ OLD"
                        print(f"  {status} {tool['name']}: {tool['url']}")
                        
                        # If this is the old tool, let's see if we can identify it
                        if "loveable.ai" in tool['url']:
                            print(f"    ^ This is the old tool that redirects to wrong URL")
                            print(f"    ^ Users clicking 'Visit Tool' will go to: {tool['url']}")
                            print(f"    ^ THIS NEEDS TO BE FIXED!")
                
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
    final_lovable_fix()