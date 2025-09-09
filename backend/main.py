import json
import copy
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

# --- App Configuration ---

AUTH_FILE = "app/data/auth.json"
SUBMISSIONS_DIR = Path("app/data/submissions")
SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Mirrored from frontend/src/projects/heating_plan_2025-2026/menu.js
MENU_DATA = [
  {
    "name": "集团公司",
    "tables": [
      { "id": "0", "name": "0 集团分单位汇总表", "templateName": "groupTemplate", "type": "summary", "subsidiaries": [], "aggregationExclusions": [] },
      { 
        "id": "1", 
        "name": "1 集团汇总表", 
        "templateName": "subsidiaryTemplate", 
        "type": "summary",
        "subsidiaries": ["2", "9", "10", "11", "12", "13", "14"],
        "aggregationExclusions": [],
      },
    ]
  },
  {
    "name": "主城区",
    "tables": [
      { 
        "id": "2", 
        "name": "2 主城区汇总表", 
        "templateName": "subsidiaryTemplate", 
        "type": "summary",
        "subsidiaries": ["3", "7", "8"],
        "aggregationExclusions": [],
      },
    ]
  },
  {
    "name": "北海热电厂",
    "tables": [
      { 
        "id": "3", 
        "name": "3 北海汇总表", 
        "templateName": "subsidiaryTemplate", 
        "type": "summary",
        "subsidiaries": ["4", "5", "6"],
        "aggregationExclusions": [97,105,107,109,111,113,114],
      },
      { "id": "4", "name": "4 北海热电厂(热电联产)表", "templateName": "subsidiaryTemplate", "type": "subsidiary" },
      { "id": "5", "name": "5 北海热电厂(水炉)表", "templateName": "subsidiaryTemplate", "type": "subsidiary" },
      { "id": "6", "name": "6 北海热电厂(天然气炉)表", "templateName": "subsidiaryTemplate", "type": "subsidiary" },
    ]
  },
  { "name": "香海热电厂", "tables": [ { "id": "7", "name": "7 香海热电厂表", "templateName": "subsidiaryTemplate", "type": "subsidiary" } ] },
  {
    "name": "供热公司",
    "tables": [
      { "id": "8", "name": "8 供热公司表", "templateName": "subsidiaryTemplate", "type": "subsidiary" },
      { "id": "9", "name": "9 主城区电锅炉表", "templateName": "subsidiaryTemplate", "type": "subsidiary" },
    ]
  },
  { "name": "金州热电", "tables": [ { "id": "10", "name": "10 金州热电表", "templateName": "subsidiaryTemplate", "type": "subsidiary" } ] },
  { "name": "北方热电", "tables": [ { "id": "11", "name": "11 北方热电表", "templateName": "subsidiaryTemplate", "type": "subsidiary" } ] },
  { "name": "金普热电", "tables": [ { "id": "12", "name": "12 金普热电表", "templateName": "subsidiaryTemplate", "type": "subsidiary" } ] },
  { "name": "庄河热电", "tables": [ { "id": "13", "name": "13 庄河环海表", "templateName": "subsidiaryTemplate", "type": "subsidiary" } ] },
  { "name": "研究院", "tables": [ { "id": "14", "name": "14 研究院表", "templateName": "subsidiaryTemplate", "type": "subsidiary" } ] }
]

ALL_TABLES = {table["id"]: table for group in MENU_DATA for table in group["tables"]}

# --- Pydantic model for login request body ---
class UserLogin(BaseModel):
    username: str
    password: str

# --- API Endpoints ---

@app.post("/login")
def login(user_login: UserLogin):
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
    data = {}
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if content:
                    data = json.loads(content)
                if not isinstance(data, dict):
                    data = {}
        except (json.JSONDecodeError, IOError):
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
    file_path = SUBMISSIONS_DIR / f"{table_id}.json"
    _update_data_file(file_path, "submit", payload)
    return {"message": f"Data for table ID '{table_id}' submitted successfully."}

@app.post("/project/{project_id}/table/{table_id}/save_draft")
async def save_draft(project_id: str, table_id: str, payload: dict = Body(...)):
    file_path = SUBMISSIONS_DIR / f"{table_id}.json"
    _update_data_file(file_path, "temp", payload)
    return {"message": f"Draft for table ID '{table_id}' saved successfully."}

@app.get("/data/table/{table_id}")
async def get_table_data(table_id: str):
    table_config = ALL_TABLES.get(table_id)
    if not table_config:
        raise HTTPException(status_code=404, detail="Table configuration not found.")

    if table_config.get("type") != "summary" or not table_config.get("subsidiaries"):
        file_path = SUBMISSIONS_DIR / f"{table_id}.json"
        if not file_path.exists():
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    aggregated_payload = None
    subsidiary_ids = table_config.get("subsidiaries", [])
    exclusion_set = set(table_config.get("aggregationExclusions", []))

    for sub_id in subsidiary_ids:
        sub_file_path = SUBMISSIONS_DIR / f"{sub_id}.json"
        if not sub_file_path.exists():
            continue

        try:
            with open(sub_file_path, "r", encoding="utf-8") as f:
                sub_content = json.load(f)
            
            sub_data = sub_content.get("submit") or sub_content.get("temp")
            if not sub_data or not isinstance(sub_data.get("tableData"), list):
                continue

            if aggregated_payload is None:
                aggregated_payload = copy.deepcopy(sub_data)
                aggregated_payload["submittedAt"] = None
                aggregated_payload["submittedBy"] = None
                if aggregated_payload.get("table"):
                    aggregated_payload["table"]["id"] = table_config.get("id")
                    aggregated_payload["table"]["name"] = table_config.get("name")
                
                for row in aggregated_payload.get("tableData", []):
                    if row.get("metricId") not in exclusion_set:
                        for cell in row.get("values", []):
                            if isinstance(cell.get("value"), (int, float)):
                                cell["value"] = 0
                            if "explanation" in cell:
                                del cell["explanation"]
            
            sub_data_map = {row["metricId"]: row for row in sub_data.get("tableData", []) if row.get("metricId")}

            for agg_row in aggregated_payload.get("tableData", []):
                metric_id = agg_row.get("metricId")
                if not metric_id or agg_row.get("type") != "basic" or metric_id in exclusion_set:
                    continue
                
                if metric_id in sub_data_map:
                    sub_row = sub_data_map[metric_id]
                    sub_cell_map = {cell["fieldId"]: cell.get("value", 0) for cell in sub_row.get("values", []) if cell.get("fieldId")}
                    for agg_cell in agg_row.get("values", []):
                        field_id = agg_cell.get("fieldId")
                        if field_id and isinstance(agg_cell.get("value"), (int, float)):
                            current_val = agg_cell.get("value", 0)
                            agg_cell["value"] = current_val + sub_cell_map.get(field_id, 0)

        except Exception:
            continue

    summary_file_path = SUBMISSIONS_DIR / f"{table_id}.json"
    if summary_file_path.exists() and aggregated_payload is not None:
        try:
            with open(summary_file_path, "r", encoding="utf-8") as f:
                summary_content = json.load(f)
            summary_data = summary_content.get("submit") or summary_content.get("temp")
            if summary_data and isinstance(summary_data.get("tableData"), list):
                aggregated_payload["submittedAt"] = summary_data.get("submittedAt")
                aggregated_payload["submittedBy"] = summary_data.get("submittedBy")

                summary_data_map = {row["metricId"]: row for row in summary_data.get("tableData", []) if row.get("metricId")}
                for agg_row in aggregated_payload.get("tableData", []):
                    metric_id = agg_row.get("metricId")
                    if metric_id and metric_id in exclusion_set and metric_id in summary_data_map:
                        summary_row_cells = {cell["fieldId"]: cell for cell in summary_data_map[metric_id].get("values", []) if cell.get("fieldId")}
                        for i, agg_cell in enumerate(agg_row.get("values", [])):
                            field_id = agg_cell.get("fieldId")
                            if field_id and field_id in summary_row_cells:
                                agg_row["values"][i] = summary_row_cells[field_id]

        except Exception:
            pass

    return {"submit": aggregated_payload} if aggregated_payload else {}

@app.post("/project/{project_id}/table_statuses")
async def get_table_statuses(project_id: str, table_ids: list[str] = Body(...)):
    statuses = {}
    for table_id in table_ids:
        file_path = SUBMISSIONS_DIR / f"{table_id}.json"
        status_info = {"status": "new", "submittedAt": None}

        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content:
                        statuses[table_id] = status_info
                        continue
                    data = json.loads(content)
                
                if data.get("submit"):
                    status_info["status"] = "submitted"
                    status_info["submittedAt"] = data["submit"].get("submittedAt")
                    status_info["submittedBy"] = data["submit"].get("submittedBy")
                elif data.get("temp"):
                    status_info["status"] = "saved"
            except Exception:
                pass
        
        statuses[table_id] = status_info

    return statuses

@app.get("/")
def read_root():
    return {"Hello": "World"}
