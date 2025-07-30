#!/usr/bin/env python3
import requests

def remove_old_loveable_via_tools_check():
    """Remove old Loveable AI by checking URL"""
    try:
        # Get all tools
        response = requests.get("https://successai.in/api/tools")
        if response.status_code == 200:
            tools = response.json()
            
            # Find tools with wrong Loveable info
            old_loveable_tools = []
            correct_lovable_tools = []
            
            for tool in tools:
                if "love" in tool['name'].lower():
                    if "loveable.ai" in tool.get('url', ''):
                        old_loveable_tools.append(tool)
                        print(f"❌ Found old tool to remove: {tool['name']} - {tool['url']}")
                    elif "lovable.dev" in tool.get('url', ''):
                        correct_lovable_tools.append(tool)
                        print(f"✅ Found correct tool to keep: {tool['name']} - {tool['url']}")
            
            print(f"\n📊 Summary:")
            print(f"   - Old tools to remove: {len(old_loveable_tools)}")
            print(f"   - Correct tools to keep: {len(correct_lovable_tools)}")
            
            return len(old_loveable_tools), len(correct_lovable_tools)
        else:
            print(f"❌ Failed to get tools: {response.status_code}")
            return 0, 0
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0, 0

if __name__ == "__main__":
    remove_old_loveable_via_tools_check()