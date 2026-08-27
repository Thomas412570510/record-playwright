import os
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("🔥 [Auto-Combo] 啟動 無縫連擊 (錄製 -> 驗證 -> 測試 -> 轉檔)...")
    
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    record_py = os.path.join(scripts_dir, "record.py")
    test_py = os.path.join(scripts_dir, "test.py")
    
    # 決定 cwd (找出專案根目錄)
    cwd = os.getcwd()
    basename = os.path.basename(cwd)
    if os.path.exists(".github/skills") or os.path.exists("skills"):
        skills_path = ".github/skills" if os.path.exists(".github/skills") else "skills"
    else:
        agent_dir_name = None
        for d in os.listdir(cwd):
            if os.path.isdir(d) and (os.path.exists(os.path.join(cwd, d, ".github", "skills")) or os.path.exists(os.path.join(cwd, d, "skills"))):
                agent_dir_name = d
                break
        if agent_dir_name:
            skills_path = f"{agent_dir_name}/.github/skills" if os.path.exists(f"{agent_dir_name}/.github/skills") else f"{agent_dir_name}/skills"
        else:
            print("❌ 找不到 skills 或 .github/skills 資料夾！請在專案根目錄執行。")
            sys.exit(1)

    env_dir = os.path.join(cwd, skills_path, "record-playwright", "scripts", "playwright-env")

    # 0. 重置除錯保險絲
    counter_file = os.path.join(cwd, skills_path, "record-playwright", "scripts", ".retry_count")
    if os.path.exists(counter_file):
        os.remove(counter_file)
        print("🔌 已重置實體保險絲 (Retry Counter)")

    # 1. 執行錄製
    print("\n================== [第一階段: 錄製腳本] ==================")
    subprocess.run([sys.executable, record_py], cwd=cwd)
    
    import re
    # 自動找出最新生成的腳本
    tests_dir = os.path.join(cwd, "tests")
    max_num = 0
    for root, _, filenames in os.walk(tests_dir):
        for filename in filenames:
            match = re.match(r"script-(\d+)\.spec\.ts", filename)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
                
    if max_num > 0:
        latest_script = f"tests/script-{max_num}/script-{max_num}.spec.ts"
        print(f"🔍 偵測到最新生成的腳本: {latest_script}")
    else:
        print("\n=========================================================")
        print("🛑 前置驗證失敗：由於沒有產出新腳本 (script-N.spec.ts)，連擊已自動中斷。")
        sys.exit(0)
    
    # 2. 執行測試 (精確打擊：只測試剛錄好的這支檔案！)
    print("\n================== [第二階段: 執行測試] ==================")
    subprocess.run([sys.executable, test_py, latest_script], cwd=cwd)

    # 3. 執行轉檔
    print("\n================== [步驟三: 影音轉檔] ==================")
    convert_cmd = 'powershell.exe -Command "node convert-video.js"'
    subprocess.run(convert_cmd, cwd=env_dir, shell=True)
    
    print("\n=========================================================")
    print("流程執行完畢，請 Agent 確認結果並除錯。")

if __name__ == "__main__":
    main()
