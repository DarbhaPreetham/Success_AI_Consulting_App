#!/usr/bin/env python3
import requests
import uuid

def clean_delete():
    try:
        # Generate unique email
        unique_id = str(uuid.uuid4())[:8]
        email = f"admin_{unique_id}@successai.in"
        
        # Get auth token
        auth_response = requests.post("https://successai.in/api/register", json={
            "email": email,
            "username": f"admin_{unique_id}",
            "password": "AdminPass123!"
        })
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get the Loveable AI tool
            tools_response = requests.get("https://successai.in/api/tools")
            tools = tools_response.json()
            
            loveable_tool = None
            for tool in tools:
                if tool['name'] == 'Loveable AI' and 'loveable.ai' in tool['url']:
                    loveable_tool = tool
                    break
            
            if loveable_tool:
                tool_id = loveable_tool['id']
                print(f"🎯 Attempting to delete tool: {tool_id}")
                
                # Try DELETE request
                delete_response = requests.delete(f"https://successai.in/api/tools/{tool_id}", headers=headers)
                print(f"DELETE response: {delete_response.status_code}")
                print(f"DELETE text: {delete_response.text}")
                
                # Verify
                final_check = requests.get("https://successai.in/api/tools").json()
                remaining_loveable = [t for t in final_check if t['name'] == 'Loveable AI']
                
                if len(remaining_loveable) == 0:
                    print("✅ SUCCESS: Loveable AI removed!")
                else:
                    print(f"❌ Still exists: {len(remaining_loveable)} Loveable AI tools")
                    
            else:
                print("✅ Loveable AI already removed!")
                
        else:
            print(f"❌ Auth failed: {auth_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_delete()