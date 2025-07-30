from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from openai import OpenAI
import json
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI setup
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Security setup
SECRET_KEY = "your-secret-key-here"  # In production, use a secure random key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="AI Tools Consulting API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    hashed_password: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    preferences: Optional[Dict[str, Any]] = {}

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class AITool(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str
    platforms: List[str]
    features: List[str]
    pricing: str
    url: str
    rating: float = 0.0
    review_count: int = 0
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AIToolCreate(BaseModel):
    name: str
    description: str
    category: str
    platforms: List[str]
    features: List[str]
    pricing: str
    url: str
    tags: List[str] = []

class ToolRecommendationRequest(BaseModel):
    requirements: str
    preferred_platforms: List[str] = []
    budget: Optional[str] = None
    use_case: Optional[str] = None

class ToolRecommendation(BaseModel):
    tools: List[AITool]
    reasoning: str
    match_scores: Dict[str, float]

class UserReview(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tool_id: str
    rating: int  # 1-5
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReviewCreate(BaseModel):
    tool_id: str
    rating: int
    comment: str

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.users.find_one({"email": user_email})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

# Initialize sample AI tools data
async def init_sample_data():
    existing_tools = await db.ai_tools.count_documents({})
    if existing_tools == 0:
        sample_tools = [
            {
                "id": str(uuid.uuid4()),
                "name": "Cursor AI",
                "description": "AI-powered coding assistant for faster development with intelligent code completion and real-time collaboration",
                "category": "Development",
                "platforms": ["Web", "Desktop"],
                "features": ["Code completion", "Real-time collaboration", "Debugging support", "Multi-language support"],
                "pricing": "Freemium - $20/month for premium",
                "url": "https://cursor.ai",
                "rating": 4.8,
                "review_count": 150,
                "tags": ["coding", "ai", "productivity", "development"],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "ChatGPT",
                "description": "Advanced conversational AI for content creation, coding help, and general assistance",
                "category": "General AI",
                "platforms": ["Web", "Mobile", "API"],
                "features": ["Natural language processing", "Code generation", "Content creation", "Problem solving"],
                "pricing": "Free tier available - $20/month for premium",
                "url": "https://chat.openai.com",
                "rating": 4.7,
                "review_count": 5000,
                "tags": ["chatbot", "ai", "content", "assistance"],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "DALL-E 3",
                "description": "AI image generation tool for creating high-quality artwork and images from text descriptions",
                "category": "Image Generation",
                "platforms": ["Web", "API"],
                "features": ["Text-to-image generation", "High resolution output", "Style customization", "Commercial usage"],
                "pricing": "Credits-based - $15-50/month depending on usage",
                "url": "https://openai.com/dall-e-3",
                "rating": 4.6,
                "review_count": 800,
                "tags": ["image", "ai", "art", "generation"],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "GitHub Copilot",
                "description": "AI pair programmer that helps you write code faster with intelligent suggestions",
                "category": "Development",
                "platforms": ["IDE Extensions", "Web"],
                "features": ["Code suggestions", "Auto-completion", "Documentation generation", "Test writing"],
                "pricing": "$10/month for individuals - $19/month for business",
                "url": "https://github.com/features/copilot",
                "rating": 4.5,
                "review_count": 2000,
                "tags": ["coding", "github", "ai", "programming"],
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Midjourney",
                "description": "AI art generator known for creating stunning, artistic images from text prompts",
                "category": "Image Generation",
                "platforms": ["Discord Bot", "Web"],
                "features": ["Artistic image generation", "Style variations", "Upscaling", "Community gallery"],
                "pricing": "Subscription-based - $10-60/month",
                "url": "https://midjourney.com",
                "rating": 4.9,
                "review_count": 1200,
                "tags": ["art", "ai", "creativity", "discord"],
                "created_at": datetime.utcnow()
            }
        ]
        await db.ai_tools.insert_many(sample_tools)
        print("Sample AI tools data initialized")

# OpenAI recommendation function
async def get_ai_recommendations(requirements: str, available_tools: List[dict]) -> Dict[str, Any]:
    tools_summary = []
    for tool in available_tools[:20]:  # Limit to avoid token limits
        tools_summary.append({
            "name": tool["name"],
            "description": tool["description"],
            "category": tool["category"],
            "platforms": tool["platforms"],
            "features": tool["features"],
            "pricing": tool["pricing"],
            "rating": tool["rating"]
        })
    
    prompt = f"""
    Based on the user requirements: "{requirements}"
    
    Here are the available AI tools:
    {json.dumps(tools_summary, indent=2)}
    
    Please analyze the requirements and recommend the most suitable tools. 
    Respond with a JSON object containing:
    {{
        "recommended_tools": [list of tool names ranked by relevance],
        "reasoning": "explanation of why these tools match the requirements",
        "match_scores": {{"tool_name": score_out_of_100, ...}}
    }}
    
    Consider factors like use case alignment, platform compatibility, features matching, and value for money.
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI tools expert who provides intelligent recommendations based on user requirements. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Fallback to simple keyword matching
        return {
            "recommended_tools": [tool["name"] for tool in available_tools[:5]],
            "reasoning": "Showing top-rated tools due to AI service unavailability",
            "match_scores": {tool["name"]: 80.0 for tool in available_tools[:5]}
        }

# Authentication routes
@api_router.post("/register", response_model=Token)
async def register_user(user: UserRegister):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user_obj = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        preferences=user.preferences or {}
    )
    
    await db.users.insert_one(user_obj.dict())
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/login", response_model=Token)
async def login_user(user: UserLogin):
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# AI Tools routes
@api_router.get("/tools", response_model=List[AITool])
async def get_tools(
    category: Optional[str] = None,
    platform: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50
):
    query = {}
    if category:
        query["category"] = category
    if platform:
        query["platforms"] = {"$in": [platform]}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search.lower()]}}
        ]
    
    tools = await db.ai_tools.find(query).limit(limit).to_list(limit)
    return [AITool(**tool) for tool in tools]

@api_router.post("/tools", response_model=AITool)
async def create_tool(tool: AIToolCreate, current_user: User = Depends(get_current_user)):
    tool_obj = AITool(**tool.dict())
    await db.ai_tools.insert_one(tool_obj.dict())
    return tool_obj

@api_router.delete("/tools/{tool_id}")
async def delete_tool(tool_id: str, current_user: User = Depends(get_current_user)):
    result = await db.ai_tools.delete_one({"id": tool_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"message": "Tool deleted successfully"}

@api_router.get("/tools/{tool_id}", response_model=AITool)
async def get_tool(tool_id: str):
    tool = await db.ai_tools.find_one({"id": tool_id})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return AITool(**tool)

# Smart recommendation endpoint
@api_router.post("/recommendations", response_model=ToolRecommendation)
async def get_recommendations(request: ToolRecommendationRequest, current_user: User = Depends(get_current_user)):
    # Get all available tools
    query = {}
    if request.preferred_platforms:
        query["platforms"] = {"$in": request.preferred_platforms}
    
    all_tools = await db.ai_tools.find(query).to_list(100)
    
    if not all_tools:
        raise HTTPException(status_code=404, detail="No tools found matching criteria")
    
    # Get AI-powered recommendations
    ai_result = await get_ai_recommendations(request.requirements, all_tools)
    
    # Filter and sort tools based on AI recommendations
    recommended_tool_names = ai_result.get("recommended_tools", [])
    tools_dict = {tool["name"]: AITool(**tool) for tool in all_tools}
    
    recommended_tools = []
    for tool_name in recommended_tool_names:
        if tool_name in tools_dict:
            recommended_tools.append(tools_dict[tool_name])
    
    # Add any remaining highly-rated tools if we don't have enough recommendations
    if len(recommended_tools) < 5:
        remaining_tools = [tools_dict[name] for name in tools_dict.keys() 
                         if name not in recommended_tool_names]
        remaining_tools.sort(key=lambda x: x.rating, reverse=True)
        recommended_tools.extend(remaining_tools[:5-len(recommended_tools)])
    
    return ToolRecommendation(
        tools=recommended_tools,
        reasoning=ai_result.get("reasoning", "Tools recommended based on your requirements"),
        match_scores=ai_result.get("match_scores", {})
    )

# Reviews routes
@api_router.post("/reviews", response_model=UserReview)
async def create_review(review: ReviewCreate, current_user: User = Depends(get_current_user)):
    # Check if tool exists
    tool = await db.ai_tools.find_one({"id": review.tool_id})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Check if user already reviewed this tool
    existing_review = await db.reviews.find_one({"user_id": current_user.id, "tool_id": review.tool_id})
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this tool")
    
    review_obj = UserReview(
        user_id=current_user.id,
        tool_id=review.tool_id,
        rating=review.rating,
        comment=review.comment
    )
    
    await db.reviews.insert_one(review_obj.dict())
    
    # Update tool rating
    all_reviews = await db.reviews.find({"tool_id": review.tool_id}).to_list(1000)
    avg_rating = sum(r["rating"] for r in all_reviews) / len(all_reviews)
    await db.ai_tools.update_one(
        {"id": review.tool_id},
        {"$set": {"rating": round(avg_rating, 1), "review_count": len(all_reviews)}}
    )
    
    return review_obj

@api_router.get("/tools/{tool_id}/reviews")
async def get_tool_reviews(tool_id: str):
    reviews = await db.reviews.find({"tool_id": tool_id}).to_list(100)
    return reviews

# Categories endpoint
@api_router.get("/categories")
async def get_categories():
    categories = await db.ai_tools.distinct("category")
    return {"categories": categories}

# User favorites
@api_router.post("/favorites/{tool_id}")
async def add_to_favorites(tool_id: str, current_user: User = Depends(get_current_user)):
    await db.users.update_one(
        {"id": current_user.id},
        {"$addToSet": {"preferences.favorites": tool_id}}
    )
    return {"message": "Added to favorites"}

@api_router.delete("/favorites/{tool_id}")
async def remove_from_favorites(tool_id: str, current_user: User = Depends(get_current_user)):
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"preferences.favorites": tool_id}}
    )
    return {"message": "Removed from favorites"}

@api_router.get("/favorites")
async def get_user_favorites(current_user: User = Depends(get_current_user)):
    user = await db.users.find_one({"id": current_user.id})
    favorite_ids = user.get("preferences", {}).get("favorites", [])
    
    if not favorite_ids:
        return {"tools": []}
    
    favorite_tools = await db.ai_tools.find({"id": {"$in": favorite_ids}}).to_list(100)
    return {"tools": [AITool(**tool) for tool in favorite_tools]}

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "AI Tools Consulting API is running!", "status": "healthy"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize data on startup
@app.on_event("startup")
async def startup_event():
    await init_sample_data()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()