import os
import subprocess
import json
import shutil
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=None, check=True):
    print(f"執行指令: {cmd}")
    env = os.environ.copy()
    env["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"
    result = subprocess.run(cmd, shell=True, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode != 0:
        print(f"❌ 執行失敗: {cmd}\n錯誤訊息: {result.stderr.decode('utf-8', errors='ignore')}")
        sys.exit(1)
    return result

def check_executable(name, cmd):
    print(f"🔍 檢查環境依賴: {name} ...", end=" ")
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            version = result.stdout.decode('utf-8', errors='ignore').strip().split('\n')[0]
            print(f"✅ 已安裝 ({version})")
            return True
        else:
            print(f"❌ 未安裝或不在 PATH 中")
            return False
    except Exception:
        print(f"❌ 未安裝或不在 PATH 中")
        return False

def main():
    print("🚀 啟動 Playwright 企業級環境自動安裝程序...\n")
    
    # 0. 系統環境前置檢查
    print("================== [環境前置檢查] ==================")
    all_passed = True
    if not check_executable("Node.js", "node -v"): all_passed = False
    if not check_executable("npm", "npm -v"): all_passed = False
    if not check_executable("npx", "npx -v"): all_passed = False
    if not check_executable("VS Code CLI", "code -v"): 
        print("⚠️ 警告: 找不到 'code' 指令。若是免安裝版 VS Code 則可忽略，否則無法自動安裝擴充。")
        # 允許沒有 code cli，只是警告

    if not all_passed:
        print("\n🛑 【嚴重錯誤】缺少基礎執行環境！")
        print("為確保系統能正常運作，請手動下載並安裝以下大型依賴：")
        print("👉 Node.js (含 npm/npx): https://nodejs.org/")
        print("👉 VS Code: https://code.visualstudio.com/")
        print("安裝完畢後，請務必【重新啟動終端機】以載入 PATH，再重新執行本腳本。")
        sys.exit(1)
    print("====================================================\n")

    # 判斷架構層級 (4層或5層)
    cwd = os.getcwd()
    basename = os.path.basename(cwd)
    
    if os.path.exists(".github/skills") or os.path.exists("skills"):
        print("📍 偵測到扁平化架構 (4層): 目前根目錄下包含 skills")
        is_flat = True
        agent_dir_name = ""
        skills_path = ".github/skills" if os.path.exists(".github/skills") else "skills"
        depth_str = "../../../../../" if os.path.exists(".github/skills") else "../../../../"
    else:
        agent_dir_name = None
        for d in os.listdir(cwd):
            if os.path.isdir(d) and (os.path.exists(os.path.join(cwd, d, ".github", "skills")) or os.path.exists(os.path.join(cwd, d, "skills"))):
                agent_dir_name = d
                break
        
        if agent_dir_name:
            print(f"📍 偵測到標準架構 (5層): 找到隱藏資料夾 {agent_dir_name}")
            is_flat = False
            skills_path = f"{agent_dir_name}/.github/skills" if os.path.exists(f"{agent_dir_name}/.github/skills") else f"{agent_dir_name}/skills"
            depth_str = "../../../../../../" if os.path.exists(f"{agent_dir_name}/.github/skills") else "../../../../../"
        else:
            print("❌ 找不到 skills 或 .github/skills 資料夾！請確保您在正確的專案根目錄執行此腳本。")
            sys.exit(1)

    # 1. 安裝 VSCode 擴充
    print("\n📦 檢查 VSCode Playwright 擴充...")
    run_cmd("code --install-extension ms-playwright.playwright", check=False)

    # 2. 建立黑洞引擎區
    env_dir = os.path.join(cwd, skills_path, "record-playwright", "scripts", "playwright-env")
    if not os.path.exists(env_dir):
        os.makedirs(env_dir)
        print(f"📁 建立隔離區: {env_dir}")
    
    print("\n⚙️ 檢查 Playwright 引擎與 Chromium...")
    if not os.path.exists(os.path.join(env_dir, "package.json")):
        run_cmd("npx -y create-playwright@latest . --quiet --browser=chromium --lang=TypeScript", cwd=env_dir)
        run_cmd("npx playwright install chromium", cwd=env_dir)
    else:
        print("✅ Playwright 專案已初始化。")
    
    print("\n📦 檢查影音轉檔與環境依賴...")
    deps = ["ffmpeg-static", "fluent-ffmpeg", "dotenv"]
    need_install = False
    for dep in deps:
        if not os.path.exists(os.path.join(env_dir, "node_modules", dep)):
            need_install = True
            break
            
    if need_install:
        run_cmd("npm install ffmpeg-static fluent-ffmpeg dotenv", cwd=env_dir)
    else:
        print("✅ 所有 NPM 依賴皆已安裝完畢。")

    # 3. 寫入黑洞配置檔
    print("\n📝 寫入 playwright.config.ts...")
    config_content = f"""import {{ defineConfig }} from '@playwright/test';
import {{ readFileSync }} from 'node:fs';
import {{ resolve }} from 'node:path';

try {{
  for (const line of readFileSync(resolve(__dirname, '{depth_str}.env'), 'utf8').split(/\\r?\\n/)) {{
    const separator = line.indexOf('=');
    if (separator > 0 && !line.startsWith('#')) {{
      process.env[line.slice(0, separator)] ??= line.slice(separator + 1);
    }}
  }}
}} catch(e) {{}}

export default defineConfig({{
  testDir: '{depth_str}tests',
  outputDir: '{depth_str}test-results',
  use: {{
    video: 'on',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    headless: false
  }}
}});
"""
    with open(os.path.join(env_dir, "playwright.config.ts"), "w", encoding="utf8") as f:
        f.write(config_content)

    # 4. 生成外層結構
    print("\n📁 建立專案測試資料夾...")
    tests_dir = os.path.join(cwd, "tests")
    os.makedirs(tests_dir, exist_ok=True)
    os.makedirs(os.path.join(cwd, "test-results"), exist_ok=True)

    # 蟲洞導航 tsconfig.json
    tsconfig = {
      "compilerOptions": {
        "baseUrl": ".",
        "paths": {
          "@playwright/test": [f"../{skills_path}/record-playwright/scripts/playwright-env/node_modules/@playwright/test"],
          "@playwright/test/*": [f"../{skills_path}/record-playwright/scripts/playwright-env/node_modules/@playwright/test/*"]
        }
      }
    }
    with open(os.path.join(tests_dir, "tsconfig.json"), "w", encoding="utf8") as f:
        json.dump(tsconfig, f, indent=2)

    # 寫入 example 測試
    example_test = """import { test, expect } from '@playwright/test';
test('example smoke test', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toHaveTitle(/Example/);
});
"""
    with open(os.path.join(tests_dir, "example.spec.ts"), "w", encoding="utf8") as f:
        f.write(example_test)

    # 生成 .env
    env_path = os.path.join(cwd, ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf8") as f:
            f.write("# Playwright Environment Variables\nPLAYWRIGHT_BASE_URL=https://example.com\n")

    # VSCode Settings
    vscode_dir = os.path.join(cwd, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)
    vscode_settings = {
        "playwright.configPath": f"{skills_path}/record-playwright/scripts/playwright-env/playwright.config.ts"
    }
    with open(os.path.join(vscode_dir, "settings.json"), "w", encoding="utf8") as f:
        json.dump(vscode_settings, f, indent=2)

    # 寫入 package.json 代理
    cd_path = f"{skills_path}/record-playwright/scripts/playwright-env"
    pkg = {
      "name": "playwright-enterprise-wrapper",
      "private": True,
      "scripts": {
        "codegen": f"python {skills_path}/record-playwright/scripts/record.py",
        "test": f"python {skills_path}/record-playwright/scripts/test.py",
        "convert-video": f"cd {cd_path} && node convert-video.js",
        "auto-combo": f"python {skills_path}/record-playwright/scripts/auto_combo.py"
      }
    }
    with open(os.path.join(cwd, "package.json"), "w", encoding="utf8") as f:
        json.dump(pkg, f, indent=2)

    print("\n✅ 環境建置全部完成！您可以開始使用 `npm run auto-combo` 進行無痕錄製了！")

if __name__ == "__main__":
    main()
