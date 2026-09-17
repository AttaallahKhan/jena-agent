import os, shutil, ast, datetime, difflib

BASE = os.path.expanduser("~/jena-agent")
AGENT = os.path.join(BASE, "agent.py")

def backup():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bk = f"{AGENT}.backup-{ts}"
    shutil.copy(AGENT, bk)
    print(f"📦 Backup: {bk}")
    return bk

def check_syntax(code):
    try:
        ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"

def show_diff(old, new):
    diff = difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm='', n=3)
    print("\n--- DIFF ---")
    for line in diff:
        print(line)
    print("--- END DIFF ---\n")

def safe_edit(mode, content, target_func=None):
    with open(AGENT,'r',encoding='utf-8',errors='ignore') as f:
        old = f.read()

    bk = backup()

    if mode == "append":
        marker = "\nif __name__ == \"__main__\":"
        addition = f"\n\n# [Jena self-edit {datetime.datetime.now()}]\n{content}\n"
        if marker in old:
            new = old.replace(marker, addition + marker, 1)
        else:
            new = old + addition
    elif mode == "replace_func" and target_func:
        # simple: function ko dhoond ke replace karo
        import re
        pattern = rf"def {target_func}\(.*?\):.*?(?=\n def |\nclass |\Z)"
        # agar complex lage to append hi karo
        new = old + f"\n\n# Replaced {target_func}\n{content}\n"
    else:
        new = content  # full rewrite (dangerous but allowed)

    show_diff(old, new)

    ok, msg = check_syntax(new)
    if not ok:
        print(f"❌ Syntax fail: {msg}")
        print("↩️ Rollback...")
        shutil.copy(bk, AGENT)
        return False

    # confirm from user
    ans = input("✅ Syntax OK. Apply karun? (y/n): ").lower()
    if ans != 'y':
        print("Cancelled, rollback")
        shutil.copy(bk, AGENT)
        return False

    with open(AGENT,'w',encoding='utf-8') as f:
        f.write(new)
    print("✅ Edit applied! Restart agent.py")
    return True

if __name__ == "__main__":
    import sys
    print("Usage: python tools/self_editor.py append 'print(\"hi\")'")
