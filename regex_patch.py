import os
import re
import sys

def force_patch_test():
    filepath = r"C:\Users\kobe2\Desktop\.agent7\.github\skills\record-playwright\scripts\test.py"
    
    # Check out original clean file first
    os.system(f"git checkout 8e68261 -- {filepath}")

    with open(filepath, 'rb') as f:
        content = f.read().decode('utf-8-sig')

    # Regex search for get_depth_info function
    match = re.search(r"def get_depth_info\(\):.*?sys\.exit\(1\)", content, flags=re.DOTALL)
    if not match:
        print("Failed to find get_depth_info in test.py via regex")
        sys.exit(1)

    new_func = """def get_depth_info():
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
        sys.exit(1)"""

    content = content.replace(match.group(0), new_func)
    
    # Also inject ExecutionPolicy Bypass
    content = content.replace('powershell.exe -Command', 'powershell.exe -ExecutionPolicy Bypass -Command')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
force_patch_test()
