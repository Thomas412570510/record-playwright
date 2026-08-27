import os

def fix_encoding(filepath):
    try:
        # Try reading as utf-8
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            # Try reading as big5
            with open(filepath, 'r', encoding='big5') as f:
                content = f.read()
        except:
            return
            
    # Write back as pure utf-8
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

base = r"C:\Users\kobe2\Desktop\.agent7\.github\skills\record-playwright\scripts"
for f in ["record.py", "test.py", "auto_combo.py", "setup.py"]:
    fix_encoding(os.path.join(base, f))
