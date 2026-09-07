import pandas as pd
from datetime import datetime

def generate_excel_report(test_results_list, output_filename=None):
    print("\n📤 [輸出模組] 準備生成 Excel 報表...")
    
    report_data = []
    for item in test_results_list:
        row = {
            "NO.": item.get("no", ""),
            "應用系統名稱": item.get("app_name", ""),
            "系統負責部門": item.get("department", ""),
            "系統負責單位": item.get("unit", ""), 
            "負責人": item.get("owner", ""),
            "URL環境": item.get("env", ""),
            "URL": item.get("url", ""),
            "檢視發現": item.get("finding", ""),   
            "A. 預計改善日": "",                   
            "B. 備註說明": ""                      
        }
        report_data.append(row)
        
    df_report = pd.DataFrame(report_data)
    
    if not output_filename:
        today = datetime.now().strftime("%Y%m%d")
        output_filename = f"資安查核結果_{today}.xlsx"
        
    df_report.to_excel(output_filename, index=False)
    print(f"✅ [輸出模組] 報表已存檔至：{output_filename}")
