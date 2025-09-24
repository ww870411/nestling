import json
import copy
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException, status, Body, Request
from typing import List
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

LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "activity.log"

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
TABLE_TO_GROUP = {table["id"]: group["name"] for group in MENU_DATA for table in group["tables"]}

# Build child-parent relationships (direct only)
CHILDREN_MAP: dict[str, list[str]] = {}
PARENT_MAP: dict[str, list[str]] = {}
for group in MENU_DATA:
    for t in group.get("tables", []):
        tid = str(t.get("id"))
        children: list[str] = []
        subs = t.get("subsidiaries")
        if isinstance(subs, list):
            children = [str(x) for x in subs]
        elif isinstance(subs, dict):
            try:
                children = [str(v) for v in subs.values()]
            except Exception:
                children = []
        if children:
            CHILDREN_MAP[tid] = children
            for cid in children:
                PARENT_MAP.setdefault(cid, []).append(tid)

def _load_users():
    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _get_user_from_request(request: Request):
    username = request.headers.get('X-User-Name') if hasattr(request, 'headers') else None
    if not username:
        return None
    for u in _load_users():
        if u.get('username') == username:
            return u
    return None

def _is_table_approved(project_id: str, table_id: str) -> bool:
    submissions_dir = DATA_DIR / f"{project_id}_data"
    file_path = submissions_dir / f"{table_id}.json"
    if not file_path.exists():
        return False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return bool(data.get("approved"))
    except Exception:
        return False

def _region_scope_ids(region_name: str):
    # 所属区域的汇总表ID集合及其（递归）子表ID集合
    region_table_ids = set()
    child_ids = set()
    id_to_table = {str(t["id"]): t for g in MENU_DATA for t in g.get("tables", [])}

    for group in MENU_DATA:
        if group.get('name') == region_name:
            for t in group.get('tables', []):
                tid = str(t.get('id'))
                region_table_ids.add(tid)
                subs = t.get('subsidiaries')
                if isinstance(subs, list):
                    stack = [str(s) for s in subs]
                    while stack:
                        cid = stack.pop()
                        if cid in child_ids:
                            continue
                        child_ids.add(cid)
                        ct = id_to_table.get(cid)
                        if ct and isinstance(ct.get('subsidiaries'), list):
                            stack.extend([str(s) for s in ct.get('subsidiaries')])
    return region_table_ids, child_ids

def _can_approve(table_id: str, user: dict, action: str):
    # action: 'approve' or 'unapprove'
    if not user:
        return False
    role = user.get('globalRole')
    unit = user.get('unit')
    if role in ('god', 'super_admin'):
        return True

    group_name = TABLE_TO_GROUP.get(str(table_id))
    if role == 'unit_admin':
        # 单位管理员：仅能批准本单位表；不可撤销批准
        if action == 'approve':
            return group_name == unit
        return False

    if role == 'regional_admin':
        # 区域管理员：批准仅限本区域汇总表；撤销仅限其下属单位表
        region_tables, region_children = _region_scope_ids(unit or '')
        tid = str(table_id)
        if action == 'approve':
            return tid in region_tables
        else:
            return tid in region_children

    return False

# --- Pydantic model for login request body ---
class UserLogin(BaseModel):
    username: str
    password: str

# --- API Endpoints ---

@app.post("/login")
def login(user_login: UserLogin, request: Request):
    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except FileNotFoundError:
        _log_action("login", request, username=user_login.username, details={"result": "failed", "reason": "auth_file_missing"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication file not found on the server."
        )

    for user in users:
        if user["username"] == user_login.username and user["password"] == user_login.password:
            user_info = user.copy()
            del user_info["password"]
            _log_action("login", request, username=user_info.get("username") or user_login.username, details={"result": "success"})
            return {"message": "Login successful", "user": user_info}

    _log_action("login", request, username=user_login.username, details={"result": "failed", "reason": "invalid_credentials"})
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



def _get_client_ip(request):
    if request is None:
        return None
    forwarded = request.headers.get('x-forwarded-for') if hasattr(request, 'headers') else None
    if forwarded:
        return forwarded.split(',')[0].strip()
    client = getattr(request, 'client', None)
    return getattr(client, 'host', None) if client else None


def _extract_username(payload=None, request=None):
    username = None

    if isinstance(payload, dict):
        submitted_by = payload.get('submittedBy')
        if isinstance(submitted_by, dict):
            username = submitted_by.get('username') or username
        if not username:
            username = payload.get('username') or payload.get('user')
        if isinstance(username, dict):
            username = username.get('username')

    if (not username) and request is not None:
        if hasattr(request, 'headers'):
            for header in ('x-user-name', 'x-username', 'x-auth-user', 'x-actor'):
                header_value = request.headers.get(header)
                if header_value:
                    username = header_value.strip()
                    if username:
                        break

    return username


def _log_action(action, request=None, username=None, details=None):
    try:
        entry = {
            'timestamp': datetime.now(BEIJING_TZ).isoformat(),
            'action': action,
            'username': username,
            'ip': _get_client_ip(request),
        }
        if details:
            entry['details'] = details

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
            log_file.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass


def _append_history_record(submissions_dir: Path, project_id: str, table_id: str, payload: dict, action: str):
    payload = payload if isinstance(payload, dict) else {}
    table_info = payload.get("table") if isinstance(payload.get("table"), dict) else {}
    # Derive timestamp by action type first, then fallback to generic fields, then now()
    ts_candidates = []
    if action == "submit":
        ts_candidates.append(payload.get("submittedAt"))
    elif action == "approve":
        ts_candidates.append(payload.get("approvedAt"))
    elif action == "unapprove":
        # may be provided by caller; otherwise will fallback to now
        ts_candidates.append(payload.get("unapprovedAt"))
    elif action == "save_draft":
        ts_candidates.append(payload.get("savedAt"))
    # generic fallbacks
    ts_candidates.append(payload.get("timestamp"))
    ts_candidates.append(payload.get("submittedAt"))
    timestamp = next((t for t in ts_candidates if isinstance(t, str) and t), None)
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
async def submit_data(project_id: str, table_id: str, request: Request, payload: dict = Body(...)):
    submissions_dir = DATA_DIR / f"{project_id}_data"
    submissions_dir.mkdir(parents=True, exist_ok=True)
    file_path = submissions_dir / f"{table_id}.json"
    # Normalize submit metadata server-side to ensure accurate history
    try:
        if not isinstance(payload, dict):
            payload = {}
        if not payload.get('submittedAt'):
            payload['submittedAt'] = datetime.now(BEIJING_TZ).isoformat()
        if not payload.get('submittedBy'):
            user = _get_user_from_request(request)
            if user:
                payload['submittedBy'] = user
    except Exception:
        pass
    _update_data_file(file_path, "submit", payload)
    _append_history_record(submissions_dir, project_id, table_id, payload, "submit")
    _log_action("submit", request, username=_extract_username(payload, request), details={"projectId": project_id, "tableId": table_id})
    return {"message": f"Data for table ID '{table_id}' submitted successfully."}

@app.post("/project/{project_id}/table/{table_id}/approve")
async def approve_table(project_id: str, table_id: str, request: Request):
    user = _get_user_from_request(request)
    if not _can_approve(str(table_id), user, 'approve'):
        raise HTTPException(status_code=403, detail="Not allowed to approve this table.")

    # 规则：若为汇总表，只有当其直接子表均已处于“已批准”状态时，方可批准
    t_id = str(table_id)
    direct_children = CHILDREN_MAP.get(t_id, [])
    if direct_children:
        not_ready = [cid for cid in direct_children if not _is_table_approved(project_id, cid)]
        if not_ready:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "无法批准：存在未被批准的直接子表。",
                    "unapprovedChildren": not_ready,
                }
            )

    submissions_dir = DATA_DIR / f"{project_id}_data"
    submissions_dir.mkdir(parents=True, exist_ok=True)
    file_path = submissions_dir / f"{table_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Table data not found.")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read table file.")

    submit_payload = data.get('submit')
    if not submit_payload:
        raise HTTPException(status_code=400, detail="No submission to approve.")

    approved = copy.deepcopy(submit_payload)
    approved['approvedAt'] = datetime.now(BEIJING_TZ).isoformat()
    approved['approvedBy'] = user
    data['approved'] = approved

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write approval: {e}")

    # history uses operator and action time
    _append_history_record(submissions_dir, project_id, table_id, {"approvedAt": approved.get("approvedAt"), "submittedBy": user}, "approve")
    _log_action("approve", request, username=_extract_username(approved, request), details={"projectId": project_id, "tableId": table_id})
    return {"message": "Approved."}

@app.post("/project/{project_id}/table/{table_id}/unapprove")
async def unapprove_table(project_id: str, table_id: str, request: Request):
    user = _get_user_from_request(request)
    if not _can_approve(str(table_id), user, 'unapprove'):
        raise HTTPException(status_code=403, detail="Not allowed to unapprove this table.")

    # 规则：撤销某张子表的批准，必须确保其直接汇总表未处于“已批准”状态
    t_id = str(table_id)
    direct_parents = PARENT_MAP.get(t_id, [])
    if direct_parents:
        blocking = [pid for pid in direct_parents if _is_table_approved(project_id, pid)]
        if blocking:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "无法撤销：其直接汇总表处于已批准状态，请先撤销汇总表的批准。",
                    "approvedParents": blocking,
                }
            )

    submissions_dir = DATA_DIR / f"{project_id}_data"
    submissions_dir.mkdir(parents=True, exist_ok=True)
    file_path = submissions_dir / f"{table_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Table data not found.")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read table file.")

    if 'approved' in data:
        approved_snapshot = data['approved']
        del data['approved']
        # 记录撤销批准的操作信息，供仪表盘显示
        data['unapproved'] = {
            'unapprovedAt': datetime.now(BEIJING_TZ).isoformat(),
            'unapprovedBy': user,
        }
        # 若不存在提交快照，则用原批准快照回填 submit，确保状态可回退为“已提交”
        try:
            if 'submit' not in data and isinstance(approved_snapshot, dict):
                restored = copy.deepcopy(approved_snapshot)
                # 清理与批准相关的字段，保留原提交元数据
                restored.pop('approvedAt', None)
                restored.pop('approvedBy', None)
                data['submit'] = restored
        except Exception:
            pass
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to remove approval: {e}")
        _append_history_record(submissions_dir, project_id, table_id, {"unapprovedAt": data['unapproved']['unapprovedAt'], "submittedBy": user}, "unapprove")
        _log_action("unapprove", request, username=_extract_username(approved_snapshot, request), details={"projectId": project_id, "tableId": table_id})
    return {"message": "Unapproved."}


@app.post("/project/{project_id}/table/{table_id}/save_draft")
async def save_draft(project_id: str, table_id: str, request: Request, payload: dict = Body(...)):
    submissions_dir = DATA_DIR / f"{project_id}_data"
    submissions_dir.mkdir(parents=True, exist_ok=True)
    file_path = submissions_dir / f"{table_id}.json"
    _update_data_file(file_path, "temp", payload)
    _append_history_record(submissions_dir, project_id, table_id, {"savedAt": datetime.now(BEIJING_TZ).isoformat(), "submittedBy": _get_user_from_request(request) or _extract_username(payload, request)}, "save_draft")
    _log_action("save_draft", request, username=_extract_username(payload, request), details={"projectId": project_id, "tableId": table_id})
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

        # 表0仅汇总已批准的数据；未批准则跳过
        sub_data = sub_content.get("approved") or sub_content.get("submit")
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

            # 规则：表1汇总其子表的已批准版本；表2/3使用其子表的已提交版本；其它默认沿用已提交/草稿。
            if table_id == '1':
                sub_data = sub_content.get("approved") or sub_content.get("submit")
            elif table_id in ('2', '3'):
                sub_data = sub_content.get("submit")
            else:
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
async def get_table_data(project_id: str, table_id: str, request: Request):
    result = await get_table_data_recursive(project_id, table_id)
    username = _extract_username(None, request)
    has_temp = isinstance(result, dict) and bool(result.get('temp'))
    has_submit = isinstance(result, dict) and bool(result.get('submit'))
    details = {
        'projectId': project_id,
        'tableId': table_id,
        'hasTemp': has_temp,
        'hasSubmit': has_submit,
    }
    _log_action('load_table', request, username=username, details=details)
    if has_temp:
        _log_action('retrieve_draft', request, username=username, details=details)
    return result

@app.post("/project/{project_id}/table_statuses")
async def get_table_statuses(project_id: str, table_ids: List[str] = Body(...)):
    statuses = {}
    submissions_dir = DATA_DIR / f"{project_id}_data"
    for table_id in table_ids:
        file_path = submissions_dir / f"{table_id}.json"
        status_info = {"status": "new", "submittedAt": None, "submittedBy": None, "approvedAt": None, "approvedBy": None, "unapprovedAt": None, "unapprovedBy": None}

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

                # Approved has highest priority
                if data.get("approved"):
                    status_info["status"] = "approved"
                    status_info["approvedAt"] = data["approved"].get("approvedAt")
                    status_info["approvedBy"] = data["approved"].get("approvedBy")
                    # also surface submitted info if present
                    if data.get("submit"):
                        status_info["submittedAt"] = data["submit"].get("submittedAt")
                        status_info["submittedBy"] = data["submit"].get("submittedBy")

                # Capture unapprove (withdraw) meta for display, without changing status
                if data.get("unapproved"):
                    status_info["unapprovedAt"] = data["unapproved"].get("unapprovedAt")
                    status_info["unapprovedBy"] = data["unapproved"].get("unapprovedBy")

                # Check for a valid submission if not approved
                if status_info["status"] != "approved" and data.get("submit"):
                    submitted_by = data["submit"].get("submittedBy") or {}
                    # god 提交必须隐身：当提交者为 god 时，不记为“已提交”
                    is_god_submit = (
                        submitted_by.get("username") == "ww870411" or
                        submitted_by.get("globalRole") == "god"
                    )
                    if not is_god_submit:
                        status_info["status"] = "submitted"
                        status_info["submittedAt"] = data["submit"].get("submittedAt")
                        status_info["submittedBy"] = submitted_by

            except Exception:
                pass
        
        statuses[table_id] = status_info

    return statuses

@app.get("/")
def read_root():
    return {"Hello": "World"}

