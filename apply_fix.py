import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # For record.py and test.py
    old_func = re.search(r"def get_depth_info\(\):.*?sys\.exit\(1\)", content, flags=re.DOTALL)
    if old_func:
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
        content = content.replace(old_func.group(0), new_func)

    # For auto_combo.py
    old_combo = re.search(r"if basename\.startswith\('\.agent'\):.*?sys\.exit\(1\)", content, flags=re.DOTALL)
    if old_combo:
        new_combo = """if os.path.exists(".github/skills") or os.path.exists("skills"):
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
        content = content.replace(old_combo.group(0), new_combo)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

base = r"C:\Users\kobe2\Desktop\.agent7\.github\skills\record-playwright\scripts"
fix_file(os.path.join(base, "test.py"))
fix_file(os.path.join(base, "record.py"))
fix_file(os.path.join(base, "auto_combo.py"))
