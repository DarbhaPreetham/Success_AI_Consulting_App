#!/usr/bin/env python3
import requests

def final_delete():
    try:
        # Get auth token
        auth_response = requests.post("https://successai.in/api/register", json={
            "email": "admin_final_delete@successai.in",
            "username": "admin_final_delete",
            "password": "AdminPass123!"
        })
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get all tools and find Loveable AI
            tools_response = requests.get("https://successai.in/api/tools")
            if tools_response.status_code == 200:
                tools = tools_response.json()
                
                loveable_tool = None
                for tool in tools:
                    if tool['name'] == 'Loveable AI' and 'loveable.ai' in tool['url']:
                        loveable_tool = tool
                        break
                
                if loveable_tool:
                    tool_id = loveable_tool['id']
                    print(f"🎯 Found Loveable AI to delete: {tool_id}")
                    
                    # Delete using new endpoint
                    delete_response = requests.delete(f"https://successai.in/api/tools/{tool_id}", headers=headers)
                    
                    if delete_response.status_code == 200:
                        print("✅ Successfully deleted Loveable AI!")
                    else:
                        print(f"❌ Delete failed: {delete_response.status_code} - {delete_response.text}")
                else:
                    print("ℹ️  Loveable AI not found (may already be removed)")
                
                # Final verification
                print("\n📊 Final status check:")
                final_tools = requests.get("https://successai.in/api/tools").json()
                love_tools = [t for t in final_tools if 'love' in t['name'].lower()]
                
                print(f"Total tools: {len(final_tools)}")
                print(f"Lovable-related tools: {len(love_tools)}")
                for tool in love_tools:
                    status = "✅" if "lovable.dev" in tool['url'] else "❌"
                    print(f"  {status} {tool['name']}: {tool['url']}")
                    
            else:
                print(f"❌ Failed to get tools: {tools_response.status_code}")
        else:
            print(f"❌ Auth failed: {auth_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    final_delete()