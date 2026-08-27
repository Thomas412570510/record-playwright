import os
import re
import subprocess
import sys
import time

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

def sanitize_credentials(output_file):
    with open(output_file, "r", encoding="utf-8") as file:
        source = file.read()

    replacements = {
        r"(await page\.getByRole\('textbox', \{ name: '帳號 \( 非 email \)' \}\)\.fill\()['\"].*?['\"](\);)": r"\1process.env.TEST_ACCOUNT ?? ''\2",
        r"(await page\.getByRole\('textbox', \{ name: '密碼' \}\)\.fill\()['\"].*?['\"](\);)": r"\1process.env.TEST_PASSWORD ?? ''\2",
    }
    for pattern, replacement in replacements.items():
        source = re.sub(pattern, replacement, source)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(source)

def main():
    print("準備啟動 Playwright Codegen...")
    is_flat, skills_path, depth_str = get_depth_info()
    
    env_dir = os.path.join(os.getcwd(), skills_path, "record-playwright", "scripts", "playwright-env")
    tests_dir = os.path.join(os.getcwd(), "tests")
    os.makedirs(tests_dir, exist_ok=True)
    
    max_num = 0
    import re
    for root, _, filenames in os.walk(tests_dir):
        for filename in filenames:
            match = re.match(r"script-(\d+)\.spec\.ts", filename)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
                
    next_num = max_num + 1
    output_filename = f"script-{next_num}.spec.ts"
    script_dir = os.path.join(tests_dir, f"script-{next_num}")
    output_file = os.path.join(script_dir, output_filename)
    os.makedirs(script_dir, exist_ok=True)
    
    print(f"將錄製儲存為: script-{next_num}/{output_filename}")

    cmd = f'powershell.exe -Command "npx playwright codegen -o {depth_str}tests/script-{next_num}/{output_filename}"'
    print(f"執行指令: {cmd}")
    
    try:
        # 阻塞等待使用者操作瀏覽器並關閉
        subprocess.run(cmd, cwd=env_dir, shell=True, check=True)
    except subprocess.CalledProcessError:
        print("錄製過程異常中斷。")
    
    # 驗證是否有產出內容
    if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
        print("錄製已取消或未產出任何操作腳本，自動終止，不進行測試。")
        sys.exit(0)

    sanitize_credentials(output_file)
    print(f"錄製完成！腳本已成功寫入: {output_file}")

if __name__ == "__main__":
    main()
