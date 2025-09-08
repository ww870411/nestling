import json
import re
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

def sanitize_filename(name: str) -> str:
    """Removes characters that are invalid or problematic in filenames."""
    # Remove invalid characters for Windows/Linux/macOS and other problematic ones like parentheses
    name = re.sub(r'[\\/*?<>|()"\\]', '', name).strip()
    # Replace spaces with underscores for further safety
    return name.replace(' ', '_')

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
    Receives submitted table data and saves it to a JSON file named after the table's name.
    Overwrites the file if it already exists.
    """
    try:
        table_name = payload['table']['name']
    except KeyError:
        raise HTTPException(status_code=400, detail="Payload must contain table name.")

    sanitized_name = sanitize_filename(table_name)
    if not sanitized_name:
        raise HTTPException(status_code=400, detail="Invalid table name after sanitization.")
        
    file_path = SUBMISSIONS_DIR / f"{sanitized_name}.json"
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
        return {"message": f"Data for table '{table_name}' submitted and saved successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save data: {str(e)}"
        )

@app.get("/data/table/{table_name}")
async def get_table_data(table_name: str):
    """
    Retrieves saved data for a given table name.
    """
    sanitized_name = sanitize_filename(table_name)
    if not sanitized_name:
        raise HTTPException(status_code=400, detail="Invalid table name after sanitization.")

    file_path = SUBMISSIONS_DIR / f"{sanitized_name}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"No saved data found for table '{table_name}'.")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading data file: {str(e)}"
        )


@app.get("/")
def read_root():
    return {"Hello": "World"}