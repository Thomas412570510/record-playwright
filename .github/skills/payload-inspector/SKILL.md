---
name: payload-inspector
description: 攔截並稽核網頁發送的網路請求 Payload，自動檢測明文密碼傳輸與內部 IPv4 位址洩漏。
---

# Payload Inspector 網路傳輸與機敏資訊稽核技能

本技能專為資安查核、弱點評估與網路傳輸檢測設計。
透過 Playwright 網路監聽機制，攔截所有由瀏覽器發送的 HTTP POST/PUT/PATCH 請求 Payload，並進行兩大核心稽核：
1. **明文密碼檢測**：比對輸入之密碼是否未經前端加密（如直接出現明文，或確認是否使用 `rangpwd` 加密欄位）。
2. **IPv4 位址洩漏檢測**：利用正規表達式自動掃描封包與傳輸內容是否洩漏企業內部私有 IP（如 `10.x.x.x`、`192.168.x.x`）。

## 核心模組
- `scripts/payload_listener.py`: 核心監聽與資安比對引擎（包含 `PayloadAuditor` 類別）。
- `scripts/inspect_login.py`: 獨立執行檢測的命令列程式。

## 產出格式
產出的檢視發現文字嚴格對齊稽核清單格式：
```text
發現IPv4 位址:
10.42.70.37

發現明確的明文密碼:
password = WrongPassword123!
```

## 呼叫範例（整合進既有流程）
```python
from payload_listener import PayloadAuditor

# 1. 建立 Auditor 並綁定 page
auditor = PayloadAuditor(page, input_account="TestUser", input_password="TestPassword123")

# 2. 進行正常瀏覽器操作 (輸入、點擊送出)
page.goto("https://target-url.com/login")
page.fill("input[type='password']", "TestPassword123")
page.click("button[type='submit']")
page.wait_for_timeout(3000)

# 3. 取得符合稽核 Excel 格式的文字
finding_text = auditor.get_audit_findings_text()
```
