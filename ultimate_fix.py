import os
import re

def fix():
    os.system("git checkout 8e68261 -- .github/skills/record-playwright/scripts/record.py")
    os.system("git checkout 8e68261 -- .github/skills/record-playwright/scripts/test.py")
    os.system("git checkout 8e68261 -- .github/skills/record-playwright/scripts/auto_combo.py")

    def patch(filepath, is_combo=False):
        with open(filepath, 'rb') as f:
            content = f.read().decode('utf-8-sig').replace('\r\n', '\n')

        old_str = """def get_depth_info():
    cwd = os.getcwd()
    basename = os.path.basename(cwd)
    if basename.startswith('.agent'):
        return True, (".github/skills" if os.path.exists(".github/skills") else "skills"), ("../../../../../" if os.path.exists(".github/skills") else "../../../../")
    elif any(d.startswith('.agent') for d in os.listdir(cwd) if os.path.isdir(d)):
        agent_dir_name = next(d for d in os.listdir(cwd) if d.startswith('.agent'))
        return False, (f"{agent_dir_name}/.github/skills" if os.path.exists(f"{agent_dir_name}/.github/skills") else f"{agent_dir_name}/skills"), ("../../../../../../" if os.path.exists(f"{agent_dir_name}/.github/skills") else "../../../../../")
    else:
        print("錯誤：找不到 .agent 資料夾。請在專案根目錄執行。")
        sys.exit(1)"""

        new_str = """def get_depth_info():
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

        old_combo = """    if basename.startswith('.agent'):
        skills_path = ".github/skills" if os.path.exists(".github/skills") else "skills"
    elif any(d.startswith('.agent') for d in os.listdir(cwd) if os.path.isdir(d)):
        agent_dir_name = next(d for d in os.listdir(cwd) if d.startswith('.agent'))
        skills_path = f"{agent_dir_name}/.github/skills" if os.path.exists(f"{agent_dir_name}/.github/skills") else f"{agent_dir_name}/skills"
    else:
        print("錯誤：找不到 .agent 資料夾。請在專案根目錄執行。")
        sys.exit(1)"""
        
        new_combo = """    if os.path.exists(".github/skills") or os.path.exists("skills"):
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
            print("❌ 找不到 skills 或 .github/skills 資料夾！請確保在專案根目錄執行。")
            sys.exit(1)"""

        if not is_combo:
            content = content.replace(old_str, new_str)
        else:
            content = content.replace(old_combo, new_combo)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    base = r"C:\Users\kobe2\Desktop\.agent7\.github\skills\record-playwright\scripts"
    patch(os.path.join(base, "record.py"))
    patch(os.path.join(base, "test.py"))
    patch(os.path.join(base, "auto_combo.py"), is_combo=True)

fix()
