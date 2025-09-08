import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, status, Body
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
SUBMISSIONS_DIR = Path("app/data/submissions")
# Ensure the submissions directory exists on startup
SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)

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
            user_info = user.copy()
            del user_info["password"]
            return {"message": "Login successful", "user": user_info}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.post("/project/{project_id}/table/{table_id}/submit")
async def submit_data(project_id: str, table_id: str, payload: dict = Body(...)):
    """
    Receives submitted table data from the frontend and saves it to a JSON file
    in the 'submissions' directory for testing purposes.
    """
    # Sanitize IDs to prevent directory traversal attacks
    if ".." in project_id or "/" in project_id or "\\" in project_id:
        raise HTTPException(status_code=400, detail="Invalid project_id.")
    if ".." in table_id or "/" in table_id or "\\" in table_id:
        raise HTTPException(status_code=400, detail="Invalid table_id.")
        
    file_path = SUBMISSIONS_DIR / f"{project_id}_{table_id}.json"
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
        return {"message": "Data submitted and saved successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save data: {str(e)}"
        )

@app.get("/")
def read_root():
    return {"Hello": "World"}
