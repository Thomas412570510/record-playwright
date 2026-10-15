# 🎬 Record Playwright & Agent Automation Skills Suite

[![Playwright](https://img.shields.io/badge/Playwright-Automation-45ba4b?logo=playwright&logoColor=white)](https://playwright.dev/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> 一套專為 **AI Coding Agent (如 Antigravity / Claude Code / Copilot Workspace)** 與測試工程師量身打造的 Playwright 技能套件（Agent Skills），提供端到端測試錄製、環境隔離、自動去敏化、資安弱點掃描與網路封包監聽。

---

## 🌟 核心模組 (Skills Modules)

本專案將複雜的 Playwright 測試與稽核流程模組化為三個專門的 Agent Skills：

| 模組名稱 | 位置 | 核心能力 |
| :--- | :--- | :--- |
| **`record-playwright`** | `.github/skills/record-playwright/` | • 零配置環境隔離建置 (`setup.py`)<br>• 一鍵互動錄製與測試 (`npm run auto-combo`)<br>• 錄製腳本自動敏感資訊去敏化 (替換為 `process.env`)<br>• 影片即時轉檔 (`.webm` ➔ `.mp4`) |
| **`audit-playwright`** | `.github/skills/audit-playwright/` | • 自動化 Web 弱點檢測與安全性測試 (`security_tester.py`)<br>• 測試資料擷取 (`data_extractor.py`)<br>• HTML 稽核報告產出 (`report_generator.py`) |
| **`payload-inspector`** | `.github/skills/payload-inspector/` | • 網路流量封包監聽 (`payload_listener.py`)<br>• 登入 Payload 封包擷取與驗證 (`inspect_login.py`) |

---

## 🏗️ 目錄架構 (Project Architecture)

```text
record-playwright/
├── .github/
│   └── skills/
│       ├── record-playwright/       # 錄製與轉檔工作流
│       │   ├── scripts/
│       │   │   ├── auto_combo.py    # 錄製 + 測試 + 轉檔一鍵組合拳
│       │   │   ├── record.py        # Playwright Codegen 與密碼去敏化
│       │   │   ├── test.py          # 測試執行調度
│       │   │   ├── convert-video.js # FFmpeg 影片轉檔
│       │   │   └── setup.py         # 隔離環境快速建置
│       │   ├── SKILL.md             # Agent 呼叫技能規格書
│       │   └── README.md
│       ├── audit-playwright/        # 資安與合規稽核模組
│       │   ├── scripts/
│       │   └── SKILL.md
│       ├── payload-inspector/       # 封包分析與登入偵測模組
│       │   ├── scripts/
│       │   └── SKILL.md
│       └── README.md                # 技能總覽說明
├── true_patch.py                    # 跨層級目錄路徑適配修補工具
├── .gitignore
└── README.md                        # 專案總說明文件
```

---

## 🚀 快速上手 (Quick Start)

### 1. 環境初始化 (One-Click Setup)

執行環境建置腳本，自動偵測工作目錄層級，並於 `.github/skills/record-playwright/scripts/playwright-env/` 建置完全隔離的 Node/Playwright 執行環境，**絕不污染專案根目錄**：

```bash
python .github/skills/record-playwright/scripts/setup.py
```

### 2. 一鍵錄製、測試與轉檔 (Auto-Combo)

```bash
npm run auto-combo
```

- **Step 1 [錄製]**：彈出瀏覽器視窗供人工操作，操作時自動擷取 DOM 與事件。
- **Step 2 [防呆與去敏]**：產出之 TypeScript 測試腳本自動將表單中的真實帳號密碼替換為 `process.env.TEST_ACCOUNT` 與 `process.env.TEST_PASSWORD`。
- **Step 3 [回歸測試]**：錄製完成後於背景以無頭模式執行該測試以確保穩定性。
- **Step 4 [影片轉檔]**：將瀏覽器錄製的 `.webm` 自動轉換為全平台通用的 `.mp4` 存入 `test-results/`。

---

## 🤖 搭配 AI Agent 使用模式

當整合至 Antigravity、Gemini CLI 或 Claude 代理時，Agent 可直接讀取各 Skill 的 `SKILL.md`：
- **使用者輸入**：「幫我錄製登入流程並驗證成功畫面」
- **Agent 行為**：
  1. 呼叫 `record-playwright` 啟動自動錄製。
  2. 檢查測試結果與錯誤截圖。
  3. 若有例外，自動調度 `payload-inspector` 擷取 API 錯誤回應進行分析修正。

---

## 🛡️ 安全設計 (Security & Privacy)

1. **自動脫敏**：`record.py` 內建正則替換機制，防止錄製時敲入之機密密碼明文存入測試代碼。
2. **環境隔離**：所有 `node_modules` 與依賴項均限制於 sandbox 目錄中，專案根目錄保持輕量乾淨。
3. **版本控管過濾**：`.gitignore` 預設排除所有憑證檔案 (`.env`)、日誌與快取資料。

---

## 📄 授權條款 (License)

本專案採用 [MIT License](LICENSE) 授權。
