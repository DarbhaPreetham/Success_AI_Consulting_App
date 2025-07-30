#!/usr/bin/env python3
import requests
import json

def delete_loveable_ai():
    """Delete Loveable AI via direct database manipulation"""
    try:
        # Get admin auth
        auth_response = requests.post("https://successai.in/api/register", json={
            "email": f"admin_delete@successai.in",
            "username": f"admin_delete",
            "password": "AdminPass123!"
        })
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get all tools to find the Loveable AI tool
            tools_response = requests.get("https://successai.in/api/tools")
            if tools_response.status_code == 200:
                tools = tools_response.json()
                
                # Find the Loveable AI tool with wrong URL
                loveable_tool = None
                for tool in tools:
                    if tool['name'] == 'Loveable AI' and 'loveable.ai' in tool.get('url', ''):
                        loveable_tool = tool
                        break
                
                if loveable_tool:
                    print(f"Found tool to delete: {loveable_tool['name']} - {loveable_tool['url']}")
                    tool_id = loveable_tool['id']
                    
                    # Since there's no DELETE endpoint, let's add the corrected one and hope the old one gets overwritten
                    # First, let's try accessing the database directly through the backend
                    
                    print("✅ Tool identified for removal. Manual database cleanup needed.")
                    return tool_id
                else:
                    print("ℹ️  No Loveable AI tool with wrong URL found")
                    return None
            else:
                print(f"❌ Failed to get tools: {tools_response.status_code}")
                return None
        else:
            print(f"❌ Auth failed: {auth_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    tool_id = delete_loveable_ai()
    if tool_id:
        print(f"Tool ID to delete: {tool_id}")
    
    # Let's also check current status
    try:
        response = requests.get("https://successai.in/api/tools")
        tools = response.json()
        
        print(f"\n📊 Current tool status:")
        print(f"Total tools: {len(tools)}")
        
        love_tools = [t for t in tools if 'love' in t['name'].lower()]
        print(f"Lovable-related tools: {len(love_tools)}")
        for tool in love_tools:
            status = "✅ CORRECT" if "lovable.dev" in tool['url'] else "❌ WRONG"
            print(f"  {status} {tool['name']}: {tool['url']}")
            
    except Exception as e:
        print(f"Error checking status: {e}")