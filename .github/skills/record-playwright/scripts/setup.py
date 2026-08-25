import os
import subprocess
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_cmd(cmd, cwd=None, check=True):
    print(f"執行指令: {cmd}")
    env = os.environ.copy()
    env["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"
    # 不攔截 stdout/stderr，讓下載進度條能印出
    result = subprocess.run(cmd, shell=True, cwd=cwd, env=env)
    if check and result.returncode != 0:
        print(f"❌ 執行失敗: {cmd}")
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
    print("⚠️ 警告: 已自動關閉 TLS 憑證驗證 (NODE_TLS_REJECT_UNAUTHORIZED=0) 以繞過企業防火牆。請留意傳輸安全。\n")
    
    print("================== [環境前置檢查] ==================")
    all_passed = True
    if not check_executable("Node.js", "node -v"): all_passed = False
    if not check_executable("npm", "npm -v"): all_passed = False
    if not check_executable("npx", "npx -v"): all_passed = False
    if not check_executable("VS Code CLI", "code -v"): 
        print("⚠️ 警告: 找不到 'code' 指令。若是免安裝版 VS Code 則可忽略，否則無法自動安裝擴充。")

    if not all_passed:
        print("\n🛑 【嚴重錯誤】缺少基礎執行環境！")
        sys.exit(1)
    print("====================================================\n")

    cwd = os.getcwd()
    
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

    print("\n📦 檢查 VSCode Playwright 擴充...")
    run_cmd("code --install-extension ms-playwright.playwright", check=False)

    env_dir = os.path.join(cwd, skills_path, "record-playwright", "scripts", "playwright-env")
    if not os.path.exists(env_dir):
        os.makedirs(env_dir)
        print(f"📁 建立隔離區: {env_dir}")
    
    print("\n⚙️ 檢查 Playwright 引擎與 Chromium (這可能需要數分鐘)...")
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

    print("\n📝 寫入配置檔與專案結構...")
    config_path = os.path.join(env_dir, "playwright.config.ts")
    if not os.path.exists(config_path):
        config_content = f'''import {{ defineConfig }} from '@playwright/test';
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
'''
        with open(config_path, "w", encoding="utf8") as f:
            f.write(config_content)

    tests_dir = os.path.join(cwd, "tests")
    os.makedirs(tests_dir, exist_ok=True)
    os.makedirs(os.path.join(cwd, "test-results"), exist_ok=True)

    tsconfig_path = os.path.join(tests_dir, "tsconfig.json")
    if not os.path.exists(tsconfig_path):
        tsconfig = {
          "compilerOptions": {
            "baseUrl": ".",
            "paths": {
              "@playwright/test": [f"../{skills_path}/record-playwright/scripts/playwright-env/node_modules/@playwright/test"],
              "@playwright/test/*": [f"../{skills_path}/record-playwright/scripts/playwright-env/node_modules/@playwright/test/*"]
            }
          }
        }
        with open(tsconfig_path, "w", encoding="utf8") as f:
            json.dump(tsconfig, f, indent=2)

    example_path = os.path.join(tests_dir, "example.spec.ts")
    if not os.path.exists(example_path):
        example_test = '''import { test, expect } from '@playwright/test';
test('example smoke test', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toHaveTitle(/Example/);
});
'''
        with open(example_path, "w", encoding="utf8") as f:
            f.write(example_test)

    env_path = os.path.join(cwd, ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf8") as f:
            f.write("# Playwright Environment Variables\nPLAYWRIGHT_BASE_URL=https://example.com\n")

    vscode_dir = os.path.join(cwd, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)
    settings_path = os.path.join(vscode_dir, "settings.json")
    if not os.path.exists(settings_path):
        vscode_settings = {
            "playwright.configPath": f"{skills_path}/record-playwright/scripts/playwright-env/playwright.config.ts"
        }
        with open(settings_path, "w", encoding="utf8") as f:
            json.dump(vscode_settings, f, indent=2)

    print("\n📦 安全合併外層 package.json...")
    cd_path = f"{skills_path}/record-playwright/scripts/playwright-env"
    pkg_path = os.path.join(cwd, "package.json")
    
    if os.path.exists(pkg_path):
        with open(pkg_path, "r", encoding="utf8") as f:
            try:
                pkg = json.load(f)
            except:
                pkg = {}
    else:
        pkg = {"name": "playwright-enterprise-wrapper", "private": True}
        
    if "scripts" not in pkg:
        pkg["scripts"] = {}
        
    pkg["scripts"]["codegen"] = f"python {skills_path}/record-playwright/scripts/record.py"
    pkg["scripts"]["test"] = f"python {skills_path}/record-playwright/scripts/test.py"
    pkg["scripts"]["convert-video"] = f"cd {cd_path} && node convert-video.js"
    pkg["scripts"]["auto-combo"] = f"python {skills_path}/record-playwright/scripts/auto_combo.py"

    with open(pkg_path, "w", encoding="utf8") as f:
        json.dump(pkg, f, indent=2)

    print("\n🧪 執行自動化 Smoke Test 驗證引擎是否正常啟動...")
    smoke_cmd = [sys.executable, f"{skills_path}/record-playwright/scripts/test.py", "tests/example.spec.ts"]
    smoke_result = subprocess.run(smoke_cmd, cwd=cwd)
    if smoke_result.returncode == 0:
        print("\n✅ 環境建置全部完成！您可以開始使用 
pm run auto-combo 進行無痕錄製了！")
    else:
        print("\n⚠️ 環境建置完成，但 Smoke Test 執行失敗。請檢查上方日誌。")

if __name__ == "__main__":
    main()
