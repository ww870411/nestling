import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import json
from pathlib import Path
import datetime
import traceback

# --- Configuration copied from frontend/srcs/projects/heating_plan_2025-2026/templates/subsidiaryTemplate.js ---
# This makes the script self-contained.

FIELD_CONFIG = [
  { "id": 1000, "name": 'metricid', "label": '指标序号', "type": 'basic', "component": 'label' },
  { "id": 1001, "name": 'name', "label": '指标名称', "type": 'basic', "component": 'label' },
  { "id": 1002, "name": 'unit', "label": '计量单位', "type": 'basic', "component": 'label' },
  { "id": 1003, "name": 'totals.plan', "label": '本期计划', "type": 'calculated', "component": 'display', "formula": 'VAL(2001)+VAL(2003)+VAL(2005)+VAL(2007)+VAL(2009)+VAL(2011)+VAL(2013)' },
  { "id": 1004, "name": 'totals.samePeriod', "label": '同期完成', "type": 'calculated', "component": 'display', "formula": 'VAL(2002)+VAL(2004)+VAL(2006)+VAL(2008)+VAL(2010)+VAL(2012)+VAL(2014)' },
  { "id": 1005, "name": 'totals.diffRate', "label": '差异率', "type": 'calculated', "component": 'display', "displayFormat": { 'type': 'percentage', 'places': 2 }, "formula": '(VAL(1003)-VAL(1004))/VAL(1004)' },
  { "id": 2001, "name": 'monthlyData.october.plan', "label": '10月-计划', "type": 'basic', "component": 'input' },
  { "id": 2002, "name": 'monthlyData.october.samePeriod', "label": '10月-同期', "type": 'basic', "component": 'display' },
  { "id": 2003, "name": 'monthlyData.november.plan', "label": '11月-计划', "type": 'basic', "component": 'input' },
  { "id": 2004, "name": 'monthlyData.november.samePeriod', "label": '11月-同期', "type": 'basic', "component": 'display' },
  { "id": 2005, "name": 'monthlyData.december.plan', "label": '12月-计划', "type": 'basic', "component": 'input' },
  { "id": 2006, "name": 'monthlyData.december.samePeriod', "label": '12月-同期', "type": 'basic', "component": 'display' },
  { "id": 2007, "name": 'monthlyData.january.plan', "label": '1月-计划', "type": 'basic', "component": 'input' },
  { "id": 2008, "name": 'monthlyData.january.samePeriod', "label": '1月-同期', "type": 'basic', "component": 'display' },
  { "id": 2009, "name": 'monthlyData.february.plan', "label": '2月-计划', "type": 'basic', "component": 'input' },
  { "id": 2010, "name": 'monthlyData.february.samePeriod', "label": '2月-同期', "type": 'basic', "component": 'display' },
  { "id": 2011, "name": 'monthlyData.march.plan', "label": '3月-计划', "type": 'basic', "component": 'input' },
  { "id": 2012, "name": 'monthlyData.march.samePeriod', "label": '3月-同期', "type": 'basic', "component": 'display' },
  { "id": 2013, "name": 'monthlyData.april.plan', "label": '4月-计划', "type": 'basic', "component": 'input' },
  { "id": 2014, "name": 'monthlyData.april.samePeriod', "label": '4月-同期', "type": 'basic', "component": 'display' },
]

REPORT_TEMPLATE = [
  { "id": 1, "name": '月平均高温', "type": 'basic' }, { "id": 2, "name": '月平均低温', "type": 'basic' },
  { "id": 3, "name": '发电机组容量', "type": 'basic' }, { "id": 4, "name": '燃煤锅炉装机容量', "type": 'basic' },
  { "id": 5, "name": '电锅炉/热泵装机容量', "type": 'basic' }, { "id": 6, "name": '发电量', "type": 'basic' },
  { "id": 7, "name": '供热量', "type": 'calculated' }, { "id": 8, "name": '其中：1.供汽量', "type": 'basic' },
  { "id": 9, "name": '2.高温水供热量', "type": 'basic' }, { "id": 10, "name": '3.低真空供热量', "type": 'basic' },
  { "id": 11, "name": '4.低温水供热量', "type": 'basic' }, { "id": 12, "name": '5.电锅炉/热泵供热量', "type": 'basic' },
  { "id": 13, "name": '售电量', "type": 'basic' }, { "id": 14, "name": '售汽量', "type": 'basic' },
  { "id": 15, "name": '关联交易汽量', "type": 'basic' }, { "id": 16, "name": '关联交易高温水量', "type": 'basic' },
  { "id": 17, "name": '期末挂网面积', "type": 'basic' }, { "id": 18, "name": '期末供暖收费面积', "type": 'calculated' },
  { "id": 19, "name": '1.汽站面积', "type": 'basic' }, { "id": 20, "name": '2.高温水站面积', "type": 'basic' },
  { "id": 21, "name": '3.低真空站面积', "type": 'basic' }, { "id": 22, "name": '4.低温水供热面积', "type": 'basic' },
  { "id": 23, "name": '5.电锅炉/热泵面积', "type": 'basic' }, { "id": 24, "name": '高温水销售量', "type": 'basic' },
  { "id": 25, "name": '生产耗原煤量', "type": 'calculated' }, { "id": 26, "name": '其中：1.发电耗原煤量', "type": 'basic' },
  { "id": 27, "name": '2.供热耗原煤量', "type": 'basic' }, { "id": 28, "name": '耗标煤总量', "type": 'calculated' },
  { "id": 29, "name": '其中：1.发电耗标煤量', "type": 'calculated' }, { "id": 30, "name": '1.1煤折标煤耗量', "type": 'basic' },
  { "id": 31, "name": '1.2油折标煤耗量', "type": 'basic' }, { "id": 32, "name": '2.供热耗标煤量', "type": 'calculated' },
  { "id": 33, "name": '2.1煤折标煤耗量', "type": 'basic' }, { "id": 34, "name": '2.2油折标煤耗量', "type": 'basic' },
  { "id": 35, "name": '煤折标煤耗量', "type": 'calculated' }, { "id": 36, "name": '耗油量', "type": 'calculated' },
  { "id": 37, "name": '其中：1.发电耗油量', "type": 'basic' }, { "id": 38, "name": '2.供热耗油量', "type": 'basic' },
  { "id": 39, "name": '外购热量', "type": 'basic' }, { "id": 40, "name": '耗水量', "type": 'calculated' },
  { "id": 41, "name": '其中：1.电厂耗水量', "type": 'basic' }, { "id": 42, "name": '2.电厂一次网补水量', "type": 'calculated' },
  { "id": 43, "name": '2.1高温水首站补水量', "type": 'basic' }, { "id": 44, "name": '2.2低真空补水量', "type": 'basic' },
  { "id": 45, "name": '3.换热站补水量', "type": 'basic' }, { "id": 46, "name": '4.燃煤锅炉房耗水量', "type": 'basic' },
  { "id": 47, "name": '5.电锅炉/热泵耗水量', "type": 'basic' }, { "id": 48, "name": '耗自来水量', "type": 'basic' },
  { "id": 49, "name": '耗再生水/井水量', "type": 'basic' }, { "id": 50, "name": '耗酸量', "type": 'basic' },
  { "id": 51, "name": '耗碱量', "type": 'basic' }, { "id": 52, "name": '耗石灰石量（粗）', "type": 'basic' },
  { "id": 53, "name": '耗石灰石粉量（细）', "type": 'basic' }, { "id": 54, "name": '耗氨水量', "type": 'basic' },
  { "id": 55, "name": '耗氧化镁量', "type": 'basic' }, { "id": 56, "name": '耗脱硝剂量', "type": 'basic' },
  { "id": 57, "name": '耗阻垢剂量', "type": 'basic' }, { "id": 58, "name": '耗杀菌剂量', "type": 'basic' },
  { "id": 59, "name": '耗钢球量', "type": 'basic' }, { "id": 60, "name": '耗天然气量', "type": 'basic' },
  { "id": 61, "name": '站内耗热量', "type": 'basic' }, { "id": 62, "name": '耗电量', "type": 'calculated' },
  { "id": 63, "name": '综合厂用电量', "type": 'calculated' }, { "id": 64, "name": '其中：1.非生产厂用电量', "type": 'basic' },
  { "id": 65, "name": '2.生产厂用电量', "type": 'calculated' }, { "id": 66, "name": '2.1发电厂用电量', "type": 'basic' },
  { "id": 67, "name": '2.2供热厂用电量', "type": 'basic' }, { "id": 68, "name": '外购电量', "type": 'calculated' },
  { "id": 69, "name": '其中：1.电厂外购电量', "type": 'basic' }, { "id": 70, "name": '2.燃煤锅炉房外购电量', "type": 'basic' },
  { "id": 71, "name": '3.换热站外购电量', "type": 'basic' }, { "id": 72, "name": '4.电锅炉/热泵外购电量', "type": 'basic' },
  { "id": 73, "name": '脱硫脱销耗水量', "type": 'basic' }, { "id": 74, "name": '脱硫脱硝耗电量', "type": 'basic' },
  { "id": 75, "name": '生产产出率', "type": 'calculated' }, { "id": 76, "name": '综合产出率', "type": 'calculated' },
  { "id": 77, "name": '全厂热效率', "type": 'calculated' }, { "id": 78, "name": '热电比', "type": 'calculated' },
  { "id": 79, "name": '热分摊比', "type": 'calculated' }, { "id": 80, "name": '发电设备利用率', "type": 'calculated' },
  { "id": 81, "name": '供热设备利用率', "type": 'calculated' }, { "id": 82, "name": '综合厂用电率', "type": 'calculated' },
  { "id": 83, "name": '发电厂用电率', "type": 'calculated' }, { "id": 84, "name": '供热厂用电率', "type": 'calculated' },
  { "id": 85, "name": '发电标准煤耗率', "type": 'calculated' }, { "id": 86, "name": '供电标准煤耗率', "type": 'calculated' },
  { "id": 87, "name": '供热标准煤耗率', "type": 'calculated' }, { "id": 88, "name": '发电水耗率', "type": 'calculated' },
  { "id": 89, "name": '供热水耗率', "type": 'calculated' }, { "id": 90, "name": '供暖热耗率', "type": 'calculated' },
  { "id": 91, "name": '供暖水耗率', "type": 'calculated' }, { "id": 92, "name": '供暖电耗率', "type": 'calculated' },
  { "id": 93, "name": '入炉煤低位发热量', "type": 'calculated' }, { "id": 94, "name": '供热发电收入', "type": 'calculated' },
  { "id": 95, "name": '暖收入', "type": 'basic' }, { "id": 96, "name": '暖单价', "type": 'calculated' },
  { "id": 97, "name": '电收入', "type": 'basic' }, { "id": 98, "name": '电单价', "type": 'calculated' },
  { "id": 99, "name": '售汽收入', "type": 'basic' }, { "id": 100, "name": '汽平均单价', "type": 'calculated' },
  { "id": 101, "name": '售高温水收入', "type": 'basic' }, { "id": 102, "name": '高温水平均单价', "type": 'calculated' },
  { "id": 103, "name": '购热成本', "type": 'basic' }, { "id": 104, "name": '热单价', "type": 'calculated' },
  { "id": 105, "name": '煤成本', "type": 'basic' }, { "id": 106, "name": '标煤单价', "type": 'calculated' },
  { "id": 107, "name": '购电成本', "type": 'basic' }, { "id": 108, "name": '购电单价', "type": 'calculated' },
  { "id": 109, "name": '水成本', "type": 'basic' }, { "id": 110, "name": '水单价', "type": 'calculated' },
  { "id": 111, "name": '天然气成本', "type": 'basic' }, { "id": 112, "name": '购天然气单价', "type": 'calculated' },
  { "id": 113, "name": '劳务费', "type": 'basic' }, { "id": 114, "name": '抢修费', "type": 'basic' },
  { "id": 115, "name": '毛利', "type": 'calculated' },
]

class HistoryImporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("历史数据导入工具")
        self.root.geometry("600x450")

        self.csv_path = tk.StringVar()
        self.output_id = tk.StringVar()

        # --- Widgets ---
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=5)

        # CSV File Selection
        tk.Label(top_frame, text="CSV 文件路径:").pack(side="left", pady=5)
        tk.Entry(top_frame, textvariable=self.csv_path, width=50, state='readonly').pack(side="left", expand=True, fill="x", pady=5)
        tk.Button(top_frame, text="浏览...", command=self.select_csv_file).pack(side="left", padx=5, pady=5)

        # Output File ID
        id_frame = tk.Frame(root)
        id_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(id_frame, text="输出文件ID:").pack(side="left", pady=5)
        tk.Entry(id_frame, textvariable=self.output_id, width=20).pack(side="left", pady=5)
        
        # Start Button
        tk.Button(root, text="开始导入", command=self.process_file, font=('Arial', 12, 'bold'), bg='lightblue').pack(pady=10)

        # Log Text Area
        log_frame = tk.Frame(root)
        log_frame.pack(expand=True, fill="both", padx=10, pady=10)
        tk.Label(log_frame, text="日志与错误信息:").pack(anchor="w")
        self.log_text = tk.Text(log_frame, height=10, width=70, bg="#f0f0f0", relief="sunken", borderwidth=1)
        self.log_text.pack(side="left", expand=True, fill="both")
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def select_csv_file(self):
        path = filedialog.askopenfilename(
            title="请选择CSV文件",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if path:
            self.csv_path.set(path)

    def process_file(self):
        self.log_text.delete(1.0, tk.END)
        csv_file = self.csv_path.get()
        output_id = self.output_id.get().strip()

        if not csv_file:
            messagebox.showerror("错误", "请先选择一个CSV文件！")
            return
        if not output_id:
            messagebox.showerror("错误", "请输入输出文件ID！")
            return

        try:
            self.log("开始处理...")
            # --- Main Conversion Logic ---
            report_template_map = {item['id']: item for item in REPORT_TEMPLATE}
            field_label_map = {field['label']: field for field in FIELD_CONFIG}

            table_data = []
            
            with open(csv_file, mode='r', encoding='gbk') as f:
                reader = csv.reader(f)
                header = None
                data_started = False

                for i, row in enumerate(reader):
                    if not row or not any(row):
                        continue # Skip empty rows

                    # --- Find header row ---
                    if not data_started:
                        if "指标序号" in row:
                            self.log(f"在第 {i+1} 行找到表头，开始处理数据...")
                            header = row
                            data_started = True
                        continue # Skip until header is found
                    
                    # --- Process data rows ---
                    try:
                        metric_id = int(row[0])
                        metric_def = report_template_map.get(metric_id)
                        if not metric_def:
                            self.log(f"警告: 跳过第 {i+1} 行，未知的指标ID: {row[0]}")
                            continue

                        row_dict = {header[j]: cell for j, cell in enumerate(row) if j < len(header)}

                        metric_object = {
                            "metricId": metric_id,
                            "metricName": metric_def['name'],
                            "type": metric_def['type'],
                            "values": []
                        }
                        
                        has_non_zero_data = False

                        # Populate values
                        for field in FIELD_CONFIG:
                            field_id = field['id']
                            label = field['label']
                            cell_value = row_dict.get(label, '')

                            final_value = cell_value
                            if field['component'] != 'label':
                                try:
                                    num_val = float(cell_value) if cell_value and cell_value.strip() else 0
                                    final_value = num_val
                                    if num_val != 0:
                                        has_non_zero_data = True
                                except (ValueError, TypeError):
                                    final_value = cell_value # Keep as string if conversion fails
                            
                            metric_object['values'].append({
                                "fieldId": field_id,
                                "fieldName": field['name'],
                                "fieldLabel": label,
                                "value": final_value
                            })
                        
                        if has_non_zero_data:
                            metric_object['force'] = True
                        
                        table_data.append(metric_object)

                    except (ValueError, IndexError) as row_err:
                        self.log(f"警告: 跳过第 {i+1} 行，数据格式无效。错误: {row_err}")
                        continue

            if not data_started:
                raise ValueError("未在CSV文件中找到有效的表头行 (需包含'指标序号')")

            # --- Assemble final payload ---
            payload = {
                "submit": {
                    "submittedAt": datetime.datetime.now().isoformat(),
                    "table": {
                        "id": output_id,
                        "name": f"Imported History for Table {output_id}",
                        "template": "subsidiaryTemplate"
                    },
                    "submittedBy": {
                        "username": "history_importer"
                    },
                    "tableData": table_data
                }
            }

            # --- Write JSON file ---
            output_dir = Path("historyin")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{output_id}.json"

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)

            self.log(f"处理完成！总共处理了 {len(table_data)} 行指标。")
            messagebox.showinfo("成功", f"文件已成功导入并保存至：\n{output_path.resolve()}")

        except Exception as e:
            self.log("发生严重错误！")
            self.log(traceback.format_exc())
            messagebox.showerror("导入失败", f"处理文件时发生错误，请查看日志获取详细信息。")


if __name__ == "__main__":
    root = tk.Tk()
    app = HistoryImporterApp(root)
    root.mainloop()