import os, re, subprocess
BASE=os.path.expanduser("~/jena-agent")
AGENT=os.path.join(BASE,"agent.py")
YELLOW="\033[93m"; WHITE="\033[97m"; RESET="\033[0m"; BOLD="\033[1m"
def run(c): return subprocess.getoutput(c)
def say(m): print(f"{WHITE}{m}{RESET}")
def jadoo(): say("Main seekh gayi AbuSaif!")
print(f"{WHITE}{BOLD}🤖 Jena v1.0.4 - Colored UI{RESET}")
while True:
    try:
        ui=input(f"{YELLOW}{BOLD}👤 AbuSaif: {RESET}{YELLOW}").strip()
        print(RESET,end="")
    except: break
    if not ui: continue
    if ui.lower() in ["exit","q"]:
        say("🤖 Jena: Allah Hafiz!"); break
    low=ui.lower()
    m=re.match(r'(\w+)\s*(chalao|run|karo)', low)
    if m:
        fname=m.group(1)
        if fname in globals() and callable(globals()[fname]):
            say(f"🤖 Jena: {fname}() chala rahi hun...")
            try: globals()[fname]()
            except Exception as e: say(f"Error: {e}")
            continue
    if "apni file read" in low:
        with open(AGENT,'r',errors='ignore') as f: say(f.read())
        continue
    if "apni file" in low and ("add" in low):
        say("🤖 Jena: Kya add karna hay?")
        code=input(f"{YELLOW}📝 Code: {RESET}{YELLOW}").strip()
        print(RESET,end="")
        if not code: continue
        import importlib.util
        spec=importlib.util.spec_from_file_location("self_editor", f"{BASE}/tools/self_editor.py")
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if mod.safe_edit("append", code):
            say("Restart: python agent.py"); break
        continue
    if "push" in low:
        os.chdir(BASE)
        run("echo '.env' >>.gitignore")
        run("echo '__pycache__/' >>.gitignore")
        run("echo '*.backup-*' >>.gitignore")
        run("git add.gitignore tools/ agent.py")
        say(run('git commit -m "Jena v1.0.4 colored UI - Yellow you White me"'))
        say(run("git push origin master"))
        continue
    say(f"🤖 Jena: Ji AbuSaif? bolo 'jadoo chalao' / 'push kardo'")
