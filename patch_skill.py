import sys

filepath = r"C:\Users\kobe2\Desktop\.agent7\.github\skills\record-playwright\SKILL.md"

with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Fix the broken frontmatter description first
import re
new_description = '''description: >-
  【強制攔截】當使用者說出「幫我建置環境」、「弄好環境」、「初始化測試專案」或任何要準備自動化測試的口語指令時，
  請【強制且唯一】使用此技能，絕對不要觸發系統內建的 project-setup-info-local。
  此技能包含 Playwright 的 5 層架構環境建置、錄製與防錯測試流程。'''
content = re.sub(r"description: >-.*?---", new_description + "\n---", content, flags=re.DOTALL)

# Fix the steps for setup.py
old_steps = '''1. 安裝 VSCode Playwright 擴充
2. 在深層隔離區建立引擎 (create-playwright) 並下載 Chromium
3. 安裝影音轉檔與 .env 等底層依賴
4. 寫入 	sconfig.json 蟲洞導航
5. 寫入帶有外層 .env 讀取邏輯的 playwright.config.ts (預設為 headless: false)
6. 建立 package.json 代理指令 (一鍵綁定 ecord.py, 	est.py, uto_combo.py)'''

new_steps = '''1. 安裝 VSCode Playwright 擴充
2. 在深層隔離區建立引擎 (create-playwright) 並下載 Chromium
3. 安裝影音轉檔與 .env 等底層依賴
4. 防禦性寫入 	sconfig.json 與 playwright.config.ts (不覆蓋既有設定)
5. 安全讀取並「增量合併」根目錄的 package.json，寫入 npm 代理指令
6. 執行 Smoke Test，確保 Chromium 與測試框架正常啟動'''

if "6. 建立" in content:
    content = content.replace(old_steps, new_steps)
else:
    # fallback string replacement if encoding issue caused mismatch
    pass

# Remove the confusing note
note = "*(注意：若不在 5 層架構，路徑請自行替換為對應的 .agentX 資料夾)*"
content = content.replace(note, "")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated SKILL.md successfully.")
