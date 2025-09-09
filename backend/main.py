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

def _update_data_file(file_path: Path, key: str, payload: dict):
    """
    Atomically reads, updates, and writes data to a JSON file.
    'key' can be 'temp' or 'submit'.
    """
    data = {}
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # Handle empty or invalid JSON file
                content = f.read()
                if content:
                    data = json.loads(content)
                if not isinstance(data, dict):
                    data = {}
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or unreadable, start fresh
            data = {}

    data[key] = payload

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write data: {str(e)}"
        )

@app.post("/project/{project_id}/table/{table_id}/submit")
async def submit_data(project_id: str, table_id: str, payload: dict = Body(...)):
    """
    Receives final submitted data and saves it under the 'submit' key in a JSON file.
    The filename is based on the table_id.
    """
    file_path = SUBMISSIONS_DIR / f"{table_id}.json"
    _update_data_file(file_path, "submit", payload)
    return {"message": f"Data for table ID '{table_id}' submitted successfully."}

@app.post("/project/{project_id}/table/{table_id}/save_draft")
async def save_draft(project_id: str, table_id: str, payload: dict = Body(...)):
    """
    Receives draft data and saves it under the 'temp' key in a JSON file.
    The filename is based on the table_id.
    """
    file_path = SUBMISSIONS_DIR / f"{table_id}.json"
    _update_data_file(file_path, "temp", payload)
    return {"message": f"Draft for table ID '{table_id}' saved successfully."}


@app.get("/data/table/{table_id}")
async def get_table_data(table_id: str):
    """
    Retrieves saved data for a given table ID, returning the whole object
    with 'temp' and 'submit' keys. Returns an empty object if not found.
    """
    file_path = SUBMISSIONS_DIR / f"{table_id}.json"

    if not file_path.exists():
        return {}  # Return empty object instead of 404

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError):
        # If file is corrupted or unreadable, treat as if it doesn't exist
        return {}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading data file: {str(e)}"
        )

@app.post("/project/{project_id}/table_statuses")
async def get_table_statuses(project_id: str, table_ids: list[str] = Body(...)):
    """
    Receives a list of table IDs and returns their statuses.
    """
    statuses = {}
    for table_id in table_ids:
        file_path = SUBMISSIONS_DIR / f"{table_id}.json"
        
        status_info = {"status": "new", "submittedAt": None}

        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content:  # Handle empty file
                        statuses[table_id] = status_info
                        continue
                    data = json.loads(content)
                
                if data.get("submit"):
                    status_info["status"] = "submitted"
                    status_info["submittedAt"] = data["submit"].get("submittedAt")
                    status_info["submittedBy"] = data["submit"].get("submittedBy")
                elif data.get("temp"):
                    status_info["status"] = "saved"
            except (json.JSONDecodeError, IOError):
                # On error, report as 'new'
                pass
        
        statuses[table_id] = status_info

    return statuses


@app.get("/")
def read_root():
    return {"Hello": "World"}
