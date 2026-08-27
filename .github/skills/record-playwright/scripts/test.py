import os
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_depth_info():
    cwd = os.getcwd()
    if os.path.exists(".github/skills") or os.path.exists("skills"):
        return True, (".github/skills" if os.path.exists(".github/skills") else "skills"), ("../../../../../" if os.path.exists(".github/skills") else "../../../../")
    else:
        agent_dir_name = None
        for d in os.listdir(cwd):
            if os.path.isdir(d) and (os.path.exists(os.path.join(cwd, d, ".github", "skills")) or os.path.exists(os.path.join(cwd, d, "skills"))):
                agent_dir_name = d
                break
        if agent_dir_name:
            return False, (f"{agent_dir_name}/.github/skills" if os.path.exists(f"{agent_dir_name}/.github/skills") else f"{agent_dir_name}/skills"), ("../../../../../../" if os.path.exists(f"{agent_dir_name}/.github/skills") else "../../../../../")
        print("❌ 找不到 skills 或 .github/skills 資料夾！請確保在專案根目錄執行。")
        sys.exit(1)

def main():
    print("🔬 [Playwright] 開始執行自動化測試...")
    is_flat, skills_path, depth_str = get_depth_info()
    cwd = os.getcwd()
    
    env_dir = os.path.join(cwd, skills_path, "record-playwright", "scripts", "playwright-env")
    
    # ====== 實體保險絲 (Physical Lock) 機制 ======
    counter_file = os.path.join(cwd, skills_path, "record-playwright", "scripts", ".retry_count")
    count = 0
    if os.path.exists(counter_file):
        with open(counter_file, 'r') as f:
            try:
                count = int(f.read().strip())
            except:
                count = 0
                
    if count >= 2:
        print("\n🛑 [安全保護機制] AI 一擊必殺失敗（測試已執行 2 次皆失敗），已強制中斷並交還人類決策。")
        sys.exit(1)
        
    # 次數 + 1
    with open(counter_file, 'w') as f:
        f.write(str(count + 1))
    print(f"🔍 目前執行測試次數：{count + 1} / 2")
    # ===============================================

    print("\n🚀 啟動 Playwright 無頭自動化測試...")
    # 解析是否指定了特定的測試檔案
    target_file = ""
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            # 在 Windows 上將反斜線替換為正斜線，避免 Playwright 誤判為正則表達式
            target_file = f" {arg.replace(chr(92), '/')}"
            break

    # 組合 Playwright 指令
    playwright_cmd = f"npx playwright test{target_file}"
    if "--update-snapshots" in sys.argv:
        playwright_cmd += " --update-snapshots"
        print("📸 [視覺回歸模式] 偵測到更新截圖指令，將自動建立/更新基準圖！")
        
    cmd = f'powershell.exe -Command "{playwright_cmd}"'
    print(f"執行指令: {cmd}")
    
    # 注入 NODE_PATH 確保能找到 playwright 模組
    env = os.environ.copy()
    env["NODE_PATH"] = os.path.join(env_dir, "node_modules")
    
    result = subprocess.run(cmd, cwd=env_dir, shell=True, env=env)
    
    if result.returncode == 0:
        print("測試成功。")
        # 綠燈通關，重置計數器
        if os.path.exists(counter_file):
            os.remove(counter_file)
    else:
        print("測試失敗，進入除錯流程。")
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
