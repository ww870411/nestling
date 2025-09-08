import json
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic model for login request body ---
class UserLogin(BaseModel):
    username: str
    password: str

AUTH_FILE = "app/data/auth.json"

@app.post("/login")
def login(user_login: UserLogin):
    """
    Authenticates a user based on username and password.
    Reads user data from a JSON file.
    """
    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication file not found on the server."
        )

    for user in users:
        if user["username"] == user_login.username and user["password"] == user_login.password:
            # Create a copy of the user dict to avoid modifying the original
            user_info = user.copy()
            # Never return the password to the client
            del user_info["password"]
            return {"message": "Login successful", "user": user_info}

    # If the loop completes without finding a user, authentication fails
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.get("/")
def read_root():
    return {"Hello": "World"}
