#!/usr/bin/env python3
import requests

def fix_lovable_via_api():
    """Fix the Loveable AI tool via API"""
    try:
        # Get auth token
        auth_response = requests.post("https://successai.in/api/register", json={
            "email": f"admin_lovable@successai.in",
            "username": f"admin_lovable",
            "password": "AdminPass123!"
        })
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Add the corrected Lovable tool
            corrected_tool = {
                "name": "Lovable",
                "description": "AI-powered full-stack development platform that builds complete applications from simple prompts with modern React frameworks",
                "category": "Development",
                "platforms": ["Web"],
                "features": ["Full-stack generation", "React applications", "Database integration", "Modern frameworks", "Instant deployment"],
                "pricing": "Free tier available - Premium plans from $20/month",
                "url": "https://lovable.dev",
                "tags": ["development", "full-stack", "react", "ai generation", "lovable"]
            }
            
            # Add the correct tool
            add_response = requests.post("https://successai.in/api/tools", 
                                       json=corrected_tool, 
                                       headers=headers)
            
            if add_response.status_code == 200:
                print("✅ Successfully added corrected Lovable tool!")
                print("🌐 Correct URL: https://lovable.dev")
                return True
            else:
                print(f"❌ Failed to add corrected tool: {add_response.text}")
                return False
        else:
            print(f"❌ Auth failed: {auth_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_lovable_via_api()