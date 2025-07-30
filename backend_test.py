import requests
import sys
import json
from datetime import datetime

class AIToolsAPITester:
    def __init__(self, base_url="https://4627abdd-3473-435e-b584-0308dd257186.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                try:
                    error_data = response.json()
                    details += f", Response: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {"status": "success"}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_health_check(self):
        """Test API health check"""
        result = self.run_test("Health Check", "GET", "", 200)
        return result is not None

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_data = {
            "email": f"test_user_{timestamp}@example.com",
            "username": f"testuser_{timestamp}",
            "password": "TestPass123!"
        }
        
        result = self.run_test("User Registration", "POST", "register", 200, test_data)
        if result and 'access_token' in result:
            self.token = result['access_token']
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        # First register a user
        timestamp = datetime.now().strftime('%H%M%S')
        register_data = {
            "email": f"login_test_{timestamp}@example.com",
            "username": f"loginuser_{timestamp}",
            "password": "LoginTest123!"
        }
        
        # Register user
        register_result = self.run_test("Pre-Login Registration", "POST", "register", 200, register_data)
        if not register_result:
            return False
        
        # Now test login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        result = self.run_test("User Login", "POST", "login", 200, login_data)
        if result and 'access_token' in result:
            self.token = result['access_token']  # Update token for subsequent tests
            return True
        return False

    def test_get_user_info(self):
        """Test getting current user info"""
        if not self.token:
            self.log_test("Get User Info", False, "No authentication token available")
            return False
        
        result = self.run_test("Get User Info", "GET", "me", 200)
        return result is not None

    def test_get_tools(self):
        """Test getting all tools"""
        result = self.run_test("Get All Tools", "GET", "tools", 200)
        if result and isinstance(result, list) and len(result) > 0:
            print(f"   Found {len(result)} tools in database")
            return True
        return False

    def test_get_tools_with_filters(self):
        """Test getting tools with filters"""
        # Test category filter
        result = self.run_test("Get Tools by Category", "GET", "tools?category=Development", 200)
        success1 = result is not None
        
        # Test search filter
        result = self.run_test("Get Tools by Search", "GET", "tools?search=AI", 200)
        success2 = result is not None
        
        # Test platform filter
        result = self.run_test("Get Tools by Platform", "GET", "tools?platform=Web", 200)
        success3 = result is not None
        
        return success1 and success2 and success3

    def test_get_categories(self):
        """Test getting tool categories"""
        result = self.run_test("Get Categories", "GET", "categories", 200)
        if result and 'categories' in result and len(result['categories']) > 0:
            print(f"   Found categories: {result['categories']}")
            return True
        return False

    def test_ai_recommendations(self):
        """Test AI-powered recommendations"""
        if not self.token:
            self.log_test("AI Recommendations", False, "No authentication token available")
            return False
        
        recommendation_data = {
            "requirements": "I need an AI tool for coding assistance with real-time collaboration",
            "preferred_platforms": ["Web", "Desktop"],
            "use_case": "development"
        }
        
        result = self.run_test("AI Recommendations", "POST", "recommendations", 200, recommendation_data)
        if result and 'tools' in result and 'reasoning' in result:
            print(f"   Got {len(result['tools'])} recommendations")
            print(f"   Reasoning: {result['reasoning'][:100]}...")
            return True
        return False

    def test_favorites_system(self):
        """Test favorites add/remove/get functionality"""
        if not self.token:
            self.log_test("Favorites System", False, "No authentication token available")
            return False
        
        # First get a tool ID
        tools_result = self.run_test("Get Tools for Favorites Test", "GET", "tools?limit=1", 200)
        if not tools_result or len(tools_result) == 0:
            self.log_test("Favorites System", False, "No tools available for testing")
            return False
        
        tool_id = tools_result[0]['id']
        
        # Add to favorites
        add_result = self.run_test("Add to Favorites", "POST", f"favorites/{tool_id}", 200)
        success1 = add_result is not None
        
        # Get favorites
        get_result = self.run_test("Get Favorites", "GET", "favorites", 200)
        success2 = get_result is not None and 'tools' in get_result
        
        # Remove from favorites
        remove_result = self.run_test("Remove from Favorites", "DELETE", f"favorites/{tool_id}", 200)
        success3 = remove_result is not None
        
        return success1 and success2 and success3

    def test_tool_creation(self):
        """Test creating a new tool (requires authentication)"""
        if not self.token:
            self.log_test("Tool Creation", False, "No authentication token available")
            return False
        
        tool_data = {
            "name": "Test AI Tool",
            "description": "A test AI tool for automated testing purposes",
            "category": "Testing",
            "platforms": ["Web", "API"],
            "features": ["Automated testing", "API integration", "Real-time monitoring"],
            "pricing": "Free for testing",
            "url": "https://example.com/test-tool",
            "tags": ["testing", "automation", "api"]
        }
        
        result = self.run_test("Create Tool", "POST", "tools", 200, tool_data)
        return result is not None

    def test_invalid_endpoints(self):
        """Test error handling for invalid endpoints"""
        # Test non-existent endpoint
        result = self.run_test("Invalid Endpoint", "GET", "nonexistent", 404)
        success1 = result is None  # We expect this to fail
        
        # Test invalid tool ID
        result = self.run_test("Invalid Tool ID", "GET", "tools/invalid-id", 404)
        success2 = result is None  # We expect this to fail
        
        return True  # These tests are expected to fail, so we return True

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting AI Tools API Testing...")
        print(f"Testing against: {self.api_url}")
        print("=" * 60)
        
        # Basic functionality tests
        self.test_health_check()
        self.test_user_registration()
        self.test_user_login()
        self.test_get_user_info()
        
        # Tools functionality tests
        self.test_get_tools()
        self.test_get_tools_with_filters()
        self.test_get_categories()
        
        # Advanced features tests
        self.test_ai_recommendations()
        self.test_favorites_system()
        self.test_tool_creation()
        
        # Error handling tests
        self.test_invalid_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Print failed tests details
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['name']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AIToolsAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())