import os

def patch_powershell(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Replace 'powershell.exe -Command' with 'powershell.exe -ExecutionPolicy Bypass -Command'
    new_content = content.replace('powershell.exe -Command', 'powershell.exe -ExecutionPolicy Bypass -Command')

    if content != new_content:
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
        print(f"Patched powershell command in {os.path.basename(filepath)}")

base = r"C:\Users\kobe2\Desktop\.agent7\.github\skills\record-playwright\scripts"
patch_powershell(os.path.join(base, "record.py"))
patch_powershell(os.path.join(base, "test.py"))
patch_powershell(os.path.join(base, "auto_combo.py"))
