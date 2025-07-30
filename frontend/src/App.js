import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Badge } from './components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from './components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Checkbox } from './components/ui/checkbox';
import { StarIcon, SearchIcon, FilterIcon, HeartIcon, ExternalLinkIcon, SparklesIcon, BrainIcon, RocketIcon } from 'lucide-react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth context
const AuthContext = React.createContext();

const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserInfo();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUserInfo = async () => {
    try {
      const response = await axios.get(`${API}/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/login`, { email, password });
      const { access_token } = response.data;
      setToken(access_token);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      await fetchUserInfo();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (email, username, password) => {
    try {
      const response = await axios.post(`${API}/register`, { email, username, password });
      const { access_token } = response.data;
      setToken(access_token);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      await fetchUserInfo();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    // Force redirect to home page after logout
    window.location.href = '/';
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Landing Page Component
const LandingPage = () => {
  const { user } = useAuth();
  const [requirements, setRequirements] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [quickRecommendations, setQuickRecommendations] = useState([]);

  const handleQuickSearch = async () => {
    if (!requirements.trim()) return;
    
    setIsSearching(true);
    try {
      // For guest users, we'll call the tools API directly and do client-side matching
      if (!user) {
        const response = await axios.get(`${API}/tools`);
        const allTools = response.data || [];
        
        // Simple client-side matching for guest users
        const keywordMatches = allTools.filter(tool => 
          tool.name.toLowerCase().includes(requirements.toLowerCase()) ||
          tool.description.toLowerCase().includes(requirements.toLowerCase()) ||
          tool.category.toLowerCase().includes(requirements.toLowerCase()) ||
          tool.tags.some(tag => tag.toLowerCase().includes(requirements.toLowerCase()))
        ).slice(0, 3);
        
        setQuickRecommendations(keywordMatches);
      } else {
        // For authenticated users, use the AI recommendation endpoint
        const response = await axios.post(`${API}/recommendations`, {
          requirements: requirements,
          preferred_platforms: [],
          use_case: 'general'
        });
        setQuickRecommendations(response.data.tools.slice(0, 3));
      }
    } catch (error) {
      console.error('Quick search failed:', error);
      // Fallback: try to get some sample tools
      try {
        const response = await axios.get(`${API}/tools?limit=3`);
        setQuickRecommendations(response.data || []);
      } catch (fallbackError) {
        console.error('Fallback search also failed:', fallbackError);
        setQuickRecommendations([]);
      }
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
              <SparklesIcon className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              AI Tools Hub
            </span>
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-3">
                <Avatar className="w-8 h-8">
                  <AvatarFallback>{user.username?.charAt(0).toUpperCase()}</AvatarFallback>
                </Avatar>
                <span className="text-sm font-medium">{user.username}</span>
              </div>
            ) : (
              <>
                <Button variant="ghost" onClick={() => window.location.href = '/login'}>
                  Sign In
                </Button>
                <Button onClick={() => window.location.href = '/register'}>
                  Get Started
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center space-x-2 bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <BrainIcon className="w-4 h-4" />
            <span>AI-Powered Tool Discovery</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Find the Perfect
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"> AI Tool </span>
            for Your Needs
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Get intelligent recommendations from our comprehensive database of AI tools. 
            Tell us what you need, and we'll match you with the perfect solution.
          </p>

          {/* Quick Search */}
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200 p-6 mb-12 max-w-2xl mx-auto">
            <div className="space-y-4">
              <Textarea
                placeholder="Describe what you need... (e.g., 'I need an AI tool for coding assistance with real-time collaboration')"
                value={requirements}
                onChange={(e) => setRequirements(e.target.value)}
                className="min-h-[100px] border-gray-300 resize-none"
              />
              <Button
                onClick={handleQuickSearch}
                disabled={isSearching || !requirements.trim()}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                size="lg"
              >
                {isSearching ? (
                  <>
                    <SparklesIcon className="w-4 h-4 mr-2 animate-spin" />
                    Finding Perfect Matches...
                  </>
                ) : (
                  <>
                    <SearchIcon className="w-4 h-4 mr-2" />
                    Get AI Recommendations
                  </>
                )}
              </Button>
            </div>

            {quickRecommendations.length > 0 && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <RocketIcon className="w-5 h-5 mr-2 text-blue-600" />
                  Quick Recommendations
                </h3>
                <div className="space-y-3">
                  {quickRecommendations.map((tool) => (
                    <div key={tool.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium">{tool.name}</h4>
                          <div className="flex items-center">
                            <StarIcon className="w-4 h-4 text-yellow-400 fill-current" />
                            <span className="text-sm text-gray-600 ml-1">{tool.rating}</span>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600">{tool.description.substring(0, 80)}...</p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(tool.url, '_blank')}
                      >
                        <ExternalLinkIcon className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              size="lg"
              onClick={() => window.location.href = user ? '/dashboard' : '/register'}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 px-8"
            >
              {user ? 'Go to Dashboard' : 'Start Free Today'}
              <RocketIcon className="w-4 h-4 ml-2" />
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => window.location.href = '/tools'}
              className="px-8"
            >
              Browse All Tools
              <SearchIcon className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Why Choose AI Tools Hub?</h2>
            <p className="text-lg text-gray-600">Discover the power of intelligent tool matching</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
              <CardHeader className="text-center">
                <BrainIcon className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <CardTitle>AI-Powered Matching</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-center">
                  Our advanced AI analyzes your requirements and matches you with the most suitable tools
                </p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
              <CardHeader className="text-center">
                <SearchIcon className="w-12 h-12 text-green-600 mx-auto mb-4" />
                <CardTitle>Comprehensive Database</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-center">
                  Access hundreds of carefully curated AI tools across all categories and use cases
                </p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
              <CardHeader className="text-center">
                <HeartIcon className="w-12 h-12 text-red-600 mx-auto mb-4" />
                <CardTitle>Personalized Experience</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-center">
                  Save favorites, track your preferences, and get personalized recommendations
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <SparklesIcon className="w-6 h-6 text-blue-400" />
                <span className="text-lg font-bold">AI Tools Hub</span>
              </div>
              <p className="text-gray-400">
                Discover the best AI tools for your projects with intelligent recommendations.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Categories</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Development</li>
                <li>Design</li>
                <li>Writing</li>
                <li>Marketing</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Blog</li>
                <li>Guides</li>
                <li>API</li>
                <li>Support</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li>About</li>
                <li>Privacy</li>
                <li>Terms</li>
                <li>Contact</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 AI Tools Hub. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Login Component
const LoginPage = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(email, password);
    if (result.success) {
      window.location.href = '/dashboard';
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <SparklesIcon className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold">AI Tools Hub</span>
          </div>
          <CardTitle className="text-2xl">Welcome back</CardTitle>
          <CardDescription>
            Enter your credentials to access your account
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-3">
            <Button 
              type="submit" 
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
            <p className="text-sm text-center text-gray-600">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => window.location.href = '/register'}
                className="text-blue-600 hover:underline"
              >
                Sign up
              </button>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};

// Register Component
const RegisterPage = () => {
  const { register } = useAuth();
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await register(email, username, password);
    if (result.success) {
      window.location.href = '/dashboard';
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <SparklesIcon className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold">AI Tools Hub</span>
          </div>
          <CardTitle className="text-2xl">Create your account</CardTitle>
          <CardDescription>
            Join thousands of users discovering the best AI tools
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Choose a username"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Create a password"
                required
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-3">
            <Button 
              type="submit" 
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </Button>
            <p className="text-sm text-center text-gray-600">
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => window.location.href = '/login'}
                className="text-blue-600 hover:underline"
              >
                Sign in
              </button>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const { user, logout } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      const response = await axios.get(`${API}/favorites`);
      setFavorites(response.data.tools);
    } catch (error) {
      console.error('Failed to fetch favorites:', error);
    }
  };

  const getPersonalizedRecommendations = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/recommendations`, {
        requirements: 'Show me trending and highly-rated AI tools across different categories',
        preferred_platforms: [],
        use_case: 'discovery'
      });
      setRecommendations(response.data.tools);
    } catch (error) {
      console.error('Failed to get recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <SparklesIcon className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-bold">AI Tools Hub</span>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" onClick={() => window.location.href = '/tools'}>
              Browse Tools
            </Button>
            <Avatar className="w-8 h-8">
              <AvatarFallback>{user?.username?.charAt(0).toUpperCase()}</AvatarFallback>
            </Avatar>
            <span className="text-sm font-medium">{user?.username}</span>
            <Button variant="outline" onClick={logout} className="text-red-600 border-red-200 hover:bg-red-50">
              <ExternalLinkIcon className="w-4 h-4 mr-2 rotate-180" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-gray-600">Discover new AI tools and manage your favorites</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Personalized Recommendations */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center">
                    <BrainIcon className="w-5 h-5 mr-2 text-blue-600" />
                    Personalized Recommendations
                  </CardTitle>
                  <Button onClick={getPersonalizedRecommendations} disabled={loading}>
                    {loading ? 'Loading...' : 'Refresh'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {recommendations.length === 0 && !loading ? (
                  <div className="text-center py-8">
                    <RocketIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">Get personalized tool recommendations</p>
                    <Button onClick={getPersonalizedRecommendations}>
                      Get Recommendations
                    </Button>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-2 gap-4">
                    {recommendations.map((tool) => (
                      <Card key={tool.id} className="border-l-4 border-l-blue-500">
                        <CardHeader className="pb-2">
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-lg">{tool.name}</CardTitle>
                            <div className="flex items-center">
                              <StarIcon className="w-4 h-4 text-yellow-400 fill-current" />
                              <span className="text-sm ml-1">{tool.rating}</span>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent className="pt-2">
                          <p className="text-sm text-gray-600 mb-3">{tool.description.substring(0, 100)}...</p>
                          <div className="flex flex-wrap gap-1 mb-3">
                            {tool.platforms.slice(0, 2).map((platform) => (
                              <Badge key={platform} variant="secondary" className="text-xs">
                                {platform}
                              </Badge>
                            ))}
                          </div>
                          <Button
                            size="sm"
                            className="w-full"
                            onClick={() => window.open(tool.url, '_blank')}
                          >
                            <ExternalLinkIcon className="w-4 h-4 mr-2" />
                            Visit Tool
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => window.location.href = '/tools'}
                >
                  <SearchIcon className="w-4 h-4 mr-2" />
                  Browse All Tools
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => window.location.href = '/tools?category=Development'}
                >
                  <RocketIcon className="w-4 h-4 mr-2" />
                  Development Tools
                </Button>
              </CardContent>
            </Card>

            {/* Favorites */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <HeartIcon className="w-4 h-4 mr-2 text-red-500" />
                  Your Favorites
                </CardTitle>
              </CardHeader>
              <CardContent>
                {favorites.length === 0 ? (
                  <p className="text-gray-600 text-sm">No favorites yet. Start exploring tools!</p>
                ) : (
                  <div className="space-y-3">
                    {favorites.slice(0, 3).map((tool) => (
                      <div key={tool.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <div>
                          <p className="font-medium text-sm">{tool.name}</p>
                          <p className="text-xs text-gray-600">{tool.category}</p>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => window.open(tool.url, '_blank')}
                        >
                          <ExternalLinkIcon className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

// Tools Browse Component
const ToolsPage = () => {
  const { user } = useAuth();
  const [tools, setTools] = useState([]);
  const [categories, setCategories] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [favorites, setFavorites] = useState(new Set());

  useEffect(() => {
    const initializePage = async () => {
      setLoading(true);
      await fetchCategories();
      await fetchTools();
      if (user) {
        await fetchUserFavorites();
      }
      setLoading(false);
    };
    initializePage();
  }, []);

  useEffect(() => {
    if (!loading) {
      fetchTools();
    }
  }, [searchTerm, selectedCategory, selectedPlatform]);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      setCategories([]);
    }
  };

  const fetchTools = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (selectedCategory && selectedCategory !== 'all') params.append('category', selectedCategory);
      if (selectedPlatform && selectedPlatform !== 'all') params.append('platform', selectedPlatform);

      const response = await axios.get(`${API}/tools?${params}`);
      setTools(response.data || []);
      setError('');
    } catch (error) {
      console.error('Failed to fetch tools:', error);
      setError('Failed to load tools. Please try again.');
      setTools([]);
    }
  };

  const fetchUserFavorites = async () => {
    try {
      const response = await axios.get(`${API}/favorites`);
      const favoriteIds = new Set(response.data.tools.map(tool => tool.id));
      setFavorites(favoriteIds);
    } catch (error) {
      console.error('Failed to fetch favorites:', error);
      setFavorites(new Set());
    }
  };

  const toggleFavorite = async (toolId) => {
    if (!user) {
      window.location.href = '/login';
      return;
    }

    try {
      if (favorites.has(toolId)) {
        await axios.delete(`${API}/favorites/${toolId}`);
        setFavorites(prev => {
          const newSet = new Set(prev);
          newSet.delete(toolId);
          return newSet;
        });
      } else {
        await axios.post(`${API}/favorites/${toolId}`);
        setFavorites(prev => new Set(prev).add(toolId));
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <SparklesIcon className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-bold">AI Tools Hub</span>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" onClick={() => window.location.href = '/'}>
              Home
            </Button>
            {user && (
              <Button variant="ghost" onClick={() => window.location.href = '/dashboard'}>
                Dashboard
              </Button>
            )}
            {!user && (
              <Button onClick={() => window.location.href = '/login'}>
                Sign In
              </Button>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="grid md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <Label htmlFor="search">Search Tools</Label>
              <Input
                id="search"
                placeholder="Search by name, description, or features..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <Label>Category</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="All categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All categories</SelectItem>
                  {categories && categories.length > 0 && categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Platform</Label>
              <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="All platforms" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All platforms</SelectItem>
                  <SelectItem value="Web">Web</SelectItem>
                  <SelectItem value="Desktop">Desktop</SelectItem>
                  <SelectItem value="Mobile">Mobile</SelectItem>
                  <SelectItem value="API">API</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Tools Grid */}
        {loading ? (
          <div className="text-center py-12">
            <SparklesIcon className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading AI tools...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <div className="p-6 bg-red-50 rounded-lg border border-red-200 max-w-md mx-auto">
              <h3 className="text-lg font-semibold text-red-800 mb-2">Unable to Load Tools</h3>
              <p className="text-red-600 mb-4">{error}</p>
              <Button onClick={() => window.location.reload()} variant="outline">
                Try Again
              </Button>
            </div>
          </div>
        ) : tools.length === 0 ? (
          <div className="text-center py-12">
            <SearchIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No tools found</h3>
            <p className="text-gray-600 mb-4">Try adjusting your search criteria or browse all categories</p>
            <div className="flex gap-2 justify-center">
              <Button onClick={() => setSearchTerm('')} variant="outline">
                Clear Search
              </Button>
              <Button onClick={() => {setSelectedCategory('all'); setSelectedPlatform('all');}} variant="outline">
                Clear Filters
              </Button>
            </div>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tools.map((tool) => (
              <Card key={tool.id} className="hover:shadow-lg transition-shadow duration-200 tool-card">
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-1">{tool.name}</CardTitle>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <div className="flex items-center">
                          <StarIcon className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                          {tool.rating} ({tool.review_count})
                        </div>
                        <Badge variant="outline">{tool.category}</Badge>
                      </div>
                    </div>
                    {user && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleFavorite(tool.id)}
                        className="text-gray-400 hover:text-red-500"
                      >
                        <HeartIcon
                          className={`w-4 h-4 ${favorites.has(tool.id) ? 'fill-current text-red-500' : ''}`}
                        />
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {tool.description}
                  </p>
                  
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs font-medium text-gray-900 mb-1">Platforms</p>
                      <div className="flex flex-wrap gap-1">
                        {(tool.platforms || []).map((platform) => (
                          <Badge key={platform} variant="secondary" className="text-xs">
                            {platform}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-xs font-medium text-gray-900 mb-1">Features</p>
                      <div className="flex flex-wrap gap-1">
                        {(tool.features || []).slice(0, 3).map((feature) => (
                          <Badge key={feature} variant="outline" className="text-xs">
                            {feature}
                          </Badge>
                        ))}
                        {tool.features && tool.features.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{tool.features.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-xs font-medium text-gray-900">Pricing</p>
                      <p className="text-sm text-gray-600">{tool.pricing}</p>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="pt-4">
                  <Button
                    className="w-full"
                    onClick={() => window.open(tool.url, '_blank')}
                  >
                    <ExternalLinkIcon className="w-4 h-4 mr-2" />
                    Visit Tool
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <SparklesIcon className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return children;
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/tools" element={<ToolsPage />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;