---
name: audit-playwright
description: 自動化資安稽核工具：讀取Excel進行批次登入與欄位重置檢測，並匯出查核報表。
---

# Audit Playwright 企業資安查核自動化

這個 Skill 用於執行全自動的資安查核任務 (Data-Driven Security Testing)。
當使用者輸入例如：「幫我跑資安查核」、「測試 Excel 裡的網址」、「執行登入弱點掃描」時觸發。

## 核心能力
1. \data_extractor.py\: 負責讀取資安盤點表 (Excel)，萃取目標網址與系統資訊。
2. \security_tester.py\: 利用 Playwright 進行萬用特徵登入，並驗證報錯後「密碼、驗證碼欄位是否清空」。
3. \eport_generator.py\: 將測試結果輸出為符合稽核格式的 Excel 報表。
4. \main_controller.py\: 控制以上三者的主流程。

## 執行方式
進入 \scripts\ 資料夾後執行主程式：
\python main_controller.py\
(程式會自動彈出視窗讓使用者選取來源 Excel 檔案)
