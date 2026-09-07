import pandas as pd

def extract_tasks_from_excel(file_path):
    print(f"📥 [讀取模組] 正在解析: {file_path}")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"❌ 讀取 Excel 失敗: {e}")
        return []
        
    tasks = []
    for index, row in df.iterrows():
        # 尋找含有 URL_ 的欄位，若無則嘗試找 URL
        url = row.get('URL_') if 'URL_' in df.columns else row.get('URL')
        if pd.isna(url) or not str(url).strip():
            continue 
            
        task_info = {
            "no": index + 1,
            "app_name": row.get("應用系統名稱", ""),
            "department": row.get("系統負責部門", row.get("部門", "")),
            "unit": row.get("系統負責單位", ""),
            "owner": row.get("負責人", ""),
            "env": row.get("URL環境", ""),
            "url": str(url).strip()
        }
        tasks.append(task_info)
        
    print(f"✅ [讀取模組] 成功提取 {len(tasks)} 筆任務資料！")
    return tasks
