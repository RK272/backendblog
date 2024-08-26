
from langchain_core.prompts import ChatPromptTemplate

from langserve import add_routes
import uvicorn
import os
from langchain_groq import ChatGroq

from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

import hashlib
from datetime import datetime

load_dotenv()
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from passlib.context import CryptContext


load_dotenv()

# Load the Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")

app = FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A simple API Server"
)

# Initialize the database client
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/trade"

# Create a database engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic model for signup data
class SignupData(BaseModel):
    username: str
    email: str
    password: str

# Pydantic model for login data
class LoginData(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility function to hash passwords (optional but recommended)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/login")
async def login(data: LoginData, db: SessionLocal = Depends(get_db)):
    try:
        print(data.username)
        print(data.password)
        user_query = text("SELECT * FROM users WHERE username = :username")
        result = db.execute(user_query, {"username": data.username}).fetchone()
        print(result)

        if not result:
            raise HTTPException(status_code=400, detail="Invalid username or password")
        
        # Access the password using the correct index
        user_password = result[3]  # Assuming 'password' is the third column (index 2)

        # Hash the incoming password and compare
        if hash_password(data.password) != user_password:
            print(hash_password(data.password))
            raise HTTPException(status_code=400, detail="Invalid username or password")

        return {"message": "Login successful"}

    except Exception as e:
        print(f"Error: {e}")  # This will print the error to the console
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/signup")
async def signup(data: SignupData):
    db = SessionLocal()
    try:
        # Hash the password before storing (recommended)
        hashed_password = hash_password(data.password)
        
        # Insert signup data into the MySQL database
        signup_query = text("""
            INSERT INTO users (username, email, password, created_at, updated_at)
            VALUES (:username, :email, :password, :created_at, :updated_at)
        """)
        
        # Execute the query
        db.execute(signup_query, {
            "username": data.username,
            "email": data.email,
            "password": hashed_password,  # Using hashed password
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # Commit the transaction
        db.commit()
        
        return {"message": "Signup successful"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()

# Existing LangChain and Groq configuration
model = ChatGroq(groq_api_key=groq_api_key, model_name="gemma-7b-it")
prompt1 = ChatPromptTemplate.from_template("create a json object that represent post it should contain array of object with properties of blog about {topic} content hould be minimum 200 words and author and title and topic and content and id and date and category and tags and giv this format ")
#prompt1 = ChatPromptTemplate.from_template("create a json object that represents a post. It should contain an array of objects with properties of a blog about {topic}. Content should be a minimum of 200 words, including author, title, topic, content, id, date, category, and tags.give output to this Format: {'posts': [{ 'id': 1, 'title': 'Machine Learning for Beginners: A Comprehensive Guide', 'author': 'John Doe', 'date': '2023-10-27', 'category': 'Machine Learning', 'tags': ['machine learning', 'tutorial', 'beginners'], 'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.' }]}")
add_routes(
    app,
    prompt1 | model,
    path="/essay"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Or ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
