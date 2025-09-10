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
SUBMISSIONS_DIR = Path("app/data/heating_plan_2025-2026_data")
SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)

# Load menu data from the JSON file
with open("app/data/menucopy.json", "r", encoding="utf-8") as f:
    MENU_DATA = json.load(f)

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

async def get_table_0_data():
    """
    Special function to aggregate data for Table 0.
    """
    table_config = ALL_TABLES.get('0')
    if not table_config:
        return {}

    # Based on frontend/src/projects/heating_plan_2025-2026/templates/groupTemplate.js
    report_template = [
        {'id': 1, 'name': '月平均高温', 'unit': '℃'}, {'id': 2, 'name': '月平均低温', 'unit': '℃'},
        {'id': 3, 'name': '发电机组容量', 'unit': '万kW'}, {'id': 4, 'name': '燃煤锅炉装机容量', 'unit': 'MW'},
        {'id': 5, 'name': '电锅炉/热泵装机容量', 'unit': 'MW'}, {'id': 6, 'name': '发电量', 'unit': '万kWh'},
        {'id': 7, 'name': '供热量', 'unit': 'GJ'}, {'id': 8, 'name': '其中：1.供汽量', 'unit': '吨'},
        {'id': 9, 'name': '2.高温水供热量', 'unit': 'GJ'}, {'id': 10, 'name': '3.低真空供热量', 'unit': 'GJ'},
        {'id': 11, 'name': '4.低温水供热量', 'unit': 'GJ'}, {'id': 12, 'name': '5.电锅炉/热泵供热量', 'unit': 'GJ'},
        {'id': 13, 'name': '售电量', 'unit': '万kWh'}, {'id': 14, 'name': '售汽量', 'unit': '吨'},
        {'id': 15, 'name': '关联交易汽量', 'unit': '吨'}, {'id': 16, 'name': '关联交易高温水量', 'unit': 'GJ'},
        {'id': 17, 'name': '期末挂网面积', 'unit': '㎡'}, {'id': 18, 'name': '期末供暖收费面积', 'unit': '㎡'},
        {'id': 19, 'name': '1.汽站面积', 'unit': '㎡'}, {'id': 20, 'name': '2.高温水站面积', 'unit': '㎡'},
        {'id': 21, 'name': '3.低真空站面积', 'unit': '㎡'}, {'id': 22, 'name': '4.低温水供热面积', 'unit': '㎡'},
        {'id': 23, 'name': '5.电锅炉/热泵面积', 'unit': '㎡'}, {'id': 24, 'name': '高温水销售量', 'unit': 'GJ'},
        {'id': 25, 'name': '生产耗原煤量', 'unit': '吨'}, {'id': 26, 'name': '其中：1.发电耗原煤量', 'unit': '吨'},
        {'id': 27, 'name': '2.供热耗原煤量', 'unit': '吨'}, {'id': 28, 'name': '耗标煤总量', 'unit': '吨'},
        {'id': 29, 'name': '其中：1.发电耗标煤量', 'unit': '吨'}, {'id': 30, 'name': '1.1煤折标煤耗量', 'unit': '吨'},
        {'id': 31, 'name': '1.2油折标煤耗量', 'unit': '吨'}, {'id': 32, 'name': '2.供热耗标煤量', 'unit': '吨'},
        {'id': 33, 'name': '2.1煤折标煤耗量', 'unit': '吨'}, {'id': 34, 'name': '2.2油折标煤耗量', 'unit': '吨'},
        {'id': 35, 'name': '煤折标煤耗量', 'unit': '吨'}, {'id': 36, 'name': '耗油量', 'unit': '吨'},
        {'id': 37, 'name': '其中：1.发电耗油量', 'unit': '吨'}, {'id': 38, 'name': '2.供热耗油量', 'unit': '吨'},
        {'id': 39, 'name': '外购热量', 'unit': 'GJ'}, {'id': 40, 'name': '耗水量', 'unit': '吨'},
        {'id': 41, 'name': '其中：1.电厂耗水量', 'unit': '吨'}, {'id': 42, 'name': '2.电厂一次网补水量', 'unit': '吨'},
        {'id': 43, 'name': '2.1高温水首站补水量', 'unit': '吨'}, {'id': 44, 'name': '2.2低真空补水量', 'unit': '吨'},
        {'id': 45, 'name': '3.换热站补水量', 'unit': '吨'}, {'id': 46, 'name': '4.燃煤锅炉房耗水量', 'unit': '吨'},
        {'id': 47, 'name': '5.电锅炉/热泵耗水量', 'unit': '吨'}, {'id': 48, 'name': '耗自来水量', 'unit': '吨'},
        {'id': 49, 'name': '耗再生水/井水量', 'unit': '吨'}, {'id': 50, 'name': '耗酸量', 'unit': '吨'},
        {'id': 51, 'name': '耗碱量', 'unit': '吨'}, {'id': 52, 'name': '耗石灰石量（粗）', 'unit': '吨'},
        {'id': 53, 'name': '耗石灰石粉量（细）', 'unit': '吨'}, {'id': 54, 'name': '耗氨水量', 'unit': '吨'},
        {'id': 55, 'name': '耗氧化镁量', 'unit': '吨'}, {'id': 56, 'name': '耗脱硝剂量', 'unit': '吨'},
        {'id': 57, 'name': '耗阻垢剂量', 'unit': '吨'}, {'id': 58, 'name': '耗杀菌剂量', 'unit': '吨'},
        {'id': 59, 'name': '耗钢球量', 'unit': '吨'}, {'id': 60, 'name': '耗天然气量', 'unit': '万m3'},
        {'id': 61, 'name': '站内耗热量', 'unit': 'GJ'}, {'id': 62, 'name': '耗电量', 'unit': '万kWh'},
        {'id': 63, 'name': '综合厂用电量', 'unit': '万kWh'}, {'id': 64, 'name': '其中：1.非生产厂用电量', 'unit': '万kWh'},
        {'id': 65, 'name': '2.生产厂用电量', 'unit': '万kWh'}, {'id': 66, 'name': '2.1发电厂用电量', 'unit': '万kWh'},
        {'id': 67, 'name': '2.2供热厂用电量', 'unit': '万kWh'}, {'id': 68, 'name': '外购电量', 'unit': '万kWh'},
        {'id': 69, 'name': '其中：1.电厂外购电量', 'unit': '万kWh'}, {'id': 70, 'name': '2.燃煤锅炉房外购电量', 'unit': '万kWh'},
        {'id': 71, 'name': '3.换热站外购电量', 'unit': '万kWh'}, {'id': 72, 'name': '4.电锅炉/热泵外购电量', 'unit': '万kWh'},
        {'id': 73, 'name': '脱硫脱销耗水量', 'unit': '吨'}, {'id': 74, 'name': '脱硫脱硝耗电量', 'unit': '万kWh'},
        {'id': 75, 'name': '生产产出率', 'unit': '%'}, {'id': 76, 'name': '综合产出率', 'unit': '%'},
        {'id': 77, 'name': '全厂热效率', 'unit': '%'}, {'id': 78, 'name': '热电比', 'unit': '%'},
        {'id': 79, 'name': '热分摊比', 'unit': '%'}, {'id': 80, 'name': '发电设备利用率', 'unit': '%'},
        {'id': 81, 'name': '供热设备利用率', 'unit': '%'}, {'id': 82, 'name': '综合厂用电率', 'unit': '%'},
        {'id': 83, 'name': '发电厂用电率', 'unit': '%'}, {'id': 84, 'name': '供热厂用电率', 'unit': 'kWh/GJ'},
        {'id': 85, 'name': '发电标准煤耗率', 'unit': 'g/kWh'}, {'id': 86, 'name': '供电标准煤耗率', 'unit': 'g/kWh'},
        {'id': 87, 'name': '供热标准煤耗率', 'unit': 'kg/GJ'}, {'id': 88, 'name': '发电水耗率', 'unit': '吨/万kWh'},
        {'id': 89, 'name': '供热水耗率', 'unit': '吨/GJ'}, {'id': 90, 'name': '供暖热耗率', 'unit': 'GJ/㎡'},
        {'id': 91, 'name': '供暖水耗率', 'unit': 'kg/㎡'}, {'id': 92, 'name': '供暖电耗率', 'unit': 'kWh/㎡'},
        {'id': 93, 'name': '入炉煤低位发热量', 'unit': 'kJ/kg'}, {'id': 94, 'name': '供热发电收入', 'unit': '万元'},
        {'id': 95, 'name': '暖收入', 'unit': '万元'}, {'id': 96, 'name': '暖单价', 'unit': '元/㎡'},
        {'id': 97, 'name': '电收入', 'unit': '万元'}, {'id': 98, 'name': '电单价', 'unit': '元/kWh'},
        {'id': 99, 'name': '售汽收入', 'unit': '万元'}, {'id': 100, 'name': '汽平均单价', 'unit': '元/吨'},
        {'id': 101, 'name': '售高温水收入', 'unit': '万元'}, {'id': 102, 'name': '高温水平均单价', 'unit': '元/GJ'},
        {'id': 103, 'name': '购热成本', 'unit': '万元'}, {'id': 104, 'name': '热单价', 'unit': '元/GJ'},
        {'id': 105, 'name': '煤成本', 'unit': '万元'}, {'id': 106, 'name': '标煤单价', 'unit': '元/吨'},
        {'id': 107, 'name': '购电成本', 'unit': '万元'}, {'id': 108, 'name': '购电单价', 'unit': '元/kWh'},
        {'id': 109, 'name': '水成本', 'unit': '万元'}, {'id': 110, 'name': '水单价', 'unit': '元/吨'},
        {'id': 111, 'name': '天然气成本', 'unit': '万元'}, {'id': 112, 'name': '购天然气单价', 'unit': '元/吨'},
        {'id': 113, 'name': '劳务费', 'unit': '万元'}, {'id': 114, 'name': '抢修费', 'unit': '万元'},
        {'id': 115, 'name': '毛利', 'unit': '万元'}
    ]
    
    field_config = [
        {'id': 1001, 'name': 'name'}, {'id': 1002, 'name': 'unit'},
        {'id': 1003, 'name': 'group.plan'}, {'id': 1004, 'name': 'group.samePeriod'}, {'id': 1005, 'name': 'group.diffRate'},
        {'id': 1006, 'name': 'downtown.plan'}, {'id': 1007, 'name': 'downtown.samePeriod'}, {'id': 1008, 'name': 'downtown.diffRate'},
        {'id': 1009, 'name': 'beihai.plan'}, {'id': 1010, 'name': 'beihai.samePeriod'}, {'id': 1011, 'name': 'beihai.diffRate'},
        {'id': 1012, 'name': 'xianghai.plan'}, {'id': 1013, 'name': 'xianghai.samePeriod'}, {'id': 1014, 'name': 'xianghai.diffRate'},
        {'id': 1015, 'name': 'jinzhou.plan'}, {'id': 1016, 'name': 'jinzhou.samePeriod'}, {'id': 1017, 'name': 'jinzhou.diffRate'},
        {'id': 1018, 'name': 'beifang.plan'}, {'id': 1019, 'name': 'beifang.samePeriod'}, {'id': 1020, 'name': 'beifang.diffRate'},
        {'id': 1021, 'name': 'jinpu.plan'}, {'id': 1022, 'name': 'jinpu.samePeriod'}, {'id': 1023, 'name': 'jinpu.diffRate'},
        {'id': 1024, 'name': 'zhuanghe.plan'}, {'id': 1025, 'name': 'zhuanghe.samePeriod'}, {'id': 1026, 'name': 'zhuanghe.diffRate'},
        {'id': 1027, 'name': 'research.plan'}, {'id': 1028, 'name': 'research.samePeriod'}, {'id': 1029, 'name': 'research.diffRate'}
    ]

    # Create maps from the subsidiary key (e.g., 'group') to the target fieldId
    key_to_plan_field_id = { field['name'].split('.')[0]: field['id'] for field in field_config if '.plan' in field['name'] }
    key_to_same_period_field_id = { field['name'].split('.')[0]: field['id'] for field in field_config if '.samePeriod' in field['name'] }

    # Initialize tableData
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
            value = 0  # Default to 0 for all data cells

            if field_id == 1001: value = row_template['name']
            elif field_id == 1002: value = row_template['unit']
            new_row["values"].append({"fieldId": field_id, "value": value})
        table_data.append(new_row)

    # Fetch and populate plan and samePeriod data
    subsidiaries_map = table_config.get("subsidiaries", {})
    for sub_key, sub_id in subsidiaries_map.items():
        sub_content = await get_table_data_recursive(sub_id)
        sub_data = sub_content.get("submit") or sub_content.get("temp")
        if not sub_data or not isinstance(sub_data.get("tableData"), list):
            continue

        sub_values = {}
        for row in sub_data.get("tableData", []):
            metric_id = row.get("metricId")
            if not metric_id: continue
            plan_val, same_period_val = 0, 0
            for cell in row.get("values", []):
                if cell.get("fieldId") == 1003: plan_val = cell.get("value", 0)
                if cell.get("fieldId") == 1004: same_period_val = cell.get("value", 0)
            sub_values[metric_id] = {"plan": plan_val, "samePeriod": same_period_val}

        target_plan_id = key_to_plan_field_id.get(sub_key)
        target_same_period_id = key_to_same_period_field_id.get(sub_key)
        if not target_plan_id or not target_same_period_id: continue

        for agg_row in table_data:
            metric_id = agg_row.get("metricId")
            if metric_id in sub_values:
                for agg_cell in agg_row.get("values", []):
                    if agg_cell.get("fieldId") == target_plan_id:
                        agg_cell["value"] = sub_values[metric_id]["plan"]
                    elif agg_cell.get("fieldId") == target_same_period_id:
                        agg_cell["value"] = sub_values[metric_id]["samePeriod"]

    aggregated_payload = {
        "table": {"id": table_config.get("id"), "name": table_config.get("name")},
        "tableData": table_data,
        "submittedAt": None,
        "submittedBy": None
    }

    return {"submit": aggregated_payload}


async def get_table_data_recursive(table_id: str):
    if table_id == '0':
        return await get_table_0_data()

    table_config = ALL_TABLES.get(table_id)
    if not table_config:
        return {}

    calculated_field_ids = {1004, 1005} # REMOVED 1003
    calculated_metric_ids = {
        7, 18, 25, 28, 29, 32, 35, 36, 40, 42, 62, 63, 65, 68, 75, 76, 77, 78, 79, 80, 81, 
        82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 96, 98, 100, 102, 104, 106, 
        108, 110, 112, 115
    }

    if table_config.get("type") != "summary" or not table_config.get("subsidiaries"):
        file_path = SUBMISSIONS_DIR / f"{table_id}.json"
        if not file_path.exists(): return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return {}

    if table_config.get("type") == "summary" and isinstance(table_config.get("subsidiaries"), list):
        aggregated_payload = None
        subsidiary_ids = table_config.get("subsidiaries", [])
        exclusion_set = set(table_config.get("aggregationExclusions", []))

        for sub_id in subsidiary_ids:
            try:
                sub_content = await get_table_data_recursive(sub_id)
                sub_data = sub_content.get("submit") or sub_content.get("temp")
                if not sub_data or not isinstance(sub_data.get("tableData"), list): continue

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
                                if isinstance(cell.get("value"), (int, float)): cell["value"] = 0
                                if "explanation" in cell: del cell["explanation"]
                
                sub_data_map = {row["metricId"]: row for row in sub_data.get("tableData", []) if row.get("metricId")}

                for agg_row in aggregated_payload.get("tableData", []):
                    metric_id = agg_row.get("metricId")
                    if not metric_id or metric_id in exclusion_set or metric_id in calculated_metric_ids: continue
                    
                    if metric_id in sub_data_map:
                        sub_row = sub_data_map[metric_id]
                        sub_cell_map = {cell["fieldId"]: cell.get("value", 0) for cell in sub_row.get("values", []) if cell.get("fieldId")}
                        
                        for agg_cell in agg_row.get("values", []):
                            field_id = agg_cell.get("fieldId")
                            if not field_id or field_id in calculated_field_ids: continue

                            if isinstance(agg_cell.get("value"), (int, float)):
                                current_val = agg_cell.get("value", 0)
                                agg_cell["value"] = current_val + sub_cell_map.get(field_id, 0)

            except Exception: continue

        summary_file_path = SUBMISSIONS_DIR / f"{table_id}.json"
        if summary_file_path.exists() and aggregated_payload is not None:
            try:
                with open(summary_file_path, "r", encoding="utf-8") as f: summary_content = json.load(f)
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


@app.get("/data/table/{table_id}")
async def get_table_data(table_id: str):
    return await get_table_data_recursive(table_id)

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