---
name: payload-inspector
description: 攔截與分析網頁送出的網路請求 Payload，專門用於稽核登入時的敏感參數（如 rangpwd、password、帳號傳輸格式與加密狀態）。
---

# Payload Inspector 網路傳輸稽核技能

本技能專為 Web 資安查核與封包傳輸檢測設計。
透過 Playwright 網路監聽機制，攔截所有由瀏覽器發送的 HTTP POST/PUT 請求 Payload，自動提取關鍵欄位（例如 `rangpwd`、`password`、`token`），用以評估傳輸安全性（如是否明文傳輸、是否有前端雜湊或加密處理）。

## 核心功能
1. **即時攔截 Network 請求**：取代手動開啟 F12 Network 分頁，全自動監聽網頁所有送出的封包。
2. **多格式自動解析**：自動識別並解析 `application/json`、`application/x-www-form-urlencoded` 以及 Multipart 資料。
3. **敏感參數偵測**：針對 `rangpwd`、`pwd`、`password`、`account` 等資安稽核關鍵欄位進行提取與狀態評估。
4. **輸出稽核紀錄**：可將攔截到的 Payload 存成 JSON 檔或整合進資安報表中。

## 檔案結構
- `scripts/payload_listener.py`: 提供網路請求監聽與 Payload 解析的核心函式庫。
- `scripts/inspect_login.py`: 獨立可執行的檢測主程式，輸入目標網址即可進行登入測試與封包攔截。

## 執行方式
於 `scripts` 目錄下執行：
```bash
python inspect_login.py
```
