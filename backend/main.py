import json
import copy
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
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
# Path for USER-GENERATED data (submissions, auth file). From env var or default.
data_dir_path = os.getenv('DATA_DIR_PATH', str(Path(__file__).resolve().parent / "app" / "data"))
DATA_DIR = Path(data_dir_path)
DATA_DIR.mkdir(parents=True, exist_ok=True)
BEIJING_TZ = ZoneInfo("Asia/Shanghai")

# Path for APPLICATION-LEVEL config files (templates, menu definitions). Always with the code.
CONFIG_DIR = Path(__file__).resolve().parent / "app" / "data"

# --- Update file paths ---

# This is user data, so it uses the new DATA_DIR
AUTH_FILE = DATA_DIR / "auth.json"

# These are app configs, so they should use CONFIG_DIR
MENU_FILE = CONFIG_DIR / "heating_plan_2025-2026_data" / "menucopy.json"
with open(MENU_FILE, "r", encoding="utf-8") as f:
    MENU_DATA = json.load(f)

# Load report template from JSON file
TEMPLATE_FILE = CONFIG_DIR / "heating_plan_2025-2026_data" / "templatecopy.json"
with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
    REPORT_TEMPLATE = json.load(f)

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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during file write: {str(e)}"
        )


def _append_history_record(submissions_dir: Path, project_id: str, table_id: str, payload: dict, action: str):
    payload = payload if isinstance(payload, dict) else {}
    table_info = payload.get("table") if isinstance(payload.get("table"), dict) else {}
    timestamp = payload.get("submittedAt") if isinstance(payload.get("submittedAt"), str) else None
    if not timestamp:
        timestamp = datetime.now(BEIJING_TZ).isoformat()

    record = {
        "projectId": project_id,
        "tableId": table_id,
        "tableName": table_info.get("name"),
        "action": action,
        "timestamp": timestamp,
        "submittedBy": payload.get("submittedBy"),
    }

    table_template = table_info.get("template")
    if table_template:
        record["tableTemplate"] = table_template

    fallback_table = ALL_TABLES.get(str(table_id))
    if fallback_table and not record.get("tableName"):
        record["tableName"] = fallback_table.get("name")
    if fallback_table and "tableTemplate" not in record:
        template_name = fallback_table.get("templateName")
        if template_name:
            record["tableTemplate"] = template_name

    history_file = submissions_dir / "history.json"
    history = []

    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8-sig") as f:
                existing = json.load(f)
                if isinstance(existing, list):
                    history = existing
        except (json.JSONDecodeError, IOError):
            history = []

    history.append(record)

    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update history file: {str(e)}"
        )

@app.post("/project/{project_id}/table/{table_id}/submit")
async def submit_data(project_id: str, table_id: str, payload: dict = Body(...)):
    submissions_dir = DATA_DIR / f"{project_id}_data"
    submissions_dir.mkdir(parents=True, exist_ok=True)
    file_path = submissions_dir / f"{table_id}.json"
    _update_data_file(file_path, "submit", payload)
    _append_history_record(submissions_dir, project_id, table_id, payload, "submit")
    return {"message": f"Data for table ID '{table_id}' submitted successfully."}

@app.post("/project/{project_id}/table/{table_id}/save_draft")
async def save_draft(project_id: str, table_id: str, payload: dict = Body(...)):
    submissions_dir = DATA_DIR / f"{project_id}_data"
    submissions_dir.mkdir(parents=True, exist_ok=True)
    file_path = submissions_dir / f"{table_id}.json"
    _update_data_file(file_path, "temp", payload)
    _append_history_record(submissions_dir, project_id, table_id, payload, "save_draft")
    return {"message": f"Draft for table ID '{table_id}' saved successfully."}


async def get_table_0_data(project_id: str):
    """
    Special function to aggregate data for Table 0.
    Reads data directly from subsidiary JSON files and surfaces soft/calculated issue metadata.
    """
    table_config = ALL_TABLES.get('0')
    if not table_config:
        return {}

    # Load templates and field configurations
    report_template = REPORT_TEMPLATE
    GROUP_TEMPLATE_FILE = CONFIG_DIR / "heating_plan_2025-2026_data" / "groupTemplate.json"
    with open(GROUP_TEMPLATE_FILE, "r", encoding="utf-8") as f:
        field_config = json.load(f)

    field_label_map = {field['id']: field.get('label') for field in field_config}
    metric_name_map = {row['id']: row['name'] for row in report_template}

    issue_map = defaultdict(list)
    explanation_summary = []

    # Create maps from subsidiary key (e.g., 'group') to the target fieldId
    key_to_plan_field_id = {field['name'].split('.')[0]: field['id'] for field in field_config if '.plan' in field['name']}
    key_to_same_period_field_id = {field['name'].split('.')[0]: field['id'] for field in field_config if '.samePeriod' in field['name']}

    # Initialize tableData with default zero values
    table_data = []
    for row_template in report_template:
        new_row = {
            "metricId": row_template['id'],
            "name": row_template['name'],
            "unit": row_template['unit'],
            "values": []
        }
        for field in field_config:
            field_id = field['id']
            value = 0  # Default to 0
            if field_id == 1001:
                value = row_template['name']
            elif field_id == 1002:
                value = row_template['unit']
            new_row["values"].append({"fieldId": field_id, "value": value})
        table_data.append(new_row)

    # Directly read subsidiary files and populate plan/samePeriod data
    subsidiaries_map = table_config.get("subsidiaries", {})
    submissions_dir = DATA_DIR / f"{project_id}_data"

    for sub_key, sub_id in subsidiaries_map.items():
        sub_content = {}
        file_path = submissions_dir / f"{sub_id}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content:
                        sub_content = json.loads(content)
            except (json.JSONDecodeError, IOError):
                sub_content = {}  # Continue with empty content on error

        sub_data = sub_content.get("submit") or sub_content.get("temp")
        if not sub_data or not isinstance(sub_data.get("tableData"), list):
            continue

        target_plan_id = key_to_plan_field_id.get(sub_key)
        target_same_period_id = key_to_same_period_field_id.get(sub_key)
        if not target_plan_id or not target_same_period_id:
            continue

        sub_values = {}
        for row in sub_data.get("tableData", []):
            metric_id = row.get("metricId")
            if not metric_id:
                continue

            plan_val, same_period_val = 0, 0

            # Extract plan and samePeriod values, no fallback
            for cell in row.get("values", []):
                field_id = cell.get("fieldId")
                value = cell.get("value", 0) if isinstance(cell.get("value"), (int, float)) else 0

                if field_id == 1003:
                    plan_val = value
                if field_id == 1004:
                    same_period_val = value

            sub_values[metric_id] = {"plan": plan_val, "samePeriod": same_period_val}

            # Capture explanations on the totals columns (soft/calc issues)
            for cell in row.get("values", []):
                field_id = cell.get("fieldId")
                if field_id not in (1003, 1004):
                    continue
                explanation = cell.get("explanation")
                if not explanation or not isinstance(explanation, dict):
                    continue
                rule_key = explanation.get("ruleKey")
                if not rule_key:
                    continue
                parts = str(rule_key).split("-")
                if len(parts) < 2:
                    continue
                issue_type = parts[1]
                if issue_type not in {"B", "C"}:
                    continue

                dest_field_id = target_plan_id if field_id == 1003 else target_same_period_id
                issue_detail = {
                    "type": issue_type,
                    "message": explanation.get("message"),
                    "content": explanation.get("content"),
                    "ruleKey": rule_key,
                    "metricId": metric_id,
                    "metricName": row.get("metricName") or metric_name_map.get(metric_id),
                    "fieldId": dest_field_id,
                    "fieldLabel": field_label_map.get(dest_field_id),
                    "sourceTableId": str(sub_id),
                    "sourceTableName": ALL_TABLES.get(str(sub_id), {}).get("name"),
                }
                issue_map[(metric_id, dest_field_id)].append(issue_detail)
                explanation_summary.append(issue_detail)

        for agg_row in table_data:
            metric_id = agg_row.get("metricId")
            if metric_id in sub_values:
                for agg_cell in agg_row.get("values", []):
                    field_id = agg_cell.get("fieldId")
                    if field_id == target_plan_id:
                        agg_cell["value"] = sub_values[metric_id]["plan"]
                    elif field_id == target_same_period_id:
                        agg_cell["value"] = sub_values[metric_id]["samePeriod"]

    # Attach aggregated issue metadata back onto the table
    for agg_row in table_data:
        metric_id = agg_row.get("metricId")
        for cell in agg_row.get("values", []):
            key = (metric_id, cell.get("fieldId"))
            if key in issue_map:
                cell["issues"] = issue_map[key]

    aggregated_payload = {
        "table": {"id": table_config.get("id"), "name": table_config.get("name")},
        "tableData": table_data,
        "submittedAt": None,
        "submittedBy": None
    }

    if explanation_summary:
        aggregated_payload["explanationSummary"] = explanation_summary

    return {"submit": aggregated_payload, "explanationSummary": aggregated_payload.get("explanationSummary", [])}


async def get_table_data_recursive(project_id: str, table_id: str):
    # Table 0 is the group summary table – uses its own logic
    if table_id == '0':
        return await get_table_0_data(project_id)

    table_config = ALL_TABLES.get(table_id)
    if not table_config:
        return {}

    # --- UNIFIED LOGIC: All tables read from files, no recursion --- 

    submissions_dir = DATA_DIR / f"{project_id}_data"
    file_path = submissions_dir / f"{table_id}.json"

    # If the table is NOT a summary table, just read its own file and return.
    if table_config.get("type") != "summary" or not table_config.get("subsidiaries"):
        if not file_path.exists(): return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return {}

    # If the table IS a summary table, aggregate from direct subsidiary files.
    if table_config.get("type") == "summary" and isinstance(table_config.get("subsidiaries"), list):
        aggregated_payload = None
        subsidiary_ids = table_config.get("subsidiaries", [])
        exclusion_set = set(table_config.get("aggregationExclusions", []))
        
        # These calculated IDs are skipped during summation and recalculated in the frontend.
        calculated_field_ids = {1004, 1005}
        calculated_metric_ids = {
            7, 18, 25, 28, 29, 32, 35, 36, 40, 42, 62, 63, 65, 68, 75, 76, 77, 78, 79, 80, 81, 
            82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 96, 98, 100, 102, 104, 106, 
            108, 110, 112, 115
        }

        for sub_id in subsidiary_ids:
            # --- MODIFICATION: Directly read file, no recursive call ---
            sub_content = {}
            sub_file_path = submissions_dir / f"{sub_id}.json"
            if sub_file_path.exists():
                try:
                    with open(sub_file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if content: sub_content = json.loads(content)
                except (json.JSONDecodeError, IOError):
                    sub_content = {}
            # --- END MODIFICATION ---

            sub_data = sub_content.get("submit") or sub_content.get("temp")
            if not sub_data or not isinstance(sub_data.get("tableData"), list): continue

            if aggregated_payload is None:
                # Initialize the payload with the structure of the first sub-table
                aggregated_payload = copy.deepcopy(sub_data)
                aggregated_payload["submittedAt"] = None
                aggregated_payload["submittedBy"] = None
                if aggregated_payload.get("table"):
                    aggregated_payload["table"]["id"] = table_config.get("id")
                    aggregated_payload["table"]["name"] = table_config.get("name")
                
                # Clean the template: zero out numerical values and STRIP explanations
                for row in aggregated_payload.get("tableData", []):
                    if row.get("metricId") not in exclusion_set:
                        clean_values = []
                        for cell in row.get("values", []):
                            field_id = cell.get("fieldId")
                            # Default to a clean cell with a zeroed value
                            new_cell = {"fieldId": field_id, "value": 0}
                            # Preserve original values for non-numeric 'name' and 'unit' columns (assuming 1001/1002)
                            if field_id == 1001 or field_id == 1002:
                                new_cell["value"] = cell.get("value")
                            clean_values.append(new_cell)
                        # Replace the old list (which might have explanations) with the clean one
                        row["values"] = clean_values
            
            sub_data_map = {row["metricId"]: row for row in sub_data.get("tableData", []) if row.get("metricId")}
            sub_table_config = ALL_TABLES.get(sub_id, {})
            be_aggregated_exclusions = set(sub_table_config.get("beAggregatedExclusions", []))

            for agg_row in aggregated_payload.get("tableData", []):
                metric_id = agg_row.get("metricId")
                if not metric_id or metric_id in exclusion_set or metric_id in be_aggregated_exclusions:
                    continue

                if metric_id in sub_data_map:
                    sub_row = sub_data_map[metric_id]

                    # Skip calculated metrics, they are handled by frontend
                    if metric_id in calculated_metric_ids and not sub_row.get("force"): 
                        continue

                    sub_cell_map = {cell["fieldId"]: cell.get("value", 0) for cell in sub_row.get("values", []) if cell.get("fieldId")}
                    
                    for agg_cell in agg_row.get("values", []):
                        field_id = agg_cell.get("fieldId")
                        if not field_id or field_id in calculated_field_ids:
                            continue

                        # Perform summation with type checking
                        if isinstance(agg_cell.get("value"), (int, float)):
                            current_val = agg_cell.get("value", 0)
                            val_to_add = sub_cell_map.get(field_id, 0)
                            if not isinstance(val_to_add, (int, float)):
                                val_to_add = 0
                            agg_cell["value"] = current_val + val_to_add

        # Override with manually entered data for the summary table itself, if any
        if file_path.exists() and aggregated_payload is not None:
            try:
                with open(file_path, "r", encoding="utf-8") as f: summary_content = json.load(f)
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

            except Exception: pass

        return {"submit": aggregated_payload} if aggregated_payload else {}
    
    return {}


@app.get("/project/{project_id}/table/{table_id}/history")
async def get_table_history(project_id: str, table_id: str):
    submissions_dir = DATA_DIR / f"{project_id}_data"
    history_file = submissions_dir / "history.json"

    if not history_file.exists():
        return []

    try:
        with open(history_file, "r", encoding="utf-8-sig") as f:
            records = json.load(f)
        if not isinstance(records, list):
            return []
    except Exception:
        return []

    filtered = []
    table_id_str = str(table_id)
    fallback_table = ALL_TABLES.get(table_id_str)

    for record in records:
        if not isinstance(record, dict):
            continue
        if str(record.get("tableId")) != table_id_str:
            continue

        submitted_by = record.get("submittedBy")
        if submitted_by and (
            submitted_by.get("globalRole") == "god" or
            submitted_by.get("username") == "ww870411"
        ):
            continue

        entry = {
            "projectId": record.get("projectId"),
            "tableId": table_id_str,
            "tableName": record.get("tableName"),
            "action": record.get("action"),
            "timestamp": record.get("timestamp"),
            "submittedBy": submitted_by,
        }

        if not entry["tableName"] and fallback_table:
            entry["tableName"] = fallback_table.get("name")

        filtered.append(entry)

    filtered.sort(key=lambda item: item.get("timestamp") or "", reverse=True)
    return filtered

@app.get("/project/{project_id}/data/table/{table_id}")
async def get_table_data(project_id: str, table_id: str):
    return await get_table_data_recursive(project_id, table_id)

@app.post("/project/{project_id}/table_statuses")
async def get_table_statuses(project_id: str, table_ids: list[str] = Body(...)):
    statuses = {}
    submissions_dir = DATA_DIR / f"{project_id}_data"
    for table_id in table_ids:
        file_path = submissions_dir / f"{table_id}.json"
        status_info = {"status": "new", "submittedAt": None, "submittedBy": None}

        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content:
                        statuses[table_id] = status_info
                        continue
                    data = json.loads(content)
                
                # Default to 'saved' if a temp copy exists
                if data.get("temp"):
                    status_info["status"] = "saved"

                # Check for a valid submission that can override the status
                if data.get("submit"):
                    submitted_by = data["submit"].get("submittedBy")
                    # If NOT submitted by the admin, then it's officially "submitted"
                    if not (submitted_by and submitted_by.get("username") == 'ww870411'):
                        status_info["status"] = "submitted"
                        status_info["submittedAt"] = data["submit"].get("submittedAt")
                        status_info["submittedBy"] = data["submit"].get("submittedBy")

            except Exception:
                pass
        
        statuses[table_id] = status_info

    return statuses

@app.get("/")
def read_root():
    return {"Hello": "World"}
