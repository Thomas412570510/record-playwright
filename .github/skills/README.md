# Playwright 自動化測試框架

這是一個 Playwright 自動化測試框架。
本專案採用了隔離的架構設計，確保專案根目錄不會被 node_modules 影響。所有的底層測試環境與腳本，皆放置於 .github/skills/ 資料夾內部。

---

## 快速啟動 (Quick Start)

### 1. 環境安裝
在專案根目錄執行以下 Python 腳本，它會自動偵測目錄架構，並建置測試環境：

`ash
python .github/skills/record-playwright/scripts/setup.py
`
*(依據實際架構，路徑可能為 .agent5/.github/skills/...)*

**此安裝腳本將執行：**
- 安裝 VSCode Playwright 擴充套件
- 下載並隔離 Playwright 與 Chromium
- 建立 tests/ 與 test-results/ 資料夾
- 建立 tsconfig.json 以解決路徑解析問題
- 在 package.json 加入相對應的 npm script

---

### 2. 自動錄製與測試
您可以使用以下指令來進行測試腳本的錄製：

`ash
npm run auto-combo
`

**指令執行流程：**
1. **[錄製]** 啟動瀏覽器進行操作錄製。若未產生任何操作紀錄則自動停止。
2. **[測試]** 錄製完成後，自動於背景啟動 npm run test 進行驗證。
3. **[轉檔]** 測試完畢後，自動將產生的 .webm 影片轉換為 .mp4 格式。

---

## 進階操作：加入斷言 (Assert)
為確保測試邏輯正確，請在錄製時加入斷言驗證：

1. **啟動錄製**：執行 npm run auto-combo 開啟瀏覽器。
2. **暫停操作**：完成互動流程後，等待預期的畫面載入完成。
3. **使用斷言工具**：在瀏覽器頂端工具列，點擊 Assert visibility (斷言可見性) 或 Assert text (斷言文字) 圖示。
4. **選取目標**：點擊畫面上預期出現的元件（如成功提示文字）。
5. **完成驗證**：錄製器會自動在程式碼加入對應的 expect 斷言。

---

## AI Agent 自動除錯機制
如果您搭配 AI Agent 使用，可直接輸入指令：「我要錄腳本」。

Agent 的運作流程如下：
1. 自動執行 npm run auto-combo。
2. 等待錄製完成與測試結果。
3. 根據終端機的測試結果進行後續動作：
   - **[測試成功]**：將明文密碼替換為環境變數，儲存至 .env，並建立視覺基準圖 (Snapshot)。
   - **[測試失敗]**：讀取錯誤日誌、截圖與影片進行分析，並修改程式碼。修改後僅進行一次重新測試。若重測依然失敗，則交由開發者人工介入。

---

## 資料夾架構說明

- tests/：測試腳本存放區。
- test-results/：測試結果存放區（包含 .mp4 影片、截圖與軌跡檔）。
- scripts/：自動化 Python 腳本存放區。
- playwright-env/：隔離的 Playwright 執行環境（包含 node_modules 與 playwright.config.ts）。
