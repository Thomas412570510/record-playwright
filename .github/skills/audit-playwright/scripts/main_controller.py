import os
import sys
import tkinter as tk
from tkinter import filedialog
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from data_extractor import extract_tasks_from_excel
from report_generator import generate_excel_report
from security_tester import test_login_reset

def get_file_path_via_window():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True) 
    file_path = filedialog.askopenfilename(
        title="請選擇系統盤點 Excel 檔案",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    return file_path

def main():
    print("====================================")
    print("🛡️ 啟動全自動資安查核腳本系統")
    print("====================================")
    
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        excel_path = get_file_path_via_window()
        
    if not excel_path:
        print("⚠️ 未選擇檔案，程式結束。")
        sys.exit(0)
        
    tasks_list = extract_tasks_from_excel(excel_path)
    if not tasks_list:
        print("⚠️ 未能提取任何有效任務，請檢查 Excel 格式。")
        sys.exit(0)

    completed_results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for task in tasks_list:
            print(f"\n------------------------------------")
            print(f"🎯 正在測試: {task['app_name']}")
            print(f"🔗 {task['url']}")
            
            finding_str = test_login_reset(page, task['url'])
            print(f"📝 檢視發現: {finding_str}")
            
            task['finding'] = finding_str 
            completed_results.append(task)

        browser.close()

    generate_excel_report(completed_results)

if __name__ == "__main__":
    main()
